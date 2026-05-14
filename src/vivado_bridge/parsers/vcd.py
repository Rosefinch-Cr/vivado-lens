"""Parse VCD (Value Change Dump) files into WaveformData model."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from vivado_bridge.models.sim import SignalTrace, WaveformData


def parse_vcd(vcd_path: str | Path, signal_filter: Optional[list[str]] = None) -> WaveformData:
    """Parse a VCD file into structured waveform data."""
    signals: dict[str, list[tuple[int, int]]] = {}
    id_to_name: dict[str, str] = {}
    timescale = "1ns"
    current_time = 0
    max_time = 0

    with open(vcd_path, "r", errors="replace") as f:
        scope_stack: list[str] = []
        for line in f:
            line = line.strip()
            if line.startswith("$timescale"):
                ts = line.replace("$timescale", "").replace("$end", "").strip()
                if ts:
                    timescale = ts
            elif line.startswith("$scope"):
                parts = line.split()
                if len(parts) >= 3:
                    scope_stack.append(parts[2])
            elif line.startswith("$upscope"):
                if scope_stack:
                    scope_stack.pop()
            elif line.startswith("$var"):
                parts = line.split()
                if len(parts) >= 5:
                    var_id = parts[3]
                    var_name = parts[4]
                    full_name = ".".join(scope_stack + [var_name])
                    id_to_name[var_id] = full_name
                    if signal_filter is None or any(s in full_name for s in signal_filter):
                        signals[full_name] = []
            elif line.startswith("#"):
                try:
                    current_time = int(line[1:])
                    max_time = max(max_time, current_time)
                except ValueError:
                    pass
            elif len(line) >= 2 and line[0] in "01xzXZ":
                val = line[0]
                var_id = line[1:]
                name = id_to_name.get(var_id)
                if name and name in signals:
                    signals[name].append((current_time, 1 if val == "1" else 0))
            elif line.startswith("b"):
                parts = line.split()
                if len(parts) == 2:
                    val_str = parts[0][1:]
                    var_id = parts[1]
                    name = id_to_name.get(var_id)
                    if name and name in signals:
                        try:
                            signals[name].append((current_time, int(val_str, 2)))
                        except ValueError:
                            signals[name].append((current_time, 0))

    traces = [
        SignalTrace(name=name, transitions=transitions)
        for name, transitions in signals.items()
        if transitions
    ]

    return WaveformData(timescale=timescale, signals=traces, duration=max_time)
