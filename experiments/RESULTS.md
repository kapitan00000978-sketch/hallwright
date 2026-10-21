# hwmem A/B Benchmark Experiment Results

This document defines the real-world A/B experimental evaluation protocol for measuring token and tool efficiency gains with `hwmem`.

---

## 🎯 Experimental Scenario: Tiny Python Todo CLI

### Project Steps:
1. **Step 1: Core Domain & Tests** — In-memory `TodoItem` and `TodoList` classes with full unit test suite.
2. **Step 2: JSON Persistence** — Add disk persistence (`todos.json`) with save/load operations.
3. **Step 3: CSV Export** — Add CSV export command (`todo export --format csv`).

---

## 🧪 Evaluation Protocol

### Session 1 (Setup Baseline):
- An agent builds Step 1 and Step 2.
- In Arm B, `hwmem` records:
  - `Goal`: Build tiny Python Todo CLI
  - `Done`: Implemented core domain, unit tests, and JSON persistence (`todos.json`)
  - `Next`: Implement CSV export (`todo export --format csv`)
  - `Verify command`: `pytest tests/test_todo.py`

### Session 2 (Evaluation Run):
A completely **FRESH chat** is launched with zero conversation history.
The user provides ONLY the prompt:
> **"continue the project"**

---

## ⚖️ Evaluation Arms

* **Arm A (Control — Without Memory):**
  - No memory system present.
  - The fresh agent must explore the codebase from scratch (listing directories, reading code, discovering what has been implemented and what remains).
* **Arm B (Treatment — With hwmem):**
  - The fresh agent follows `skills/hwmem/SKILL.md`.
  - At session start, the agent runs `python memory.py show` and reads ONLY the compact index and latest session.

---

## 📊 Experimental Results Table

*Note: Token columns (`Input Tokens`, `Output Tokens`) must be filled manually by the user from their host agent's billing/usage telemetry. Do not guess or fabricate billing figures.*

| Arm | Run # | Input Tokens | Output Tokens | Files Read | Tool Calls | Step 3 Finished (Yes/No) | Tests Pass (Yes/No) | Notes / Observations |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Arm A (No Memory)** | 1 | | | | | | | |
| **Arm A (No Memory)** | 2 | | | | | | | |
| **Arm A (No Memory)** | 3 | | | | | | | |
| **Arm B (With hwmem)** | 1 | | | | | | | |
| **Arm B (With hwmem)** | 2 | | | | | | | |
| **Arm B (With hwmem)** | 3 | | | | | | | |

---

## 📐 Summary & Token Savings Analysis

*(To be calculated after completing the 6 runs above)*

* **Average Arm A Input Tokens:** `[Pending Runs]`
* **Average Arm B Input Tokens:** `[Pending Runs]`
* **Measured Token Savings:** `[Arm A - Arm B] tokens`
* **Efficiency Improvement:** `[Savings / Arm A * 100] %`
