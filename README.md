# vivado-lens

[![Tests](https://github.com/Rosefinch-Cr/vivado-lens/actions/workflows/tests.yml/badge.svg)](https://github.com/Rosefinch-Cr/vivado-lens/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Vivado](https://img.shields.io/badge/Vivado-2017.4+-orange.svg)](https://www.xilinx.com/products/design-tools/vivado.html)
[![Status](https://img.shields.io/badge/status-alpha-red.svg)]()
[![Code style](https://img.shields.io/badge/code%20style-pydantic-purple.svg)](https://docs.pydantic.dev/)

Structured design feedback for Vivado — parse, analyze, iterate.

vivado-lens turns Vivado's opaque batch-mode outputs into structured, machine-readable data. It parses timing reports, utilization tables, power breakdowns, and simulation waveforms into typed models that LLM agents and scripts can consume directly — enabling automated design iteration without GUI interaction.

## Why

Vivado produces rich design data, but it's locked behind GUI windows and verbose report files. vivado-lens extracts that intelligence:

- **Timing closure at a glance** — setup/hold/PW slack as numbers, not 500-line reports
- **Critical path decoded** — source, destination, logic vs route delay split
- **Resource awareness** — LUT/FF/BRAM/DSP usage as structured data
- **Power breakdown** — dynamic/static split with per-component attribution
- **Simulation verdict** — pass/fail detection from $display output
- **Waveform data** — VCD parsed into signal traces with transitions

All accessible via a single CLI that outputs JSON, rich terminal tables, or one-line summaries.

## Install

```bash
cd vivado-lens
pip install -e .
```

Requires:
- Python 3.9+
- Vivado 2017.4+ (path configured in `src/vivado_lens/config.py`)
- pydantic, click, rich

## Usage

```bash
# Open existing Vivado project
vivado-lens open --xpr path/to/project.xpr

# Initialize new project
vivado-lens init --project ./my_design --part xc7a35tcsg324-1 --top top

# Simulate (returns pass/fail + $display output)
vivado-lens sim --project ./my_design

# Synthesize (returns timing + utilization)
vivado-lens synth --project ./my_design

# Implement (returns timing + utilization + power)
vivado-lens impl --project ./my_design

# Generate bitstream
vivado-lens bit --project ./my_design

# Read a specific report as structured JSON
vivado-lens report --project ./my_design --type timing --stage impl

# Open Vivado GUI for spatial inspection
vivado-lens view --project ./my_design --mode schematic

# Check progress during long runs
vivado-lens status --project ./my_design
```

## Output Formats

```bash
--format json      # Default. Full structured JSON for agent/script consumption.
--format text      # Rich terminal tables (timing, utilization, power at a glance).
--format summary   # One-line: [SUCCESS] synth in 72.2s (0 errors, 19 warnings)
```

Example `--format text` output:
```
 IMPL  116.3s
                 Timing
┌─────────────┬────────────┬───────────┐
│ Check       │ Slack (ns) │  Status   │
├─────────────┼────────────┼───────────┤
│ Setup       │     +9.158 │    MET    │
│ Hold        │     +0.217 │    MET    │
│ Pulse Width │     +4.650 │    MET    │
│ Clock: CLK  │    10.0 ns │ 100.0 MHz │
└─────────────┴────────────┴───────────┘
  Critical path: state_reg[2]/C → state_reg[0]/D
  Delay: 0.841ns (logic 38% / route 62%)
                 Power
┌───────────────┬───────┬───────────┐
│ Component     │ Watts │ % Dynamic │
├───────────────┼───────┼───────────┤
│ Total         │ 0.124 │           │
│   Dynamic     │ 0.001 │           │
│   Static      │ 0.123 │           │
└───────────────┴───────┴───────────┘
```

## Architecture

```
src/vivado_lens/
├── models/       # Pydantic data models — the structured contract
├── parsers/      # Pure functions: report text → typed models (testable without Vivado)
├── execution/    # Vivado subprocess management + Tcl script generation
├── commands/     # High-level orchestration (sim, synth, impl, view)
├── client.py     # VivadoBridge facade class
└── cli.py        # Click CLI entry point
```

Design principles:
- **Parse, don't proxy** — we extract structured meaning from Vivado outputs, not just forward raw text
- **Headless-first** — core package has zero GUI dependencies; visual tools (Surfer, Vivado GUI) launched on-demand
- **Agent-native** — JSON stdout as primary interface; agents consume results directly without scraping
- **Locally executable** — no daemon, no server; just subprocess calls to Vivado batch mode

## Agent Integration

Place `skill/vivado.md` in your agent's skill directory (e.g. `.claude/commands/`). The skill provides command reference, result schemas, and workflow patterns for automated digital design.

## Acknowledgments

Architecture informed by [virtuoso-bridge-lite](https://github.com/Arcadia-1/virtuoso-bridge-lite) (analog circuit automation for Cadence Virtuoso). vivado-lens addresses a different domain (digital/FPGA) with a different core focus: report parsing and design feedback rather than remote tool control.

## License

MIT
