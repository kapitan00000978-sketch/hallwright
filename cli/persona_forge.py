#!/usr/bin/env python3
"""
Hallwright Persona Forge
CLI tool to generate and register new professional personas with character names and rigorous craftsmanship checklists.
"""

import sys
import os
import json
import argparse
import random

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

FIRST_NAMES = ["Julian", "Alistair", "Cassandra", "Dominic", "Valerie", "Nathaniel", "Seraphina", "Sebastian", "Helena", "Rowan"]
EPITHETS = ["The Vanguard", "The Shield", "The Ironclad", "The Arbiter", "The Sentinel", "The Visionary", "The Strategist", "The Catalyst"]
SURNAMES = ["Vance", "Mercer", "Blackwood", "Sterling", "Cross", "Sinclair", "Hawthorne", "Thorne", "Ashford", "Kingsley"]

def generate_character_name(title):
    fname = random.choice(FIRST_NAMES)
    epithet = random.choice(EPITHETS)
    sname = random.choice(SURNAMES)
    return f"{fname} '{epithet}' {sname}"

def create_persona(title, character_name=None, archetype=None, domain="general"):
    if not character_name:
        character_name = generate_character_name(title)
    if not archetype:
        archetype = f"Master of {title} & High-Stakes Practitioner"

    print(f"🛡️ [Persona Forge] Forging new Council Master: {character_name}")
    print(f"                   Title    : {title}")
    print(f"                   Archetype: {archetype}")

    persona_id = title.lower().replace(" ", "_").replace("-", "_")

    template = {
        "id": persona_id,
        "name": character_name,
        "title": title,
        "archetype": archetype,
        "domain": domain,
        "motto": f"Excellence in {title} is non-negotiable. Every artifact delivered must be unassailable.",
        "pledge": f"I will never deliver unverified, incomplete, or irresponsible work. As {character_name}, I stand behind every solution with Production-Ready quality.",
        "checklists": [
            f"1. Strict compliance with {title} industry benchmarks and regulatory guardrails.",
            f"2. Pre-emptive identification of hidden downside risks, concurrency bottlenecks, and failure modes.",
            f"3. Clear, concise, and actionable specifications with zero cognitive fluff.",
            f"4. Built strictly on battle-tested industry best practices.",
            f"5. Autonomous pre-delivery verification satisfying zero-babysitting criteria."
        ]
    }

    persona_dir = os.path.join(".hallwright", "personas")
    os.makedirs(persona_dir, exist_ok=True)
    file_path = os.path.join(persona_dir, f"{persona_id}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    # Append to professions directory rule if exists
    rule_path = os.path.join(".agents", "plugins", "craftsman-agent", "rules", "02-professions-directory.md")
    if os.path.exists(rule_path):
        with open(rule_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n\n### 🎭 {character_name} — {title}\n")
            f.write(f"* **Archetype:** {archetype}\n")
            f.write(f"* **Pledge:** \"{template['pledge']}\"\n")
            f.write(f"* **Motto:** \"{template['motto']}\"\n")
            f.write("* **Checklist:**\n")
            for ch in template["checklists"]:
                f.write(f"  - [ ] {ch}\n")

    print(f"✅ [SUCCESS]: '{character_name}' ({title}) successfully forged and registered!")
    print(f"   Saved to : {file_path}")
    print(f"   Pledge   : \"{template['pledge']}\"")
    return template

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hallwright Persona Forge")
    parser.add_argument("--create", help="Profession title (e.g. 'Cloud Security Architect')")
    parser.add_argument("--name", help="Character name (e.g. 'Julian Vance')")
    parser.add_argument("--archetype", help="Character archetype (e.g. 'Zero-Trust Bastion')")
    parser.add_argument("--domain", default="general", help="Domain category")
    args = parser.parse_args()

    if args.create:
        create_persona(args.create, args.name, args.archetype, args.domain)
    else:
        title = input("Enter profession title (e.g. 'Cloud Security Architect'): ").strip()
        if title:
            create_persona(title)
        else:
            parser.print_help()
