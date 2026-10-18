"""
Smart Context Management & Dynamic Master Selector
Part of the Hallwright Autonomous Craftsmanship Protocol.

Selects the most relevant Council of Masters based on task description,
keywords, and file types, preventing context pollution (reducing 12K+ tokens down to ~2K).
"""

import re
from typing import List, Dict, Any, Optional

# Keyword dictionary mapping Council Master keys to high-relevance domain triggers
MASTER_KEYWORD_MAP: Dict[str, List[str]] = {
    "software_architect": [
        "architecture", "refactor", "solid", "modular", "backend", "api", "rest", "fastapi",
        "flask", "django", "express", "router", "endpoint", "controller", "service", "clean code",
        "cohesion", "coupling", "microservice", "class", "interface", "design pattern"
    ],
    "cyber_security_auditor": [
        "auth", "authentication", "authorization", "password", "hash", "bcrypt", "argon2",
        "jwt", "token", "oauth", "security", "vulnerability", "cve", "owasp", "xss", "csrf",
        "injection", "sql injection", "sanitize", "secret", "credentials", "permission", "role",
        "encryption", "decrypt", "cipher", "ssl", "tls", "key leak"
    ],
    "principal_designer": [
        "ui", "ux", "design", "css", "html", "style", "tailwind", "flexbox", "grid", "responsive",
        "component", "button", "theme", "dark mode", "color", "typography", "wcag", "accessibility",
        "contrast", "animation", "layout", "mobile design", "ergonomics"
    ],
    "database_storage_architect": [
        "database", "db", "sql", "postgres", "postgresql", "mysql", "sqlite", "mongodb", "redis",
        "query", "index", "migration", "schema", "orm", "sqlalchemy", "prisma", "foreign key",
        "join", "transaction", "deadlock", "n+1", "connection pool", "nosql"
    ],
    "devops_cloud_architect": [
        "devops", "docker", "dockerfile", "container", "kubernetes", "k8s", "helm", "ci", "cd",
        "pipeline", "github actions", "deploy", "aws", "cloud", "s3", "terraform", "iac",
        "monitoring", "prometheus", "grafana", "observability", "sre", "resilience"
    ],
    "ai_agentic_architect": [
        "agent", "llm", "prompt", "openai", "anthropic", "gemini", "claude", "langchain",
        "rag", "embedding", "vector db", "tool calling", "mcp", "hallucination", "context window",
        "circuit breaker", "autonomous agent", "subagent"
    ],
    "elite_copywriter": [
        "copy", "copywriting", "landing page", "sales", "headline", "cta", "call to action",
        "marketing", "newsletter", "email", "hook", "conversion", "clarity", "persuasion"
    ],
    "startup_cfo_analyst": [
        "finance", "cfo", "pricing", "stripe", "payment", "billing", "subscription", "unit economics",
        "cac", "ltv", "burn rate", "runway", "gross margin", "budget", "invoice"
    ],
    "legal_contract_auditor": [
        "legal", "contract", "license", "terms", "privacy", "gdpr", "compliance", "copyright",
        "trademark", "nda", "liability", "intellectual property", "clause"
    ],
    "data_scientist_ml": [
        "data science", "ml", "machine learning", "pandas", "numpy", "scikit", "sklearn", "model",
        "dataset", "feature engineering", "regression", "classification", "data leakage", "stats"
    ],
    "systems_low_level_architect": [
        "systems", "low level", "performance", "c", "c++", "rust", "memory", "allocation",
        "malloc", "pointer", "cache line", "simd", "latency", "zero copy", "multithreading"
    ],
    "distributed_consensus_architect": [
        "distributed", "consensus", "raft", "paxos", "quorum", "cluster", "replication",
        "leader election", "split brain", "eventual consistency", "cap theorem", "byzantine"
    ],
    "compiler_type_architect": [
        "compiler", "type system", "typescript", "ast", "parser", "lexer", "grammar",
        "pattern matching", "syntax tree", "static analysis", "type checker", "generics"
    ],
    "quantum_cryptographer": [
        "quantum", "cryptography", "post quantum", "lattice", "ml-kem", "fips 203", "zkp",
        "zero knowledge", "constant time", "schnorr", "side channel", "nullifier"
    ],
    "hft_event_loop_architect": [
        "hft", "trading", "low jitter", "event loop", "ring buffer", "spsc", "lock free",
        "busy polling", "cpu affinity", "tail latency", "microsecond", "nanosecond"
    ],
    "robotics_embodied_ai_architect": [
        "robotics", "kinematics", "inverse kinematics", "actuation", "torque", "motor",
        "ekf", "kalman filter", "lidar", "trajectory", "obstacle avoidance"
    ]
}

