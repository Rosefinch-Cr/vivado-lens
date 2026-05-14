# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- pytest unit tests for parsers (timing/utilization/power/vcd)
- GitHub Actions CI (multi-Python version matrix)
- `wave` standalone command (open VCD without re-running sim)
- Iteration tracking: compare results across runs
- Linux validation (currently Windows-only tested)

## [0.1.0] — 2026-05-14

First working release. Full Vivado batch-mode flow (sim → synth → impl → bit) with
structured JSON results.

### Added
- **CLI** with 9 commands: `open`, `init`, `sim`, `synth`, `impl`, `bit`, `view`, `report`, `status`
- **Pydantic data models** for all results: `VivadoResult`, `SimResult`, `SynthResult`, `ImplResult`, `ProjectConfig`, `ProgressUpdate`
- **Report parsers** (pure functions, testable without Vivado):
  - `timing.py` — clocks, setup/hold/PW slack, critical path with logic/route delay split
  - `utilization.py` — slice logic, memory, DSP, I/O usage tables
  - `power.py` — total/dynamic/static breakdown, per-component attribution, junction temp
  - `vcd.py` — VCD signal traces with transitions
  - `log.py` — phase/error/warning extraction, `$display` output
- **Execution layer**: `LocalExecutor` (subprocess + Tcl generation), `ExecutorBase` abstraction for future SSH
- **Tcl templates** for project-mode and non-project-mode flows (synth/impl/bit/view)
- **Progress tracking** via `progress.json` for long-running operations
- **Output formats**: `--format json` (default), `--format text` (rich tables), `--format summary` (one-line)
- **8 view modes**: device, schematic, critical_path, routing, utilization, timing, power, highlight_module
- **Surfer integration** via `--open-waveform` flag on `sim` command
- **Skill definition** at `skill/vivado.md` for Claude Code agent integration
- **Project metadata**: MIT license, PyPI classifiers, GitHub URLs

### Architecture
Layered design with strict separation of concerns:
```
models/    — Pydantic contracts (no I/O)
parsers/   — text → typed models (pure)
execution/ — subprocess + Tcl
commands/  — orchestration
client.py  — facade
cli.py     — Click entry
```

### Verified
- seq_det FSM project: sim 12s, synth 72s, impl 116s, all timing met, 0.124W total power
- Vivado 2017.4 on Windows 11
- Python 3.14 (target: 3.9+)

## [0.0.1] — 2026-05-13

### Background
Started as monolithic `vivado_cli.py` (900 lines) + `vivado_gui.py` (620 lines)
Claude Code skill. Worked but had fundamental issues:

- Results communicated via `print` statements (not machine-readable)
- GUI (tkinter) mixed with CLI logic
- Single-file, not installable as a package
- Progress monitoring was hacky (file polling, flaky monitors)

### Decision
Rewrite as a proper layered Python package. Architecture informed by
[virtuoso-bridge-lite](https://github.com/Arcadia-1/virtuoso-bridge-lite),
but with a different core focus: **report parsing and design feedback**
rather than remote tool control.

Key design choices:
- Headless-first: no GUI in core package
- JSON stdout as primary interface
- Pure-function parsers (testable without Vivado)
- Executor abstraction for future SSH

### Project rename
Originally named `vivado-bridge`. Renamed to `vivado-lens` in v0.1.0 to better
reflect the project's identity: extracting design intelligence ("looking through"
opaque reports) rather than proxying commands.

[Unreleased]: https://github.com/Rosefinch-Cr/vivado-lens/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Rosefinch-Cr/vivado-lens/releases/tag/v0.1.0
