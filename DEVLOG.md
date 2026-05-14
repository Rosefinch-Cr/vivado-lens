# Development Log

## 2026-05-13: Project inception

**Background**: Started as a monolithic `vivado_cli.py` (900 lines) + `vivado_gui.py` (620 lines) Claude Code skill for automating Vivado workflows. Worked but had fundamental issues:
- Results communicated via print statements (not machine-readable)
- GUI (tkinter) mixed with CLI logic
- Single-file, not installable as a package
- Progress monitoring was hacky (polling files, flaky monitors)

**Decision**: Rewrite as a proper layered Python package inspired by [virtuoso-bridge-lite](https://github.com/Arcadia-1/virtuoso-bridge-lite) — agent-native, structured returns, clean separation of concerns.

**Key design choices**:
- Headless-first: no GUI in core package. Visual tools (Surfer, Vivado GUI) launched on-demand via explicit flags.
- JSON stdout as primary interface. Agents read JSON; humans use `--format summary`.
- Parsers are pure functions (text → model). Testable without Vivado installed.
- Executor abstraction for future SSH remote execution.

## 2026-05-14: v0.1.0 — Full flow working

**Implemented**:
1. Package scaffold (pyproject.toml, src layout, pip install -e .)
2. Models layer (Pydantic): VivadoResult, SimResult, SynthResult, ImplResult, ProjectConfig, ProgressUpdate
3. Parsers layer: timing, utilization, power, VCD, log — all tested against real Vivado reports
4. Execution layer: LocalExecutor, TclBuilder, process runner with progress.json
5. Commands layer: simulate, synthesize, implement, project management
6. CLI (Click): 7 commands registered, --format json|summary

**Verified end-to-end** on seq_det (Moore FSM sequence detector):
- `sim`: 12s, 5 tests PASS, VCD generated
- `synth`: 72s, timing met (WNS=+9.158ns), 3 FF + 1 LUT
- `impl`: 116s, 0.124W total power, timing met

**What's next**:
- `view` command (launch Vivado GUI for spatial inspection)
- `bit` command (bitstream generation)
- Git init + GitHub repo
- Tests with pytest (parser unit tests using fixture files)
- `--open-waveform` integration with Surfer
- Consider: richer `--format text` output using rich tables

## 2026-05-14: Feature additions + project identity

**Added**:
- `bit` command — bitstream generation from impl checkpoint
- `view` command — 8 modes (device/schematic/critical_path/routing/utilization/timing/power/highlight_module)
- `--format text` — rich terminal tables for timing, utilization, power
- `--open-waveform` verified working with Surfer

**Project identity pivot**:

Realized the project was positioned too similarly to virtuoso-bridge-lite ("agent-native bridge for EDA tool"). Reframed around our actual differentiator:

- **Old**: "Agent-native bridge for Xilinx Vivado" (sounds like a port of virtuoso-bridge)
- **New**: "Structured design feedback for Vivado — parse, analyze, iterate"

Key distinction: virtuoso-bridge-lite is about **remote tool control** (SSH tunnels, SKILL IPC, daemon management). We are about **design intelligence extraction** (parsing reports into structured data, enabling automated iteration). We don't proxy commands — we understand results.

Design principles codified:
1. Parse, don't proxy
2. Headless-first
3. Agent-native
4. Locally executable

Acknowledgment of virtuoso-bridge-lite as architectural inspiration added to README (proper attribution without implying derivation).
