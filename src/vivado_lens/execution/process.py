"""Vivado process runner with streaming output and progress tracking."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional

from vivado_lens.models.progress import ProgressUpdate

_PHASE_RE = re.compile(r"(Phase \d+|Starting|Finished|WARNING|ERROR|CRITICAL)", re.IGNORECASE)


def run_vivado_batch(
    cmd: str,
    cwd: Path,
    timeout: int = 1200,
    progress_file: Optional[Path] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> tuple[int, str, float, list[str], list[str]]:
    """Run a Vivado command with streaming output and progress tracking.

    Returns: (returncode, full_output, elapsed_s, errors, warnings)
    """
    proc = subprocess.Popen(
        cmd, shell=True, cwd=str(cwd),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
    )

    output_lines: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []
    start = time.time()

    def _write_progress(phase: str, done: bool = False, success: bool = True) -> None:
        if not progress_file:
            return
        update = ProgressUpdate(
            elapsed_s=round(time.time() - start, 1),
            phase=phase,
            errors=len(errors),
            warnings=len(warnings),
            done=done,
            success=success,
        )
        try:
            progress_file.write_text(update.model_dump_json())
        except OSError:
            pass

    _write_progress("Starting...")

    try:
        for line in proc.stdout:
            output_lines.append(line)
            stripped = line.strip()

            if stripped.startswith("ERROR:") or "] ERROR:" in line:
                errors.append(stripped)
            if stripped.startswith("WARNING:") or "] WARNING:" in line or "CRITICAL WARNING:" in line:
                warnings.append(stripped)

            if _PHASE_RE.search(line):
                phase_text = stripped[:60]
                _write_progress(phase_text)
                if on_progress:
                    on_progress(phase_text)

            if time.time() - start > timeout:
                proc.kill()
                _write_progress("TIMEOUT", done=True, success=False)
                return -1, "".join(output_lines), time.time() - start, errors, warnings
    except Exception:
        pass

    proc.wait()
    elapsed = time.time() - start
    success = proc.returncode == 0
    _write_progress("Done" if success else "FAILED", done=True, success=success)

    return proc.returncode, "".join(output_lines), elapsed, errors, warnings


def run_tool(cmd: list[str], cwd: Path, timeout: int = 600) -> tuple[int, str]:
    """Run a Vivado sub-tool (xvlog, xelab, xsim) and capture output."""
    result = subprocess.run(
        cmd, shell=True, cwd=str(cwd),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, timeout=timeout,
    )
    return result.returncode, result.stdout
