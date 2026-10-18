# Show HN: Hallwright — The Zero-Dependency Guardrail & Auto-Healer for AI Coding Agents

**URL:** https://github.com/kapitan00000978-sketch/hallwright  
**Playground:** https://kapitan00000978-sketch.github.io/hallwright/web/  

---

### Title:
> **Show HN: Hallwright – Zero-dependency pre-commit guardrail for AI agents (Rust/Go/Node, <2ms)**

---

### Hacker News Submission Body:

Hey HN,

We built **Hallwright** because we were tired of two compounding frustrations:

1. **AI Coding Agents (Claude Code, Cursor, Copilot, Cline) commit sloppy code:**  
   They frequently leave empty catch blocks (`except: pass` or `catch(e) {}`), placeholder `// TODO` stubs, and accidental secret keys in git repositories when doing autonomous multi-file refactoring.

2. **Existing pre-commit linters and gates are painfully slow:**  
   Running SonarQube requires a heavy JVM and PostgreSQL instance (~8,500ms startup). Standard python `pre-commit` spins up virtualenvs (~1,200ms). Even Husky pulls hundreds of megabytes of `node_modules` (~450ms). In an active engineering loop, waiting multiple seconds on every git commit breaks flow state.

---

### What Hallwright Does

Hallwright is a **zero-dependency guardrail layer and craftsmanship protocol** designed specifically for human-AI pair programming and autonomous agents:

- **100x Mechanical Sympathy (< 2ms startup, 28ms full repo audit):**  
  Compiled static binaries in Go and Rust, plus a zero-npm vanilla Node.js runner and pure Python AST engine. Zero third-party dependencies. No pip, no npm packages, no JVM.
- **Autonomous Auto-Heal (`hallwright fix`):**  
  Doesn't just complain about flaws—it uses AST transformations to rewrite bare `except: pass` into structured logging, converts unhandled catches, and externalizes hardcoded credentials. With `hallwright fix -i`, you get interactive colored diffs.
- **The Council of Masters (Domain Heuristics):**  
  Embedded domain models representing 64 Engineering Titans (Architecture, Zero-Trust Security, Mechanical Sympathy, Adversarial Testing, Systems Design).
- **Universal Multi-Agent Support:**  
  Generates native configurations for Claude Code (`CLAUDE.md`), Cursor (`.cursorrules`), Copilot (`copilot-instructions.md`), Windsurf, Cline, and Antigravity IDE.
- **Cross-Agent Continuity & Persistent Memory (`.hallwright/memory.json`):**  
  Records past lessons and scar tissue so AI agents don't make the same mistake twice across session resets.

---

### 1-Line Universal Install

```bash
# Universal (Linux, macOS, Windows)
curl -fsSL https://raw.githubusercontent.com/kapitan00000978-sketch/hallwright/main/install.sh | sh

# Or via package managers:
npx hallwright init          # Node.js / Bun / Deno
pip install hallwright       # Python
go install github.com/kapitan00000978-sketch/hallwright/cmd/hallwright@latest
```

---

### Benchmarks (500+ Files Monorepo):

| Engine / Tool | Runtime | Runtime Dependencies | Latency | Memory |
| :--- | :--- | :--- | :--- | :--- |
| **SonarQube** | JVM | JRE + PostgreSQL | ~8,500 ms | ~512 MB |
| **Pre-commit** | Python | virtualenv | ~1,200 ms | ~45 MB |
| **Husky** | Node.js | node_modules | ~450 ms | ~68 MB |
| **Hallwright (Go/Rust)** | Native | **Zero (0)** | **⚡ 28 ms** | **< 4 MB** |

Try the zero-server interactive browser playground right here:  
👉 https://kapitan00000978-sketch.github.io/hallwright/web/

Everything is open source under MIT. We would love your brutal feedback on our AST inspection logic, binary footprint, and agent rules!