# File extension to primary master mappings
FILE_EXT_MAP: Dict[str, List[str]] = {
    ".py": ["software_architect", "cyber_security_auditor"],
    ".ts": ["software_architect", "compiler_type_architect"],
    ".tsx": ["software_architect", "principal_designer"],
    ".js": ["software_architect", "principal_designer"],
    ".jsx": ["software_architect", "principal_designer"],
    ".css": ["principal_designer"],
    ".scss": ["principal_designer"],
    ".html": ["principal_designer"],
    ".sql": ["database_storage_architect"],
    ".sh": ["devops_cloud_architect"],
    ".ps1": ["devops_cloud_architect"],
    ".dockerfile": ["devops_cloud_architect"],
    "dockerfile": ["devops_cloud_architect"],
    ".yml": ["devops_cloud_architect"],
    ".yaml": ["devops_cloud_architect"],
    ".rs": ["systems_low_level_architect", "software_architect"],
    ".c": ["systems_low_level_architect"],
    ".cpp": ["systems_low_level_architect"],
    ".go": ["software_architect", "systems_low_level_architect"],
    ".sol": ["cyber_security_auditor", "distributed_consensus_architect"]
}


class SmartMasterSelector:
    """
    Intelligently ranks and selects Council Masters based on task context and files.
    """

    def __init__(self, council_dict: Optional[Dict[str, Any]] = None):
        self.council_dict = council_dict or {}

    def score_masters(self, task_description: str, files: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Calculates a relevance score for each master based on task words and file extensions.
        """
        task_norm = (task_description or "").lower()
        # Tokenize task words
        task_tokens = set(re.findall(r"\b[a-z0-9_\-\.]{2,}\b", task_norm))
        
        scores: Dict[str, float] = {k: 0.0 for k in MASTER_KEYWORD_MAP.keys()}
        rationale: Dict[str, List[str]] = {k: [] for k in MASTER_KEYWORD_MAP.keys()}

        # 1. Keyword matching
        for master, keywords in MASTER_KEYWORD_MAP.items():
            for kw in keywords:
                if " " in kw:
                    # Multi-word phrase match
                    if kw in task_norm:
                        scores[master] += 3.5
                        rationale[master].append(f"phrase match: '{kw}'")
                elif kw in task_tokens:
                    scores[master] += 2.0
                    rationale[master].append(f"keyword match: '{kw}'")

        # 2. File extension matching
        if files:
            for file_path in files:
                p_norm = file_path.lower()
                matched_ext = None
                for ext in FILE_EXT_MAP.keys():
                    if p_norm.endswith(ext) or p_norm == ext:
                        matched_ext = ext
                        break
                if matched_ext:
                    for master in FILE_EXT_MAP[matched_ext]:
                        if master in scores:
                            scores[master] += 2.5
                            rationale[master].append(f"file type match: '{matched_ext}'")

        # 3. Security booster: if auth/sensitive data keywords appear, boost security
        security_triggers = {"auth", "password", "token", "secret", "login", "payment", "key", "credential"}
        if any(t in task_tokens for t in security_triggers):
            if "cyber_security_auditor" in scores:
                scores["cyber_security_auditor"] += 3.0
                rationale["cyber_security_auditor"].append("security booster trigger")

        # 4. Architecture baseline: ensure software_architect has baseline relevance for code tasks
        code_triggers = {"create", "build", "implement", "fix", "refactor", "endpoint", "function", "api"}
        if any(t in task_tokens for t in code_triggers):
            if "software_architect" in scores:
                scores["software_architect"] += 1.5

        # Format and rank results
        ranked = []
        for master, score in scores.items():
            if score > 0:
                ranked.append({
                    "master_key": master,
                    "score": round(score, 2),
                    "rationale": list(set(rationale[master]))
                })

        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    def select_masters(self, task_description: str, files: Optional[List[str]] = None, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Returns the top `limit` most relevant masters for the given task.
        Falls back to software_architect and cyber_security_auditor if no strong matches.
        """
        scored = self.score_masters(task_description, files)
        if not scored:
            # Fallback default pair
            default_keys = ["software_architect", "cyber_security_auditor"]
            return [
                {
                    "master_key": k,
                    "score": 1.0,
                    "rationale": ["default baseline fallback"]
                }
                for k in default_keys[:limit]
            ]
        return scored[:limit]

    def build_dynamic_prompt(
        self,
        task_description: str,
        files: Optional[List[str]] = None,
        lessons: Optional[List[Dict[str, Any]]] = None,
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        Generates a concise, high-voltage system prompt (~1.5K - 2K tokens)
        tailored exclusively to the selected masters and past lessons.
        """
        selected = self.select_masters(task_description, files, limit=limit)
        
        prompt_lines = [
            "# 🛡️ HALLWRIGHT / HALLWRIGHT DYNAMIC CONTEXT (TASK-TARGETED GUARDRAIL)",
            "",
            "## ⚡ 4 INVIOLABLE PROTOCOL INVARIANTS",
            "1. ZERO STUBS: Never output unfinished TODOs, mock functions, or empty placeholders.",
            "2. ZERO SILENT CATCHES: Bare exception suppression or empty catch blocks are strictly forbidden.",
            "3. ZERO CREDENTIAL LEAKS: Never hardcode secrets, private keys, or API tokens.",
            "4. DETERMINISTIC BOUNDS: Enforce finite recursion limits and input validation.",
            "",
            "## 🏛️ ACTIVE COUNCIL MASTERS FOR THIS TASK:"
        ]

        for s in selected:
            key = s["master_key"]
            master_data = self.council_dict.get(key, {})
            name = master_data.get("name", key.replace("_", " ").title())
            archetype = master_data.get("archetype", "Council Master")
            motto = master_data.get("motto", "Excellence is non-negotiable.")
            criteria = master_data.get("criteria", [])

            prompt_lines.append(f"### 👤 {name} ({archetype})")
            prompt_lines.append(f"> Motto: \"{motto}\"")
            prompt_lines.append("Key Criteria:")
            for c in criteria[:3]:  # Top 3 criteria to preserve token budget
                prompt_lines.append(f"- {c}")
            prompt_lines.append("")

        if lessons:
            prompt_lines.append("## ⚠️ RELEVANT PAST LESSONS & SCAR TISSUE (DO NOT REPEAT):")
            for les in lessons:
                cat = les.get("category", "general")
                lesson_text = les.get("lesson", "")
                prompt_lines.append(f"- [{cat.upper()}]: {lesson_text}")
            prompt_lines.append("")

        prompt_lines.append("## 🎯 IMMEDIATE MISSION:")
        prompt_lines.append(f"Execute task with zero defect leakage: \"{task_description}\"")

        final_prompt = "\n".join(prompt_lines)
        # Approximate token count (1 token ~= 4 chars)
        approx_tokens = len(final_prompt) // 4

        return {
            "selected_masters": selected,
            "prompt": final_prompt,
            "approx_tokens": approx_tokens,
            "optimization_ratio": f"{round(12000 / max(approx_tokens, 1), 1)}x"
        }
