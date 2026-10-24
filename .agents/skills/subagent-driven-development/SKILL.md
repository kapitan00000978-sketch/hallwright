---
name: subagent-driven-development
description: Deconstructs complex architectures into independent tasks delegated to autonomous subagent workers, reviewing and merging each output.
---

# 🤖 Subagent-Driven Development

When tackling large codebases or complex multi-file features, divide and conquer by delegating bounded sub-tasks to isolated subagents while maintaining strict quality gates.

## Execution Rules:

1. **Shared Blackboard State Synchronization:**
   - Every subagent must synchronize against the shared blackboard (`.hallwright/swarm_blackboard.json` or `SwarmBlackboard`).
   - Ingest current project state, active contracts, and predecessor handoffs before touching code to eliminate information silos.

2. **Contract-First Protocol:**
   - No subagent may invent arbitrary data schemas, endpoints, or UI IDs.
   - The lead architect registers explicit interface contracts (JSON Schemas, TypeScript interfaces, CSS token sets). Downstream subagents must strictly adhere to these registered contracts.

3. **Structured Handoff Ledger:**
   - Upon stage completion, each subagent must record a formal handoff ledger entry:
     - `files_modified`: Exact list of files created or updated.
     - `contract_ids`: Contracts implemented or verified.
     - `constraints_for_next`: Invariants the next agent must respect.
     - `guarantees`: Verified test assertions and security baselines.

4. **Marcus Sterling Conflict Arbitration:**
   - Intersubagent disputes (e.g. Security vs Designer on dynamic canvas, or Database vs Performance on caching) are arbitrated deterministically by Marcus Sterling.
   - Security invariants (zero XSS, zero SQLi) are non-negotiable, but Security must provide safe local primitives rather than blocking UX capabilities.
   - Once arbitrated, the ruling is bound in the blackboard state.

5. **Context Isolation & Atomic Merging:**
   - Provide each subagent with only necessary bounded files to avoid token bloat.
   - Adversarially verify diffs against registered contracts and merge validated contributions atomically.
