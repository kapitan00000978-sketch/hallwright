<p align="center">
  <img src="./assets/hallwright-banner.jpg" alt="Hallwright Banner" width="800" />
</p>

# 🛡️ Hallwright: Autonomous Quality Protocol & Pre-Commit Craftsmanship Gate

> **Deterministic pre-commit gate, project memory, and subagent/skill definitions for Claude Code, Cursor, Copilot, Antigravity, and other AI coding assistants.**

[![CI](https://github.com/kapitan00000978-sketch/hallwright/actions/workflows/hallwright-gate.yml/badge.svg)](https://github.com/kapitan00000978-sketch/hallwright/actions)
[![npm version](https://img.shields.io/npm/v/hallwright.svg)](https://www.npmjs.com/package/hallwright)
[![MCP 2.0](https://img.shields.io/badge/MCP-JSON--RPC%202.0-orange.svg)](mcp/server.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

### ⚡ Quickstart & Verified Installation (Zero Dependencies)

Hallwright runs out-of-the-box across **Node.js, Python, Go, and compiled native binaries**:

```bash
# 🚀 1. Node.js Direct Git / NPX (Runs without npm registry dependency)
npx github:kapitan00000978-sketch/hallwright init

# 🐍 2. Python Direct Install (From GitHub or local clone)
pip install git+https://github.com/kapitan00000978-sketch/hallwright.git
# or within a cloned repository:
pip install -e .

# 🐹 3. Go Toolchain
go install github.com/kapitan00000978-sketch/hallwright/cmd/hallwright@latest

# ⚡ 4. Precompiled Standalone Native Binary (Zero runtime dependencies)
./bin/hallwright.exe init     # Windows (included in repository)
./bin/hallwright init         # Linux / macOS
```

---

### 🏎️ Multi-Engine Performance Architecture

Hallwright provides native engines engineered for minimal commit friction across any language environment:

| Engine | Implementation | Dependencies | Startup Latency | AST Inspection | Native Binary |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rust Core** (`crates/hallwright-core`) | Native Binary | **Zero (0)** | **< 2 ms** | Pre-commit regex + token scanner | `target/release/hallwright` |
| **Go Core** (`cmd/hallwright`) | Native Binary | **Zero (0)** | **< 4 ms** | Multi-file concurrent scanner | `bin/hallwright.exe` |
| **Pure Node** (`bin/hallwright.js`) | Vanilla JS | **Zero (0 npm)** | **< 15 ms** | Zero-dependency AST gate | `bin/hallwright.js` |
| **Python Engine** (`hallwright_cli.py`) | Python 3.8+ | **Zero (stdlib)** | **< 80 ms** | Full AST visitor + auto-remediation | `hallwright_cli.py` |

---

### 💡 Instant Example: What Hallwright Intercepts

```python
# ❌ Host AI Output (Blocked by Pre-Commit Gate)
def handle_webhook(payload):
    try:
        token = "sk_live_93847291834729183472"      # Secret leak!
        process_event(payload)
    except Exception:
        pass                                        # Silent error suppression!
    # Unfinished placeholder stub                   # Incomplete logic!

# ✅ After Hallwright Auto-Fix (`hallwright fix`)
import os
import logging

logger = logging.getLogger(__name__)

def handle_webhook(payload):
    token = os.environ.get("WEBHOOK_SECRET_KEY")
    if not token:
        raise ValueError("WEBHOOK_SECRET_KEY environment variable required")
    try:
        process_event(payload)
    except Exception as exc:
        logger.error("Failed to process webhook payload: %s", exc, exc_info=True)
        raise
```

---

## ⚡ The 3 Core Pillars

Hallwright is not an AI model or operating system. It sits between your developer workspace and whichever AI assistant you use, providing three deterministic guardrails:

```
                  ┌─────────────────────────────────────────┐
                  │          Your Host AI Assistant         │
                  │   (Claude Code, Cursor, Copilot, etc.)  │
                  └────────────────────┬────────────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
              ┌───────────────────┐         ┌───────────────────┐
              │  2. Project       │         │  3. Subagent &    │
              │     Memory        │         │     Skill Defs    │
              │  (.hallwright/)   │         │  (.agents/, MCP)  │
              └─────────┬─────────┘         └─────────┬─────────┘
                        │                             │
                        ▼                             ▼
                  ┌─────────────────────────────────────────┐
                  │        Local Codebase & Git Stage       │
                  └────────────────────┬────────────────────┘
                                       │ git commit
                                       ▼
                        ┌─────────────────────────────┐
                        │   1. Pre-Commit AST Gate    │
                        │   (Blocks stubs & secrets)  │
                        └─────────────────────────────┘
```

| Pillar | What It Does | Key Command |
| :--- | :--- | :--- |
| **1. Deterministic Gate** | Intercepts unfinished stubs (`pass`, `// TODO`), empty catches (`except: pass`), command injections, DOM XSS, SSRF, and secret leaks before commit. | `hallwright audit --staged` |
| **2. Project Memory** | Records past bugs as persistent "scar tissue" (`.hallwright/memory.json`, `.hallwright/memory.db`) and provides cross-agent continuity handoffs (`.hallwright/continuity.json`). | `hallwright memory` / `hallwright resume` |
| **3. Subagents & Skills** | Provides 7 specialized role definitions and domain skills that your host assistant can adopt for complex tasks. | `hallwright swarm` / `hallwright context` |

---

## 🔍 How Each Pillar Works

### Pillar 1: Deterministic Pre-Commit Gate (`scripts/detector.py`)
- **AST & Semantic Analysis:** Scans Python, JavaScript, TypeScript, Go, Java, and C# files.
- **Pattern Interception:** Catches unfinished stubs (`TODO`, `FIXME`, bare `pass`), silent error swallowers (`except: pass`, empty `catch {}`), dynamic command execution (`shell=True`, dynamic `os.system`), DOM XSS sinks (`innerHTML = user_input`, `dangerouslySetInnerHTML`), SSRF parameter risks (`requests.get(url)`), and exposed API keys (`sk-...`, `ghp_...`).
- **Auto-Fix (`hallwright fix`):** Safely refactors empty catches into structured logger statements and replaces empty stubs with atomic rollback protection.

### Pillar 2: Project Memory & Continuity (`.hallwright/`)
- **Living Scar Tissue (`.hallwright/memory.json`, SQLite WAL):** When bugs are caught and fixed, lessons are recorded. When starting new tasks, `hallwright context` injects only the matching lessons (~6x context optimization: ~2K tokens vs ~12K full rubric dump).
- **Cross-Agent Continuity (`hallwright checkpoint` & `hallwright resume`):** Checkpoints task progress, active files, and blockers so that switching between Claude Code, Cursor, or Antigravity does not lose session context.
- **Strictly Optional:** Disable anytime with `hallwright resume --no-continuity` or configuring `continuity.enabled: false`.

### Pillar 3: Subagent & Skill Definitions (`.agents/`, `skills/`)
Hallwright provides 7 structured sub-agent roles for decomposing complex engineering tasks:

> **The host agent runs the subagents; Hallwright does not call any model itself.**

| Sub-Agent | Role | Focus Area |
| :--- | :--- | :--- |
| **`hallwright-architect`** | Architecture Lead | Modular decomposition, clean APIs, zero tech-debt. |
| **`hallwright-security`** | Security Auditor | Threat modeling, OWASP Top 10 defense, credential protection. |
| **`hallwright-critic`** | Red-Team Reviewer | Objective peer review, defect ledger compilation, veto/approval. |
| **`hallwright-tester`** | Testing Lead | Edge case coverage, fuzzing, regression catch validation. |
| **`hallwright-performance`** | Performance Lead | Mechanical sympathy, zero hot-loop allocations, low latency. |
| **`hallwright-copywriter`** | Technical Writer | Clear API references, documentation, developer experience. |
| **`hallwright-healer`** | Remediation Lead | Auto-repair of silent catches, missing handlers, and stubs. |

---

## 🏛️ The Council of Masters (Core Engineering Leads)

When generating targeted context via `hallwright context "<task>"`, the `SmartMasterSelector` dynamically matches task keywords to relevant domain leads, injecting only ~2K tokens (~6x context optimization compared to a full monolithic rubric dump):

| Master | Discipline & Role | Core Focus |
| :--- | :--- | :--- |
| 💻 **Marcus 'The Vanguard' Sterling** | Senior Software Architect | SOLID architecture, clean interfaces, zero unhandled stubs |
| 🛡️ **Gabriel 'The Sentinel' Frost** | Principal Cybersecurity Auditor | OWASP Top 10, credential protection, SQL injection prevention |
| ⚡ **Gareth 'The Unbreakable' Drake** | DevOps & Cloud Reliability Architect | Idempotent IaC, container standards, health probes |
| 🔬 **Dr. Evelyn 'The Oracle' Reed** | Staff Data Scientist & ML Architect | Data integrity, leakage prevention, statistical validation |
| 🎨 **Elena 'The Visionary' Rostova** | Principal UI/UX Design Architect | WCAG 2.1 AAA accessibility, design tokens, spatial consistency |
| 📊 **Victor 'The Fortress' Montgomery** | Financial & Unit-Economics Architect | Deterministic calculations, transaction boundaries, audit logs |
| ⚖️ **Arthur 'The Ironclad' Pendelton** | Commercial Counsel & Contract Auditor | License compliance, contract safety, clear boundary definitions |
| 🎯 **Diana 'The Closer' Drake** | Technical Documentation & DX Lead | High-clarity documentation, developer experience, zero AI fluff |

> **Complete 64-Master Roster:** For specialized deep-tech, compiler, distributed systems, and physics domain leads, see [`docs/COUNCIL.md`](./docs/COUNCIL.md).

---

## 📊 Master Architecture & Defect Taxonomy (Tasnif)

Hallwright operates on a formal **5-Tier Taxonomy & Classification Matrix**, guaranteeing consistent defect detection, penalty attribution, and multi-language performance:

1. **Defect Taxonomy & Penalties:** 18 deterministic rules across Stubs (`STUB_TODO_FIXME`, `STUB_BARE_EXCEPT`), Dangerous Execution (`DANGEROUS_EVAL_EXEC`, `DANGEROUS_SQL_INJECTION`, `DANGEROUS_COMMAND_INJECTION`, `DANGEROUS_DOM_XSS`, `DANGEROUS_SSRF`), and Credentials (`SECRET_...`).
2. **Enterprise Domain Libraries:** 8 decoupled, zero-dependency domain modules across Architecture, Security, Database, Performance, Resilience, Testing, Copywriting, and Design (`src/libraries/`).
3. **Agent Ecosystem Taxonomy:** Multi-tier configurations across 14 environments (Cursor, Claude Code, Copilot, Windsurf, Cline, Antigravity IDE).
4. **Polyglot Runtime Spectrum:** Rust (2ms), Node.js (15ms), Go (28ms), Python AST (200ms), and WebAssembly (0.4ms).
5. **The 5 Core Invariants:** Zero-Defect Self-Inspection, Defensive Architecture, Background Auto-Correction, Zero Babysitting, and Constructive Partnership.

👉 **Full Official Documentation:** See [`docs/TAXONOMY.md`](./docs/TAXONOMY.md) (and [`docs/TASNIF.md`](./docs/TASNIF.md)).

```bash
# Display full taxonomy matrix in terminal
hallwright taxonomy

# Display in Uzbek or export as JSON
hallwright tasnif --json
```

---

## ❓ What `hallwright swarm` Actually Does

`hallwright swarm` does **not** invoke an LLM or make external API calls. It is a local, deterministic planning and coordination tool:

1. **Task Decomposition:** Analyzes the task description and target files using keyword and extension heuristics.
2. **Role Selection:** Selects relevant sub-agent roles from the definitions above.
3. **Memory Retrieval:** Queries `.hallwright/memory.json` to attach historical lessons relevant to each role.
4. **Plan Generation:** Outputs a structured, ordered execution plan (e.g. Architect → Security → Tester → Critic) with clear directives.
5. **Session Coordination:** In execution mode, registers session locks in `.hallwright/agent_sessions.json` to prevent multi-agent file collisions.
6. **Execution by Host:** Your **host AI assistant** (Claude Code, Cursor, Antigravity) receives the plan and executes the steps.

```bash
# Preview the decomposition plan for a task:
hallwright swarm "Implement JWT authentication and Stripe webhook" --plan

# Register stages and session locks for the host agent:
hallwright swarm "Implement JWT authentication and Stripe webhook"
```

---

## 📊 Synthetic Verification Suite (`bench/`)

Hallwright provides a reproducible verification harness evaluating deterministic static detection and autonomous remediation across 10 controlled fixtures containing common AI anti-patterns (`python bench/run_benchmark.py`):

| Fixture Metric | Baseline (no gate) | With Hallwright (Gatekeeper + Auto-Fix) |
| :--- | :--- | :--- |
| **Quality Gate Pass Rate** | `1 / 10` (10.0%) | **`10 / 10` (100.0%)** |
| **Defects Neutralized** | `0` (flaws leak into codebase) | **`9` anti-patterns deterministically resolved** |
| **Remediation Cycles** | Unbounded / Manual human triage | **Average `1.0` cycle auto-remediation** |

> Controlled evaluation methodology and task fixtures: [`bench/BENCHMARK_REPORT.md`](./bench/BENCHMARK_REPORT.md).  
> *Note: Hallwright's internal protocol and CLI test suite contains 334 passing unit, regression, and mutation tests (plus 39 specialized deep-tech science tests in `packs/science/`).*

---

## 🔌 Model Context Protocol (MCP 2.0 Server)

Hallwright exposes its inspection, memory, and library suite as standard JSON-RPC 2.0 tools for Claude Desktop, Claude Code, Cursor, Windsurf, and Antigravity:

```bash
# Start MCP server over stdio:
hallwright mcp
# or: python mcp/server.py
```

### Exposed MCP Tools:
- `hallwright_select_masters` — Context-aware selection of relevant domain leads based on task keywords.
- `hallwright_inject_prompt` — Generates a task-targeted 2K-token prompt (~6x context optimization).
- `hallwright_inspect_code` — Pre-commit AST-level flaw and secret leak analysis on code strings.
- `hallwright_get_lessons` — Searches past scar tissue and mistakes to prevent repeating bugs.
- `hallwright_record_learning` — Writes lessons and success patterns into persistent storage.
- `hallwright_resume_continuity` — Retrieves cross-agent continuity state and checkpoints.
- `hallwright_save_checkpoint` — Saves task progress and blockers across sessions.
- `hallwright_get_library` — Retrieves production implementation modules (`auth`, `db`, `payments`, etc.).
- `hallwright_review_code` — Runs adversarial red-team code review on diffs or source code.
- `hallwright_get_persona` — Retrieves full discipline criteria and pledge for any Council Master.
- `hallwright_list_council` — Lists the Council roster.
- `hallwright_recall_memory` — Direct query interface for memory ledger.

---

## 📦 Universal Production Libraries (`src/libraries/`)

Hallwright includes zero-dependency, production-grade building blocks ready for immediate use via `hallwright lib <domain>`:

| Domain Module | Real Verified Path | Description |
| :--- | :--- | :--- |
| **AgentMesh Communication** | [`src/sdk/agent_mesh.py`](./src/sdk/agent_mesh.py) | Zero-dependency async event bus & correlation trace ledger for autonomous sub-agents. |
| **Architecture & Outbox** | [`src/libraries/architecture/outbox_pattern.py`](./src/libraries/architecture/outbox_pattern.py) | Transactional outbox engine with guaranteed delivery and circuit breaker (`circuit_breaker.py`). |
| **Domain Invariant Guard** | [`src/libraries/architecture/invariant_guard.py`](./src/libraries/architecture/invariant_guard.py) | Pre/post-condition invariant contracts, runtime assertions, and architectural boundaries. |
| **Security & Crypto Vault** | [`src/libraries/security/crypto_vault.py`](./src/libraries/security/crypto_vault.py) | PBKDF2-HMAC key derivation, secret zeroizer (`SecretZeroizer`), and JWT engine (`jwt_validator.py`). |
| **ReDoS Sanitizer** | [`src/libraries/security/redos_sanitizer.py`](./src/libraries/security/redos_sanitizer.py) | Catastrophic regex backtracking denial-of-service analyzer and XSS/SQLi guard (`sanitizer.py`). |
| **Resilience & Backpressure** | [`src/libraries/resilience/backpressure.py`](./src/libraries/resilience/backpressure.py) | Token Bucket rate limiter and Leaky Bucket burst smoother preventing thread starvation. |
| **High-Throughput Performance** | [`src/libraries/performance/cache.py`](./src/libraries/performance/cache.py) | Thread-safe LRU/TTL cache, zero-alloc buffer pool (`object_pool.py`), and ring buffer (`ring_buffer.py`). |
| **Mutation & Fuzz Testing** | [`src/libraries/testing/mutation_suite.py`](./src/libraries/testing/mutation_suite.py) | AST mutation test generator and deterministic property-based fuzzer (`fuzzer.py`). |
| **Developer Experience** | [`src/libraries/copywriting/dx_linter.py`](./src/libraries/copywriting/dx_linter.py) | Developer experience & docstring linter and Keep-a-Changelog generator (`changelog.py`). |
| **Spatial 3D & Design** | [`src/libraries/design/spatial_3d.js`](./src/libraries/design/spatial_3d.js) | Standalone Three.js/WebGL spatial swarm HUD and dark-mode CSS tokens (`liquid_glass.css`). |

---

## 📁 Supported AI Agent Ecosystems

Hallwright configures 14 agent environments with native instructions and rule sets:

| # | Agent Environment | Target Platform | Core Config Files |
| :- | :--- | :--- | :--- |
| 1 | 🤖 [`antigravity-agent/`](./antigravity-agent/) | **Google Antigravity & Gemini CLI** | `.agents/plugins/`, `AGENTS.md`, `skills/` |
| 2 | 🧠 [`claude-code-agent/`](./claude-code-agent/) | **Anthropic Claude Code CLI** | `CLAUDE.md`, `skills/` |
| 3 | ⚡ [`cursor-agent/`](./cursor-agent/) | **Cursor AI Code Editor** | `.cursorrules`, `.cursor/rules/*.mdc`, `skills/` |
| 4 | 🐙 [`copilot-agent/`](./copilot-agent/) | **GitHub Copilot (CLI & Workspace)** | `.github/copilot-instructions.md`, `skills/` |
| 5 | 🌊 [`windsurf-agent/`](./windsurf-agent/) | **Windsurf IDE (Cascade AI)** | `.windsurfrules`, `skills/` |
| 6 | 🛠️ [`cline-agent/`](./cline-agent/) | **Cline & Roo Code (VS Code Extension)** | `.clinerules`, `skills/`, `mcp/server.py` |
| 7 | 🌙 [`kimi-agent/`](./kimi-agent/) | **Moonshot Kimi Code Agent** | `KIMI.md`, `skills/`, `mcp/server.py` |
| 8 | ⚡ [`kilo-agent/`](./kilo-agent/) | **Kilo Code Agent** | `KILO.md`, `skills/`, `mcp/server.py` |
| 9 | 🏛️ [`hermes-agent/`](./hermes-agent/) | **Nous Research Hermes Agent OS** | `HERMES.md`, `system_prompt.txt`, `skills/` |
| 10| 💻 [`codex-agent/`](./codex-agent/) | **OpenAI Codex CLI** | `CODEX.md`, `.codex/config.json`, `skills/` |
| 11| 🥧 [`pie-agent/`](./pie-agent/) | **Pi / Pie Coding Agent CLI (Rust)** | `PIE.md`, `.pie/config.json`, `skills/` |
| 12| 🖥️ [`opencode-agent/`](./opencode-agent/) | **OpenCode Terminal TUI Agent** | `OPENCODE.md`, `.opencode/agent.json`, `skills/` |
| 13| 🦅 [`openclaw-agent/`](./openclaw-agent/) | **OpenClaw Autonomous Agent Platform** | `OPENCLAW.md`, `.openclaw/agent_manifest.json`, `skills/` |
| 14| 🐍 [`universal-python-agent/`](./universal-python-agent/) | **Python, LangChain, AutoGen, CrewAI** | `craftsman/` SDK, `example.py`, `skills/` |

---

## 🚀 Reusable GitHub Action & Pre-Commit Hook

### 1. GitHub Actions CI (`.github/workflows/hallwright.yml`):
Audit pull requests, fail on defects, and upload OASIS SARIF v2.1.0 findings to GitHub Code Scanning:

```yaml
name: Hallwright Quality Gate
on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - name: Run Hallwright Quality & Security Gate
        uses: kapitan00000978-sketch/hallwright@v2
        with:
          sarif-file: hallwright.sarif

      - name: Upload SARIF to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: hallwright.sarif
```
*(Both `@v2` and `@v1` tags resolve to current stable releases).*

### 2. Standard `pre-commit` Framework (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/kapitan00000978-sketch/hallwright
    rev: v2.0.0
    hooks:
      - id: hallwright-gate
```

---

## 📚 Deep-Dive Documentation (`docs/`)

Specialized tools and extended documentation are maintained in `docs/`:

- **Complete 64-Master Council Roster:** [`docs/COUNCIL.md`](./docs/COUNCIL.md) (All 64 domain personas across 8 guilds).
- **Hallwright Studio (Visual UI Audits):** [`docs/STUDIO.md`](./docs/STUDIO.md) (Playwright headless Chromium visual capture and DOM checks).
- **AST Mutation Testing Engine:** [`docs/MUTATION_TESTING.md`](./docs/MUTATION_TESTING.md) (Test assertiveness verification via semantic mutants).
- **Adversarial Red-Team Code Review:** [`docs/RED_TEAM_REVIEW.md`](./docs/RED_TEAM_REVIEW.md) (Independent defect ledger and PR review generation).

---

## 💻 CLI Command Reference

```bash
# ⚡ Initialization & Setup
hallwright init                 # Auto-detects stack, installs pre-commit hook & agent configs
hallwright doctor               # Diagnostic check on git hooks, MCP, and agent rules

# 🛡️ Quality Audit & Auto-Fix
hallwright audit                # Audits entire repository for stubs, secrets & bad patterns
hallwright audit --staged       # Fast audit on git-staged changes only
hallwright audit --sarif         # Emits OASIS SARIF v2.1.0 report for GitHub Code Scanning
hallwright fix                  # Automatically repairs silent catches and unfinished stubs

# 🎯 Context & Memory
hallwright context "<task>"     # Generates targeted 2K-token prompt (~6x context optimization)
hallwright memory               # Inspects living persistent memory and recorded scar tissue
hallwright memory --search "jwt" # Search historical lessons by keyword

# 🤖 Swarm Coordination (Planning for Host Agent)
hallwright swarm "<task>" --plan # Previews multi-agent decomposition plan
hallwright swarm "<task>"       # Registers session locks for the planned stages
hallwright agents               # Displays active agent concurrency and file locks

# 🔄 Cross-Agent Continuity
hallwright resume               # Resumes from last agent checkpoint
hallwright checkpoint "<msg>"   # Checkpoints active progress and blockers
hallwright resume --no-continuity # Disables continuity tracking

# 🧪 Mutation Testing & Red-Team Review
hallwright mutate               # Measures test suite assertiveness via AST mutation testing
hallwright review               # Runs adversarial red-team peer review on files or git diff

# 📦 Enterprise Libraries
hallwright lib auth             # Inspects and exports production auth & security library
hallwright lib db               # Inspects database connection pool & migration library
hallwright lib payments         # Inspects idempotent payment processing library
hallwright lib list             # Lists all available domain libraries

# 🌐 3D Spatial Swarm HUD & Dashboard
hallwright 3d                   # Launches hardware-accelerated 3D spatial swarm dashboard
hallwright hud                  # Launches interactive terminal dashboard

# 🌐 Protocol Server & Metrics
hallwright mcp                  # Launches Model Context Protocol JSON-RPC 2.0 server
hallwright metrics              # Prints workspace quality score and file statistics

# 📊 Master Taxonomy & Classification (Tasnif)
hallwright taxonomy             # Displays full 5-tier classification matrix in terminal
hallwright tasnif --json        # Exports complete taxonomy metadata as JSON
```

---

## 🔍 Scope & Limitations

- **Pre-Commit Defense:** The gatekeeper (`scripts/pre-commit-gatekeeper.py`) inspects staged source files and AST nodes before git commits are finalized.
- **Deterministic Scope:** The gatekeeper deterministically detects unfinished stubs, bare exception catches (`except: pass`, empty `catch {}`), dangerous dynamic code execution, and hardcoded secrets. It does not replace application-specific business logic tests.
- **Host Execution:** Hallwright does not run an LLM. Your host agent executes all coding actions; Hallwright acts as the deterministic verification and memory layer.
- **Local Continuity:** Checkpoints track files, status, and notes in `.hallwright/continuity.json`. It is fully local and does not transmit code to external servers.

---

## 📄 License
MIT License. Open source under the MIT License.
