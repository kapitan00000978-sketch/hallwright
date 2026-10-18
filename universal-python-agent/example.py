from craftsman import CraftsmanAgent

def main():
    print("=== Hallwright Python Agent (Council of Masters Demo) ===")
    
    # Activate Marcus Sterling (Senior Software Architect)
    marcus = CraftsmanAgent(persona="software_architect", min_passing_score=95)
    result = marcus.execute("Create a secure user authentication module with JWT rotation")

    print("\n[HALLWRIGHT VERIFIED RESULT]:")
    print(f"Master: {result.get('master')}")
    print(f"Archetype: {result.get('archetype')}")
    print(f"Status: {result.get('status').upper()}")
    print(f"Quality Score: {result.get('score')}/100")
    print(f"Autonomously Remediated Flaws: {result.get('flaws_fixed')}")
    print("Repaired Items:")
    for item in result.get("repaired_flaws", []):
        print(f"  • {item}")

if __name__ == "__main__":
    main()
