## 🛡️ Hallwright Pull Request Verification

### Description of Changes
Briefly describe the rationale and architecture of your changes.

### Checklist
- [ ] Ran `python -m pytest tests -q` locally (all tests pass)
- [ ] Ran `python scripts/pre-commit-gatekeeper.py` locally (score: 100/100)
- [ ] Added or updated unit tests for new/changed behavior
- [ ] Zero unhandled placeholders (`TODO`, `FIXME`, bare except, empty catch)
- [ ] Zero hardcoded secrets or sensitive keys
- [ ] Verified against `artisan.config.json`
