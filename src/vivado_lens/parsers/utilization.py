"""Parse Vivado utilization.rpt into Utilization model."""

from __future__ import annotations

import re

from vivado_lens.models.synth import ResourceUsage, Utilization

_RESOURCE_RE = re.compile(
    r"\|\s*([A-Za-z0-9/ ]+?)\s*\*?\s*\|\s*(\d+)\s*\|\s*\d+\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|"
)

_SLICE_LOGIC_NAMES = {
    "Slice LUTs", "LUT as Logic", "LUT as Memory",
    "Slice Registers", "Register as Flip Flop", "Register as Latch",
    "F7 Muxes", "F8 Muxes", "Slice", "LUT Flip Flop Pairs",
}
_MEMORY_NAMES = {"Block RAM Tile", "RAMB36/FIFO", "RAMB18"}
_DSP_NAMES = {"DSPs"}
_IO_NAMES = {"Bonded IOB", "Bonded IPADs", "Bonded OPADs"}


def parse_utilization_report(content: str) -> Utilization:
    """Parse utilization.rpt text into a Utilization model."""
    parsed: dict[str, tuple[int, int, float]] = {}
    for m in _RESOURCE_RE.finditer(content):
        name = m.group(1).strip()
        if name not in parsed:
            parsed[name] = (int(m.group(2)), int(m.group(3)), float(m.group(4)))

    slice_logic: list[ResourceUsage] = []
    memory: list[ResourceUsage] = []
    dsp: list[ResourceUsage] = []
    io: list[ResourceUsage] = []

    for name, (used, available, pct) in parsed.items():
        resource = ResourceUsage(
            name=name, used=used, available=available, utilization_pct=pct
        )
        if name in _SLICE_LOGIC_NAMES:
            slice_logic.append(resource)
        elif name in _MEMORY_NAMES:
            memory.append(resource)
        elif name in _DSP_NAMES:
            dsp.append(resource)
        elif name in _IO_NAMES:
            io.append(resource)
        else:
            slice_logic.append(resource)

    return Utilization(
        slice_logic=slice_logic, memory=memory, dsp=dsp, io=io
    )
