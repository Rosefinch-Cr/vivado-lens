# vivado-lens — 项目展示文档

> 一份用于演示、汇报、对外介绍的总览。所有数据基于 v0.1.0 实测结果。

## 一句话介绍

**vivado-lens** 是一个面向 LLM Agent 的 Vivado 设计反馈工具——把 Vivado 晦涩的批处理输出转换为结构化、可消费的设计智能数据，让 agent 能像资深工程师一样"读懂"FPGA 设计的时序、资源和功耗。

英文 tagline:
> **Structured design feedback for Vivado — parse, analyze, iterate.**

## 项目基本信息

| 项 | 内容 |
|---|---|
| **GitHub** | https://github.com/Rosefinch-Cr/vivado-lens (private) |
| **License** | MIT |
| **Author** | Rosefinch-Cr |
| **当前版本** | v0.1.0 (2026-05-14) |
| **语言** | Python 3.9+ |
| **支持平台** | Windows / Linux (CI 验证) |
| **目标工具** | Xilinx Vivado 2017.4+ |
| **代码规模** | ~2700 行 Python + 测试 + 文档 |
| **依赖** | pydantic, click, rich (适中) |
| **测试** | 31 个单元测试，CI 覆盖 4×2 = 8 个环境 |

## 核心价值 ("Why this exists")

Vivado 是工业级 FPGA 工具，但它产出的是**人类阅读的报告**：上百行的 timing_summary.rpt、嵌套的 utilization 表格、晦涩的 power 分解。Agent 想自动迭代设计就必须自己解析——这件事每个人都在做，每个人都在重新发明轮子。

vivado-lens 把这一层抽出来做对：**parse, don't proxy**。

不是又一个"远程跑 Vivado"的桥（virtuoso-bridge-lite 那种），而是把 Vivado 已经吐出来的报告**结构化成 Pydantic 模型**，让 agent 直接消费 JSON。

## 主要功能

### 9 个 CLI 命令
```
open    解析现有 .xpr 项目
init    初始化新项目
sim     仿真 (xvlog → xelab → xsim)
synth   综合
impl    布局布线
bit     生成 bitstream
view    打开 Vivado GUI（8 种模式）
report  解析现有报告
status  查看正在运行的进度
```

### 三种输出格式
- **`--format json`**（默认）—— 完整结构化 JSON，agent 直接消费
- **`--format text`**—— rich 终端表格，人眼直观
- **`--format summary`**—— 一行摘要 `[SUCCESS] synth in 72.2s`

### 抽取的数据
| 类别 | 字段 |
|---|---|
| **Timing** | clocks, setup/hold/PW slack, timing_met 标志, critical_path（source/destination/logic vs route 占比） |
| **Utilization** | LUT/FF/BRAM/DSP/IOB 分组使用情况 + 利用率 |
| **Power** | total/dynamic/static + per-component 占比 + 结温 + 置信度 |
| **Simulation** | pass_fail 自动检测 + $display 输出 + VCD 信号迹 |

## 架构

```
src/vivado_lens/
├── models/        Pydantic 数据契约（无 I/O，纯类型）
├── parsers/       报告文本 → 模型（纯函数，可独立测试）
├── execution/     Vivado subprocess + Tcl 模板
├── commands/      高层编排（sim/synth/impl/...）
├── client.py      VivadoBridge 门面
└── cli.py         Click CLI 入口
```

**严格的关注点分离**：parsers 不知道 subprocess，executors 不知道 Pydantic，commands 不写 print。每层都可独立替换或测试。

## Demo: 8-bit ALU 端到端验证

`examples/alu8/` 是项目的"压力测试与展示"——从空目录到 silicon-ready，4 分钟全程 agent 自动化。

### 设计
- 8-bit 同步 ALU
- 8 种操作：ADD / SUB / AND / OR / XOR / SHL / SHR / NOT
- 标志位：zero / negative / carry
- 目标：Arty A7-35T (xc7a35tcsg324-1) @ 100 MHz

