# Contributing to Hallwright 🛡️

Thank you for your interest in contributing to **Hallwright**! Hallwright is an open-source engineering quality and craftsmanship protocol for AI coding assistants.

---

## 🎯 Ground Rules & Invariants

1. **Deterministic Quality Gate:** All code modifications must satisfy the pre-commit gatekeeper with a score of 100/100 (`python scripts/pre-commit-gatekeeper.py`).
2. **Zero Unfinished Stubs:** Never commit unfinished placeholders (`# TODO`, `// FIXME`, empty catches, or bare `except: pass`). Complete all logic end-to-end or use `# hallwright-ignore` if strictly justified.
3. **Automated Test Coverage:** Add or update unit tests in `tests/` for every behavior or rule you change.
4. **No Unverified Marketing Claims:** Avoid hyperbolic claims ("100% bug-free", "0% mistakes", "24/7"). Document empirical, measured facts.

---

## 🛠️ Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/kapitan00000978-sketch/hallwright.git
cd artisan

# 2. Install development dependencies
pip install -r requirements.txt pytest pytest-cov

# 3. Install the pre-commit gatekeeper hook
python scripts/install_git_hook.py

# 4. Run the test suite
python -m pytest tests -q

# 5. Run the gatekeeper manually
python scripts/pre-commit-gatekeeper.py
```

---

## 💡 Good First Issues

If you are looking for places to contribute, look for issues labeled `good first issue`:
- Adding new language support or AST checkers to `scripts/detector.py` (e.g. Go AST, Rust, Java).
- Expanding the Auto-Remediator (`scripts/remediator.py`) to auto-fix other common AI code pitfalls.
- Adding pre-configured agent settings for emerging AI assistants.
- Improving docs, playground examples, and benchmark cases in `bench/`.

---

## 🔀 Submitting a Pull Request

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Verify that all tests and gatekeeper audits pass:
   ```bash
   python -m pytest tests -q
   python scripts/pre-commit-gatekeeper.py
   ```
3. Push to your fork and submit a Pull Request.
4. Continuous Integration (GitHub Actions) will automatically verify your changes against Python 3.10, 3.11, and 3.12.
