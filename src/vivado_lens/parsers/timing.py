"""Parse Vivado timing_summary.rpt into TimingSummary model."""

from __future__ import annotations

import re
from typing import Optional

from vivado_lens.models.synth import (
    ClockInfo,
    CriticalPath,
    SlackInfo,
    TimingSummary,
)


def parse_timing_report(content: str) -> TimingSummary:
    """Parse timing_summary.rpt text into a TimingSummary model."""
    clocks = _parse_clocks(content)
    slack = _parse_slack(content)
    critical_path = _parse_critical_path(content)
    return TimingSummary(clocks=clocks, slack=slack, critical_path=critical_path)


def _parse_clocks(content: str) -> list[ClockInfo]:
    clocks: list[ClockInfo] = []
    for m in re.finditer(
        r"^(\w+)\s+\{[\d.]+ [\d.]+\}\s+([\d.]+)\s+([\d.]+)", content, re.MULTILINE
    ):
        clocks.append(
            ClockInfo(
                name=m.group(1),
                period_ns=float(m.group(2)),
                frequency_mhz=float(m.group(3)),
            )
        )
    return clocks


def _parse_slack(content: str) -> Optional[SlackInfo]:
    setup_ns, hold_ns, pw_ns = 0.0, 0.0, 0.0
    setup_fail, hold_fail, pw_fail = 0, 0, 0

    m = re.search(r"Setup\s*:\s*(\d+)\s*Failing.*?Worst Slack\s*([\-\d.]+)ns", content)
    if m:
        setup_fail, setup_ns = int(m.group(1)), float(m.group(2))

    m = re.search(r"Hold\s*:\s*(\d+)\s*Failing.*?Worst Slack\s*([\-\d.]+)ns", content)
    if m:
        hold_fail, hold_ns = int(m.group(1)), float(m.group(2))

    m = re.search(r"PW\s*:\s*(\d+)\s*Failing.*?Worst Slack\s*([\-\d.]+)ns", content)
    if m:
        pw_fail, pw_ns = int(m.group(1)), float(m.group(2))

    if not any([setup_ns, hold_ns, pw_ns, setup_fail, hold_fail, pw_fail]):
        return None

    return SlackInfo(
        setup_ns=setup_ns,
        hold_ns=hold_ns,
        pulse_width_ns=pw_ns,
        setup_failing=setup_fail,
        hold_failing=hold_fail,
        pw_failing=pw_fail,
    )


def _parse_critical_path(content: str) -> Optional[CriticalPath]:
    m = re.search(
        r"Slack \((?:MET|VIOLATED)\)\s*:\s*([\-\d.]+)ns.*?"
        r"Source:\s*(.+?)(?:\n\s+\(.*?\))?\s*\n.*?"
        r"Destination:\s*(.+?)(?:\n\s+\(.*?\))?\s*\n.*?"
        r"Data Path Delay:\s*([\d.]+)ns\s*\(logic ([\d.]+)ns \(([\d.]+)%\)\s*route ([\d.]+)ns \(([\d.]+)%\)\)",
        content,
        re.DOTALL,
    )
    if not m:
        return None

    return CriticalPath(
        slack_ns=float(m.group(1)),
        source=m.group(2).strip(),
        destination=m.group(3).strip(),
        data_path_delay_ns=float(m.group(4)),
        logic_delay_ns=float(m.group(5)),
        logic_pct=float(m.group(6)),
        route_delay_ns=float(m.group(7)),
        route_pct=float(m.group(8)),
    )
