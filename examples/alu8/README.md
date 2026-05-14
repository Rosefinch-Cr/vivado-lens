# Example: 8-bit ALU

A complete demonstration of vivado-lens running on a small but real digital design — an 8-bit ALU with flag generation, taken from empty directory to placed-and-routed silicon-ready design in under 4 minutes.

This example is what vivado-lens is *for*: turning Vivado's verbose batch-mode outputs into structured design intelligence that an LLM agent (or a script) can act on.

## The Design

`src/alu8.v` — a synchronous 8-bit ALU supporting:

| op[2:0] | Operation | Notes |
|---------|-----------|-------|
| 000 | `a + b` | with carry-out |
| 001 | `a - b` | with borrow |
| 010 | `a & b` | |
| 011 | `a \| b` | |
| 100 | `a ^ b` | |
| 101 | `a << 1` | |
| 110 | `a >> 1` | |
| 111 | `~a` | |

Outputs: `result[7:0]`, `zero`, `negative`, `carry`.

`tb/tb_alu8.v` — directed testbench with 10 cases covering basic ops, overflow, borrow, and edge values.

`src/alu8.xdc` — Arty A7-35T pin constraints + 100 MHz clock.

## The Flow

```bash
# Initialize project
vivado-lens init --project ./alu8 --part xc7a35tcsg324-1 --top alu8

# Simulate — auto-discovers src/ and tb/ files
vivado-lens sim --project ./alu8 --tb-top tb_alu8 --format text

# Synthesize
vivado-lens synth --project ./alu8 --format text

# Place & route + power analysis
vivado-lens impl --project ./alu8 --format text

# Inspect critical path interactively
vivado-lens view --project ./alu8 --mode critical_path --stage impl
```

Total wall clock: **~4 minutes** on a typical laptop with Vivado 2017.4.

## What vivado-lens Extracted

### Simulation: 10/10 PASS

```
PASS:        ADD basic  a=0a b=05 op=000 -> result=0f carry=0 zero=0 neg=0
PASS:     ADD overflow  a=ff b=01 op=000 -> result=00 carry=1 zero=1 neg=0
PASS:        SUB basic  a=10 b=03 op=001 -> result=0d carry=0 zero=0 neg=0
PASS:       SUB borrow  a=00 b=01 op=001 -> result=ff carry=1 zero=0 neg=1
PASS:            AND    a=f0 b=0f op=010 -> result=00 carry=0 zero=1 neg=0
PASS:            OR     a=f0 b=0f op=011 -> result=ff carry=0 zero=0 neg=1
PASS:            XOR    a=aa b=55 op=100 -> result=ff carry=0 zero=0 neg=1
PASS:            SHL    a=81 b=00 op=101 -> result=02 carry=0 zero=0 neg=0
PASS:            SHR    a=81 b=00 op=110 -> result=40 carry=0 zero=0 neg=0
PASS:            NOT    a=0f b=00 op=111 -> result=f0 carry=0 zero=0 neg=1
=== Summary: 10 PASS, 0 FAIL ===
```

`pass_fail: true` is detected automatically from the `$display` stream — the agent doesn't need to grep.

### Timing (post-implementation)

```
                  Timing
+-----------------------------------------+
| Check          | Slack (ns) |  Status   |
|----------------+------------+-----------|
| Setup          |     +8.157 |    MET    |
| Hold           |     +0.194 |    MET    |
| Pulse Width    |     +4.500 |    MET    |
| Clock: sys_clk |    10.0 ns | 100.0 MHz |
+-----------------------------------------+
  Critical path: result_reg[3]/C → zero_reg/D
  Delay: 1.811ns (logic 42% / route 58%)
```

The critical path drives the `zero` flag computation — an XOR-reduction across all 8 result bits — exactly what an experienced designer would identify by hand.

### Utilization

```
                    Utilization
+-------------------------------------------------+
| Resource              | Used | Available |    % |
|-----------------------+------+-----------+------|
| Slice LUTs            |   36 |     20800 |  0.2 |
| Slice Registers       |   19 |     41600 |  0.1 |
| F7 Muxes              |    8 |     16300 |  0.1 |
| Bonded IOB            |   32 |       210 | 15.2 |
+-------------------------------------------------+
```

19 FFs = 8-bit `result` + 8-bit `tmp` carry latch + 3 flags. 36 LUTs implement the 8-way operation mux.

### Power

```
                Power
+-----------------------------------+
| Component     | Watts | % Dynamic |
|---------------+-------+-----------|
| Total         | 0.089 |           |
|   Dynamic     | 0.017 |           |
|   Static      | 0.072 |           |
|   I/O         | 0.016 |       94% |
|   Slice Logic | 0.001 |        6% |
+-----------------------------------+
  Junction Temp: 25.4°C | Confidence: Low
```

**Insight**: 94% of dynamic power burns in I/O. With 32 IOBs (8+8+3 in, 8+3 out), this is a pad-bound design — internal logic optimization will yield diminishing returns. **An agent reading this JSON can decide where to focus next without reading 100 lines of `power.rpt`.**

## Files in This Example

```
examples/alu8/
├── README.md                    # this file
├── src/
│   ├── alu8.v                   # the ALU
│   └── alu8.xdc                 # pin + clock constraints
├── tb/
│   └── tb_alu8.v                # 10-case testbench
└── outputs/                     # raw + parsed
    ├── dump.vcd                 # full waveform from xsim
    ├── timing_summary.rpt       # raw Vivado report
    ├── utilization.rpt
    ├── power.rpt
    ├── timing.json              # vivado-lens parsed
    ├── utilization.json
    └── power.json
```

The `*.json` files are what your agent actually consumes — clean, typed, machine-readable.

## Reproduce This

```bash
# From the vivado-lens repo root
pip install -e .
cd examples/alu8

# vivado-lens needs a project directory with project.json
vivado-lens init --project . --part xc7a35tcsg324-1 --top alu8
vivado-lens sim --project . --tb-top tb_alu8 --format text
vivado-lens synth --project . --format text
vivado-lens impl --project . --format text
```