### 结果（实测）

| 阶段 | 耗时 | 关键指标 |
|------|------|---------|
| sim | 14.1s | **10/10 PASS**（含 overflow/borrow 边界用例） |
| synth | 105.5s | timing met (+7.773ns)，36 LUT / 11 FF |
| impl | 118.4s | timing met (+8.157ns)，36 LUT / 19 FF，**0.089W** |

### Critical Path
```
result_reg[3]/C → zero_reg/D
Delay: 1.811ns (logic 42% / route 58%)
```
这条路径正是计算 `zero` 标志的 8 路 OR-reduction，**与人工分析结论一致**——证明 vivado-lens 抽出的"critical path 信息"对 agent 是可用的设计洞察。

### 功耗洞察
```
Total      0.089W
  Dynamic  0.017W (94% 在 I/O)
  Static   0.072W
```
**结论一眼可见**：这是个 pad-bound 设计（19 输入 + 11 输出 = 30 个 I/O 信号），优化内部逻辑收益递减——agent 读 JSON 就能做出"应该聚焦 I/O 而非组合逻辑"的判断。

## 适合用于展示的素材

### 1. README 顶部 badges（视觉识别度）
```
[Tests CI ✓] [License: MIT] [Python 3.9+] [Vivado 2017.4+] [Status: alpha]
```

### 2. `--format text` 终端截图（最有冲击力）

强烈推荐截图这两个：

**a. ALU 仿真结果 panel**：
```
SIM  14.1s
+----------------------------- Simulation Output -----------------------------+
| === ALU8 Testbench Start ===                                                |
| PASS:        ADD basic  a=0a b=05 op=000 -> result=0f carry=0 zero=0 neg=0  |
| ... 10 lines of test results ...                                            |
| === Summary: 10 PASS, 0 FAIL ===                                            |
+-----------------------------------------------------------------------------+
PASS
```

**b. ALU impl 三表合一（Timing + Utilization + Power）**：
```
IMPL  118.4s  2 warnings
                  Timing                          Utilization                       Power
+-----------------------------------------+   +----------------------+   +-----------------------------------+
| Setup     +8.157   MET                  |   | Slice LUTs   36     |   | Total       0.089                 |
| Hold      +0.194   MET                  |   | Slice Regs   19     |   |   Dynamic   0.017  6%             |
| PW        +4.500   MET                  |   | F7 Muxes      8     |   |   I/O       0.016  94%            |
| sys_clk   10.0 ns  100.0 MHz            |   | Bonded IOB   32     |   +-----------------------------------+
+-----------------------------------------+   +----------------------+
  Critical path: result_reg[3]/C → zero_reg/D
```
**这一张图同时展示**：rich 渲染美观、信息密度高、关键洞察一眼可见、和原始 .rpt 相比的可读性提升。

### 3. JSON vs RPT 对比图（核心价值证明）

并排放两个文件来强调 "parse, don't proxy"：

| 左：raw timing_summary.rpt | 右：vivado-lens 解析的 timing.json |
|---|---|
| 200+ 行 ASCII 表格 | 60 行结构化 JSON |
| 需要正则才能提取 slack | `result.timing.slack.setup_ns` 直接拿 |
| `timing_met` 需要算 | `result.timing.timing_met` 是 Pydantic 计算属性 |

可以放在 README 或博客里做对比。

### 4. Vivado GUI 截图（view 命令展示）

`vivado-lens view --mode <X>` 可以打开 8 种 Vivado GUI 视图。最适合做截图的：
- **schematic**：看 ALU 综合后的 RTL 网表
- **critical_path**：top-5 setup 路径在芯片上的物理位置（红色高亮）
- **device**：placed 设计在 Artix-7 die 上的分布

把这 3 张截图放到 `examples/alu8/screenshots/` 后，文档质感会再上一个台阶。

### 5. CI 状态徽章（工程严肃度）

