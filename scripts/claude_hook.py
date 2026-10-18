#!/usr/bin/env python3
"""
Hallwright Claude Code Post-Tool Execution Hook
Triggered after Claude Code modifies a file:
1. Audits the changed file using Hallwright's detector (AST + Regex).
2. If defects are found, triggers autonomous auto-remediation (hallwright fix).
3. If defects remain, outputs high-signal error directives to force Claude Code to self-heal.
"""

import os
import sys

# Ensure scripts dir is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detector import scan_file, load_artisan_config
from remediator import remediate_file

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def check_and_heal(filepath: str) -> bool:
    if not filepath or not os.path.exists(filepath):
        return True

    # 1. Initial Scan
    cfg = load_artisan_config(".")
    res = scan_file(filepath, config=cfg)
    if not res or not res["findings"]:
        return True

    print(f"\n🛡️ [Hallwright Claude Hook] Defect detected in {filepath}!")
    for f in res["findings"]:
        print(f"  • Line {f['line']} [{f['category']}]: {f['message']}")

    # 2. Autonomous Auto-Remediation Attempt
    print("[*] Attempting autonomous remediation (hallwright fix)...")
    repaired_count = remediate_file(filepath)
    if repaired_count > 0:
        print(f"  [+] Auto-repaired {repaired_count} defect(s) in {filepath}")
        res_after = scan_file(filepath, config=cfg)
        if not res_after or not res_after["findings"]:
            print(f"✅ [Hallwright Verified]: All defects resolved in {filepath} (Score: 100/100)\n")
            return True

    # 3. If still defective, instruct Claude Code to fix
    print("\n❌ [Artisan Self-Healing Trigger]:")
    print(f"Claude, you modified {filepath} but it violates Artisan production benchmarks.")
    print("Directives:")
    print("  1. Remove all unhandled stubs (TODO, pass) and complete logic end-to-end.")
    print("  2. Replace bare except / empty catches with structured logging or error handling.")
    print("  3. Never hardcode API keys or secrets in source code.")
    print("Fix these defects now before finishing your turn!\n")
    return False


def main():
    target_file = sys.argv[1] if len(sys.argv) > 1 else ""
    if not target_file:
        # Check git modified files if no file argument passed
        import subprocess
        try:
            out = subprocess.check_output(["git", "diff", "--name-only"], text=True)
            files = [f.strip() for f in out.splitlines() if f.strip().endswith((".py", ".js", ".ts"))]
            for f in files:
                if not check_and_heal(f):
                    sys.exit(1)
            sys.exit(0)
        except Exception:
            sys.exit(0)

    success = check_and_heal(target_file)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
