"""Parse Vivado power.rpt into PowerReport model."""

from __future__ import annotations

import re

from vivado_lens.models.impl import PowerComponent, PowerReport

_COMP_RE = re.compile(
    r"\|\s*(Clocks|Slice Logic|Signals|Block RAM|DSPs|I/O|PS7)\s*\|\s*([\d.<]+)\s*\|"
)


def parse_power_report(content: str) -> PowerReport:
    """Parse power.rpt text into a PowerReport model."""
    total_w = _extract_float(r"Total On-Chip Power \(W\)\s*\|\s*([\d.]+)", content)
    dynamic_w = _extract_float(r"\| Dynamic \(W\)\s*\|\s*([\d.]+)", content)
    static_w = _extract_float(r"Device Static \(W\)\s*\|\s*([\d.]+)", content)
    junction_temp = _extract_float(r"Junction Temperature \(C\)\s*\|\s*([\d.]+)", content)

    confidence = ""
    m = re.search(r"Confidence Level\s*\|\s*(\w+)", content)
    if m:
        confidence = m.group(1)

    components: list[PowerComponent] = []
    for m in _COMP_RE.finditer(content):
        name = m.group(1).strip()
        val_str = m.group(2).strip()
        watts = 0.001 if val_str.startswith("<") else float(val_str)
        pct = (watts / dynamic_w * 100) if dynamic_w > 0 else 0.0
        components.append(
            PowerComponent(name=name, watts=watts, pct_of_dynamic=round(pct, 1))
        )

    return PowerReport(
        total_w=total_w,
        dynamic_w=dynamic_w,
        static_w=static_w,
        junction_temp_c=junction_temp,
        confidence=confidence,
        components=components,
    )


def _extract_float(pattern: str, content: str) -> float:
    m = re.search(pattern, content)
    return float(m.group(1)) if m else 0.0
