#!/usr/bin/env python3
"""
Hallwright Universal Python Installer
Usage:
    python cli/installer.py --agent all
    python cli/installer.py --agent cursor
"""

import os
import sys
import shutil
import argparse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BANNER = """
===================================================================
 🛡️  HALLWRIGHT UNIVERSAL AGENT INSTALLER
     Eliminate AI Prompt Babysitting & Enforce Professional Rigor
===================================================================
"""

SUPPORTED_AGENTS = {
    "antigravity": "antigravity-agent",
    "claude": "claude-code-agent",
    "cursor": "cursor-agent",
    "copilot": "copilot-agent",
    "windsurf": "windsurf-agent",
    "hermes": "hermes-agent",
    "codex": "codex-agent",
    "pie": "pie-agent",
    "opencode": "opencode-agent",
    "openclaw": "openclaw-agent",
    "python": "universal-python-agent",
    "cline": "cline-agent",
    "kimi": "kimi-agent",
    "kilo": "kilo-agent"
}

def copy_file_or_dir(src, dst):
    """Safely copies a file or directory tree to dst."""
    if not os.path.exists(src):
        return False
    if os.path.abspath(src) == os.path.abspath(dst):
        return True
    if os.path.isdir(src):
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            copy_file_or_dir(s, d)
    else:
        parent = os.path.dirname(dst)
        if parent:
            os.makedirs(parent, exist_ok=True)
        shutil.copy2(src, dst)
    return True


def install(agent_target="all"):
    print(BANNER)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.getcwd()

    print(f"[*] Base Directory   : {base_dir}")
    print(f"[*] Target Directory : {target_dir}")
    is_external = os.path.abspath(base_dir) != os.path.abspath(target_dir)

    # 1. Install core protocol rules and craftsman-core SSOT
    if is_external:
        agents_src = os.path.join(base_dir, "AGENTS.md")
        if os.path.exists(agents_src):
            copy_file_or_dir(agents_src, os.path.join(target_dir, "AGENTS.md"))
            print("  [+] Installed core AGENTS.md protocol")
        core_src = os.path.join(base_dir, ".agents", "plugins", "craftsman-core")
        if os.path.exists(core_src):
            copy_file_or_dir(core_src, os.path.join(target_dir, ".agents", "plugins", "craftsman-core"))
            print("  [+] Deployed shared craftsman-core (Single Source of Truth)")

    # 2. Initialize .hallwright memory directory
    mem_dir = os.path.join(target_dir, ".hallwright")
    os.makedirs(mem_dir, exist_ok=True)
    mem_file = os.path.join(mem_dir, "memory.json")
    if not os.path.exists(mem_file):
        sample_mem_src = os.path.join(base_dir, ".hallwright", "memory.json")
        if os.path.exists(sample_mem_src) and is_external:
            shutil.copy2(sample_mem_src, mem_file)
        else:
            with open(mem_file, "w", encoding="utf-8") as f:
                f.write('{"user_preferences": {}, "conventions": [], "recorded_scar_tissue": []}\n')
        print("  [+] Initialized clean project memory (.hallwright/memory.json)")

    # 3. Deploy specific agent configuration(s)
    agents_to_deploy = list(SUPPORTED_AGENTS.keys()) if agent_target == "all" else [agent_target.lower()]
    for agent_key in agents_to_deploy:
        folder = SUPPORTED_AGENTS.get(agent_key)
        if not folder:
            print(f"[!] Unknown agent: {agent_key}. Supported: {list(SUPPORTED_AGENTS.keys())}")
            continue

        agent_src_dir = os.path.join(base_dir, folder)
        if not os.path.exists(agent_src_dir):
            continue

        if is_external:
            for item in os.listdir(agent_src_dir):
                if item == "README.md":
                    continue
                src_item = os.path.join(agent_src_dir, item)
                dst_item = os.path.join(target_dir, item)
                copy_file_or_dir(src_item, dst_item)

        print(f"  [+] Active: {folder} ({agent_key})")

    print("\n[✓] SUCCESS: Hallwright protocol is now active!")
    print("    - Zero Babysitting: ON")
    print("    - 8 Software Guilds: READY")
    print("    - Self-Inspection Loop: ON")
    print("    - Auto-Remediation: ON")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hallwright Installer")
    parser.add_argument("--agent", default="all", help="Target agent or 'all'")
    args = parser.parse_args()
    install(args.agent)
