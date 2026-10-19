"""
Hallwright Council of Masters — Guilds and Squads Registry
Organizes the 64 Domain Titans into 8 focused, high-synergy Squads.
"""

from typing import Dict, List, Any

COUNCIL_GUILDS: Dict[str, Dict[str, Any]] = {
    "software_systems": {
        "id": "guild_01",
        "name": "Software Architecture & Modular Systems Guild",
        "lead": "software_architect",
        "icon": "🏛️",
        "description": "Enterprise modular architecture, dependency injection, circuit breakers, and bounded domain contexts.",
        "members": [
            "software_architect",
            "compiler_type_architect",
            "distributed_consensus_architect"
        ]
    },
    "security_cryptography": {
        "id": "guild_02",
        "name": "Cybersecurity & Zero-Trust Defense Guild",
        "lead": "cyber_security_auditor",
        "icon": "🛡️",
        "description": "OWASP Top 10 mitigation, zero-trust perimeter, credential leakage defense, and timing-safe cryptography.",
        "members": [
            "cyber_security_auditor",
            "quantum_zkp_cryptographer"
        ]
    },
    "systems_performance": {
        "id": "guild_03",
        "name": "Systems Performance & Low-Latency Guild",
        "lead": "systems_performance_engineer",
        "icon": "⚡",
        "description": "Memory leak defense, non-blocking asynchronous event loops, CPU cache alignment, and sub-millisecond latency budgets.",
        "members": [
            "systems_performance_engineer",
            "hft_event_loop_architect"
        ]
    },
    "quality_testing": {
        "id": "guild_04",
        "name": "Quality Engineering & Testing Guild",
        "lead": "hallwright_tester",
        "icon": "🧪",
        "description": "Deterministic unit verification, mutation testing coverage, property testing, and regression defense.",
        "members": [
            "hallwright_tester",
            "legal_contract_auditor"
        ]
    },
    "database_data": {
        "id": "guild_05",
        "name": "Database Architecture & Distributed Data Guild",
        "lead": "database_architect",
        "icon": "💾",
        "description": "ACID transactions, non-blocking zero-downtime migrations, B-tree/BRIN index coverage, and N+1 query elimination.",
        "members": [
            "database_architect",
            "data_scientist_ml"
        ]
    },
    "devops_sre": {
        "id": "guild_06",
        "name": "DevOps, Cloud & Site Reliability Guild",
        "lead": "devops_cloud_architect",
        "icon": "🚀",
        "description": "Immutable container infrastructure, automated CI/CD pipelines, zero-downtime rollouts, health probes, and self-healing.",
        "members": [
            "devops_cloud_architect",
            "embedded_firmware_architect"
        ]
    },
    "api_dx_copywriting": {
        "id": "guild_07",
        "name": "API Design, DX & Documentation Guild",
        "lead": "conversion_copywriter",
        "icon": "🔌",
        "description": "REST/GraphQL API contracts, typed error models, clear documentation, and developer experience.",
        "members": [
            "conversion_copywriter",
            "elite_copywriter",
            "technical_seo_engineer"
        ]
    },
    "frontend_ui_ux": {
        "id": "guild_08",
        "name": "Frontend Architecture & UI/UX Design Guild",
        "lead": "ui_ux_designer",
        "icon": "🎨",
        "description": "Design systems, WCAG accessibility, Core Web Vitals, responsive viewports, and 60fps ergonomic interaction.",
        "members": [
            "ui_ux_designer",
            "principal_designer",
            "mobile_systems_architect"
        ]
    }
}


def get_guild_for_master(master_key: str) -> Dict[str, Any]:
    """Finds which guild a master belongs to."""
    for guild_key, guild in COUNCIL_GUILDS.items():
        if master_key in guild["members"]:
            return {"guild_key": guild_key, **guild}
    return {"guild_key": "science_archive", "name": "Scientific / Frontier Pack", "members": [master_key]}


def list_guilds_summary() -> List[Dict[str, Any]]:
    """Returns a high-level summary of all 8 guilds."""
    summary = []
    for k, g in COUNCIL_GUILDS.items():
        summary.append({
            "key": k,
            "id": g["id"],
            "name": g["name"],
            "icon": g["icon"],
            "lead": g["lead"],
            "member_count": len(g["members"]),
            "description": g["description"]
        })
    return summary
