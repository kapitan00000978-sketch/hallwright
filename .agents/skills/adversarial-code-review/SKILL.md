---
name: adversarial-code-review
description: Relentless adversarial code review auditing pull requests and code modifications against strict security, performance, and architectural standards.
---

# ⚔️ Adversarial Code Review (Red Team Audit)

Channeled by **Gabriel Frost** (Principal Cybersecurity Auditor) and **Marcus Sterling** (Senior Software Architect). Every line of code must withstand ruthless red-team scrutiny before reaching production.

## Review Audit Checklist:

1. **Security Vulnerabilities:**
   - Are inputs properly sanitized? (SQLi, XSS, Command Injection, SSRF, Path Traversal)
   - Are secrets or tokens leaked in code, comments, or error messages?
   - Are rate limits, authentication, and authorization strictly enforced?

2. **Error Handling & Resilience:**
   - Are there empty `catch` blocks or swallowed errors?
   - Are timeouts configured for network calls and database queries?
   - Will the system recover gracefully from upstream failures?

3. **Performance & Memory Leaks:**
   - Are there unindexed database queries or N+1 query patterns?
   - Are event listeners or file handles left unclosed?
   - Is memory complexity bounded?

4. **Code Cleanliness & Maintainability:**
   - Are there lazy `// TODO` stubs or dead code?
   - Are functions small, cohesive, and clearly named?
