---
name: zero-drift-sentinel
description: The ultimate post-integration guardrail and domain confinement engine. Strictly confines the AI agent to the real codebase, forbids fictional imports/libraries, blocks generic boilerplate stubs, validates against manifests before editing, and enforces 100/100 AST gatekeeper compliance.
---

# 🛡️ ZERO-DRIFT SENTINEL: ABSOLUTE DOMAIN CONFINEMENT ENGINE

> **The Sovereign Law:** When Hallwright is integrated into any repository, the AI agent is unconditionally confined to the authentic reality of the codebase. Hallucinations, fictional packages, generic boilerplate counters, and unanchored drift are strictly prohibited.

---

## 🏛️ 5 INVIOLABLE AXIOMS

### 1. 🔍 Autonomous Reconnaissance & Fact Grounding First
- **Manifest Audit:** Before writing or proposing any code, immediately inspect repository manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`, `requirements.txt`).
- **File Tree Grounding:** Never guess, assume, or fabricate paths. Verify actual directory structures, file existence, and exported symbols.
- **Stack Version Parity:** Strict adherence to the installed library versions and configurations.

### 2. 🚫 Absolute Ban on Fictional Dependencies (Zero Hallucination)
- **Zero Hallucinated Imports:** Never import or suggest an external library that is not installed or explicitly authorized in project manifests.
- **No Invisible Packages:** If a new library is genuinely required, verify its existence and compatibility before proposing an addition.

### 3. 🎯 Zero Generic Boilerplate Drift (Loyiha Butunligi)
- **Zero Off-Topic Dummies:** Absolute ban on generating generic `counter`, `todo-app`, `pet-store`, or irrelevant toy boilerplate code unrelated to this repository.
- **Every Line Counts:** Every single line of code, suggestion, and file must directly serve the verified repository scope, architecture, and user objective.

### 4. ⚡ Zero-Defect Craftsmanship Baseline
- **Zero Stubs:** Absolute ban on `// TODO`, `FIXME`, `pass # implement later`, or mock returns.
- **Zero Silent Catches:** Absolute ban on bare `except: pass` or empty `catch {}` blocks.
- **Defensive Paranoia:** Complete defense against OWASP Top 10 vulnerabilities (SQLi, XSS, SSRF, memory leaks, unclosed handles).

### 5. 🔄 Closed-Loop AST Gatekeeper Verification
- Silently audit all code changes against pre-commit gatekeeper standards (`python scripts/pre-commit-gatekeeper.py` or equivalent AST checks).
- Achieve a 100/100 Gatekeeper score before presenting solutions to the user.
- If a flaw or regression is detected, silently diagnose and remediate in the background without user babysitting.
