# Vivado Bridge — Agent Skill

Agent-native bridge for Xilinx Vivado digital design automation. All commands return structured JSON.

## When to Use

Trigger this skill when the user mentions: Vivado, FPGA, synthesis, implementation, simulation, timing, utilization, bitstream, waveform, RTL, Verilog, SystemVerilog, or any digital circuit design operation.

## Quick Reference

| Intent | Command |
|--------|---------|
| Open existing .xpr project | `vivado-bridge open --xpr <path>` |
| New project from scratch | `vivado-bridge init --project <dir> --part <part> --top <mod>` |
| Run simulation | `vivado-bridge sim --project <dir>` |
| Run synthesis | `vivado-bridge synth --project <dir>` |
| Run implementation | `vivado-bridge impl --project <dir>` |
| Read parsed report | `vivado-bridge report --project <dir> --type timing\|utilization\|power --stage synth\|impl` |
| Check running progress | `vivado-bridge status --project <dir>` |
| Open waveform viewer | `vivado-bridge sim --project <dir> --open-waveform` |

## Result Schema

Every command outputs JSON to stdout:

```json
{
  "status": "success | failed | timeout",
  "command": "sim | synth | impl",
  "execution_time_s": 72.1,
  "errors": [],
  "warnings": ["WARNING: ..."],
  "log_tail": ""
}
```

### SimResult (additional fields)

```json
{
  "vcd_path": "C:/.../sim/dump.vcd",
  "display_output": ["Test 1: PASS", "PASS: All tests passed!"],
  "pass_fail": true,
  "testbench_top": "tb_seq_det"
}
```

### SynthResult (additional fields)

```json
{
  "timing": {
    "clocks": [{"name": "CLK", "period_ns": 10.0, "frequency_mhz": 100.0}],
    "slack": {"setup_ns": 8.879, "hold_ns": 0.066, "pulse_width_ns": 4.65, "setup_failing": 0, "hold_failing": 0, "pw_failing": 0},
    "critical_path": {"slack_ns": 8.879, "source": "...", "destination": "...", "data_path_delay_ns": 0.99, "logic_delay_ns": 0.434, "logic_pct": 43.8, "route_delay_ns": 0.556, "route_pct": 56.2}
  },
  "utilization": {
    "slice_logic": [{"name": "Slice LUTs", "used": 1, "available": 78600, "utilization_pct": 0.01}],
    "memory": [], "dsp": [], "io": []
  },
  "checkpoint_path": "C:/.../synth/top_synth.dcp"
}
```

### ImplResult (additional fields)

```json
{
  "timing": { "..." },
  "utilization": { "..." },
  "power": {
    "total_w": 0.124, "dynamic_w": 0.001, "static_w": 0.123,
    "junction_temp_c": 25.3, "confidence": "Medium",
    "components": [{"name": "Clocks", "watts": 0.001, "pct_of_dynamic": 100.0}]
  },
  "checkpoint_path": "C:/.../impl/top_impl.dcp"
}
```

## Output Format Options

```bash
--format json      # Default. Full structured JSON (agent consumption)
--format summary   # One-line: [SUCCESS] synth in 72.2s (0 errors, 19 warnings)
```

## Long-Running Operations (synth/impl)

Synthesis takes ~60-90s, implementation ~90-180s for small designs.

**Pattern for agent use:**
1. Run command in background
2. Poll progress: `vivado-bridge status --project <dir>`
3. Progress JSON: `{"elapsed_s": 45, "phase": "Phase 3 Retarget", "errors": 0, "warnings": 2, "done": false}`
4. When `"done": true`, read the full result

## Workflow

1. **Open or init** — Set up project config (project.json)
2. **Write RTL** — Create/edit Verilog/SV source files in src/ or specified paths
3. **Simulate** — `sim` command, check pass_fail and display_output
4. **Synthesize** — `synth` command, check timing.slack.all_met and utilization
5. **Implement** — `impl` command, check timing + power
6. **Iterate** — If any stage fails, modify RTL/constraints and re-run

## Visual Inspection (on-demand)

For spatial information that cannot be represented as text:

```bash
# Open waveform in Surfer after simulation
vivado-bridge sim --project <dir> --open-waveform

# Open Vivado GUI for schematic/layout/routing (future: view command)
# Currently: use Vivado GUI manually for device view, schematic, routing
```

## Environment

- Vivado 2017.4: `D:/vivado/Vivado/2017.4/bin`
- Surfer: `D:/surfer/surfer.exe`
- Python 3.9+, installed via `pip install -e C:\Users\Lenovo\Desktop\vivado-bridge`

## Project Directory Structure

```
<project>/
├── project.json         # Config (part, top, src_files, tb_files, xdc_files)
├── src/                 # RTL sources
├── tb/                  # Testbenches
├── tcl/                 # Auto-generated Tcl scripts
├── sim/                 # Simulation outputs (dump.vcd, logs, progress.json)
├── synth/               # Synthesis outputs (reports, .dcp, progress.json)
└── impl/                # Implementation outputs (reports, .dcp, .bit, progress.json)
```