GitHub Actions 已通过验证：
- 4 个 Python 版本 × 2 个操作系统 = 8 个并行 job
- 每次 push 自动跑 31 个测试
- 总耗时 2 分 17 秒

绿色 ✓ Tests badge 是工程项目"靠谱程度"的最快标记。

### 6. 架构图（如果做 PPT）

适合画一张 5 层堆叠图：
```
┌─────────────────────────────────────┐
│  CLI (Click)            cli.py      │  ← 用户/agent 入口
├─────────────────────────────────────┤
│  Client Facade          client.py   │  ← 统一 API
├─────────────────────────────────────┤
│  Commands               commands/    │  ← 编排（sim/synth/impl）
├─────────────────────────────────────┤
│  Execution              execution/   │  ← Vivado 进程 + Tcl
├──────────────────┬──────────────────┤
│  Parsers         │  Models          │
│  (pure funcs)    │  (Pydantic)      │  ← 核心抽象
└──────────────────┴──────────────────┘
```

## 与其他项目的关系

**架构灵感来源**：[virtuoso-bridge-lite](https://github.com/Arcadia-1/virtuoso-bridge-lite) — Cadence Virtuoso 的 agent 桥。

**关键差异**：

| 维度 | virtuoso-bridge-lite | vivado-lens |
|------|---------------------|-------------|
| 领域 | 模拟电路（Virtuoso） | 数字电路（Vivado） |
| 通信 | TCP daemon + SKILL IPC | 纯 subprocess batch |
| 远程支持 | SSH 隧道，多服务器 | 本地优先，架构预留 SSH |
| **核心价值** | 远程命令透传 | **报告解析与设计反馈** |
| 输出 | 原始 SKILL 返回值 | 多层次格式化（JSON / rich / summary） |

**不是衍生项目**——零代码复用，定位差异明确，README 已注明 "informed by, not derived from"。

## 路线图（CHANGELOG.md 的 Unreleased 段）

- iteration tracking：跨多次运行对比设计指标
- `wave` 独立命令：直接打开 VCD 不重跑 sim
- Linux 验证（目前 Windows 实测，Linux 仅 CI 通过）
- 更多 view 模式：路径表、片选片群、IPI 集成视图
- PyPI 发布

## 怎么向别人介绍这个项目

**30 秒电梯演讲**：
> Vivado 是 FPGA 设计的工业标准，但它输出的是给人看的报告。我做了 vivado-lens：把 Vivado 的 timing/utilization/power 报告自动解析成 Pydantic 类型，让 LLM agent 能直接读 JSON 而不是 grep 文本。命令返回结构化结果，可以判断时序是否收敛、功耗瓶颈在哪、关键路径是什么——agent 据此自动迭代 RTL。配套 9 个 CLI 命令、31 个单元测试、GitHub Actions CI。已经在 8-bit ALU 上跑通完整流程：4 分钟从空目录到 0.089W 的 placed-routed 设计。

**1 分钟版本**：在以上基础上加：
- 架构是分层 Pydantic + Click + rich 的 Python 包
- 与 virtuoso-bridge-lite 的关系（架构灵感，但领域和核心价值都不同）
- MIT 协议，可商用，欢迎二开

**15 秒标语**：
> 让 LLM agent 像资深 FPGA 工程师一样"读懂"Vivado 设计反馈。

## 文件清单（给新读者的导览）

第一次进仓库的人按这个顺序读：

1. **README.md** — 项目主页（badges + 核心价值 + 安装 + 命令表）
2. **examples/alu8/README.md** — 端到端 demo，4 分钟跑通
3. **CHANGELOG.md** — 完整开发历程（含改名故事）
4. **skill/vivado.md** — 给 LLM agent 的 skill 定义
5. **src/vivado_lens/** — 源码（按 models → parsers → commands 顺序读）
6. **tests/** — 31 个测试 + 真实 Vivado 报告 fixture

## 联系

- GitHub Issues: https://github.com/Rosefinch-Cr/vivado-lens/issues
- Repo: https://github.com/Rosefinch-Cr/vivado-lens
