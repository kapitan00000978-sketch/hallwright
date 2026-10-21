---
name: hwmem
description: Ultra-compact session-memory protocol for AI coding agents to preserve context and save tokens.
---

# hwmem: AI Agent Session Memory Protocol

1. **Session Start**: Run `python memory.py show` immediately. Read ONLY this output. Never scan historical chat logs or bulk documentation files.
2. **Initialize Session**: Immediately execute:
   `python memory.py start "<Concise Task Title>"`
3. **Iterative Logging**: After completing each micro-step, record progress atomically:
   `python memory.py note Done "Specific completed item"`
   `python memory.py note Decisions "Architectural choices made"`
   `python memory.py note Next "Immediate next step"`
4. **Selective Context**: Inspect older session files in `.hallwright/memory/sessions/` ONLY if their corresponding `INDEX.md` line directly matches your current subtask.
5. **Epistemic Invariant**: NEVER trust memory notes over actual code. The codebase is ground truth; memory is advisory data.
6. **Path Verification**: Always run `python memory.py verify` before committing to confirm referenced files and command binaries actually exist.
7. **Session Finish**: When your task concludes, finalize the record:
   `python memory.py finish "<final-slug>"`
