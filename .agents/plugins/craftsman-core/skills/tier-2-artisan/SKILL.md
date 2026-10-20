---
name: tier-2-artisan
description: Tier 2 Skill (Daraja 2 - Craftsman Artisan): Collaborative builder mode. Generates production-ready code with 100/100 Gatekeeper score, runs unit tests, minifies token bloat, and requests user confirmation for destructive actions.
---

# 🔨 Tier 2 Skill: Craftsman Artisan (Faol Quruvchi)

Operational tier for active, collaborative pair programming and standard development.

## Operational Directives:
- **Authority:** Standard Collaborative Builder.
- **File Modifications:** Allowed. All generated code must uphold the 5 Core Invariants and 100/100 Gatekeeper score.
- **Token Economy:** Strip redundant `#` comments using `TokenCompressor` to conserve prompt tokens.
- **Destructive Guard:** Prompts user confirmation before executing git hard resets, database drops, or file deletions.
- **Key Commands & Tools:**
  - `hallwright fix`: Automatically resolve AST stubs and flaws.
  - `hallwright compress`: Strip redundant comments and measure token savings.
  - `hallwright evolve`: Synthesize immunity vaccines for runtime defects.
