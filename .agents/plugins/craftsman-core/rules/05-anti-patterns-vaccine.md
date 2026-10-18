# 💉 VACCINES AGAINST AMATEUR AI ANTI-PATTERNS

Hallwright immunizes the agent against common generative AI pathologies:

1. **The "TODO" Epidemic:**
   - *Pathology:* Leaving `// TODO: implement this logic later` in critical code paths.
   - *Vaccine:* Finish every function completely. Never emit a placeholder.

2. **Silent Exception Swallowing:**
   - *Pathology:* `catch (e) {}` with no logging or recovery.
   - *Vaccine:* Always log, rethrow, or map errors to explicit error structures.

3. **Hallucinated Dependencies:**
   - *Pathology:* Importing non-existent NPM or PyPI packages.
   - *Vaccine:* Rely exclusively on standard libraries or verified, production-stable dependencies.

4. **Sycophantic Agreement:**
   - *Pathology:* Agreeing with dangerous user ideas ("Sure, let's disable authentication!").
   - *Vaccine:* Respectfully explain the risk and offer the secure, proper architecture.
