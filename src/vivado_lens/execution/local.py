"""Local executor: runs Vivado tools via subprocess on Windows."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable, Optional

from vivado_lens.config import VivadoConfig
from vivado_lens.execution.base import ExecutorBase, RunResult
from vivado_lens.execution.process import run_vivado_batch, run_tool


class LocalExecutor(ExecutorBase):
    """Execute Vivado commands locally via subprocess."""

    def __init__(self, config: VivadoConfig):
        self.config = config

    def run_batch(
        self,
        tcl_path: Path,
        cwd: Path,
        log_path: Path,
        timeout: int = 1200,
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> RunResult:
        vivado = self.config.vivado
        cmd = (
            f'"{vivado}" -mode batch -source "{tcl_path}" '
            f'-log "{log_path}" -journal "{log_path.with_suffix(".jou")}"'
        )
        progress_file = cwd / "progress.json"

        rc, output, elapsed, errors, warnings = run_vivado_batch(
            cmd=cmd,
            cwd=cwd,
            timeout=timeout,
            progress_file=progress_file,
            on_progress=on_progress,
        )
        return RunResult(
            returncode=rc,
            output=output,
            elapsed_s=elapsed,
            errors=errors,
            warnings=warnings,
        )

    def run_tool(self, cmd: list[str], cwd: Path, timeout: int = 600) -> RunResult:
        import time

        cmd_str = cmd[0] if len(cmd) == 1 else " ".join(cmd)
        start = time.time()
        rc, output = run_tool(cmd_str, cwd, timeout)
        elapsed = time.time() - start
        return RunResult(returncode=rc, output=output, elapsed_s=elapsed)

    def kill_processes(self, names: list[str]) -> None:
        for name in names:
            subprocess.run(
                f"taskkill /F /IM {name} 2>nul",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
