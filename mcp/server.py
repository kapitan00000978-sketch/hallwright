#!/usr/bin/env python3
"""
Hallwright Model Context Protocol (MCP) Server
Standard JSON-RPC 2.0 tool provider for Claude, Cursor, Antigravity, and other MCP clients.
Empowered by The Council of Masters.
"""

import sys
import os
import json

# Add directories to path for shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "sdk")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "libraries")))
from detector import scan_code

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Transparency & Ethical Disclaimer:
# The Council of Masters consists of synthetic persona archetypes and heuristic quality checklists
# derived from industry standards (OWASP, ISO/IEC 25010, SRE) and academic engineering literature.
# They are role-based heuristic models, NOT real individuals or claimed employee affiliations.

COUNCIL_MEMBERS = {
    "software_architect": {
        "name": "Marcus 'The Vanguard' Sterling",
        "archetype": "Systems Sovereign & Zero-Tech-Debt Purist",
        "title": "Senior Software Architect & Systems Lead",
        "motto": "If a system cannot fail gracefully under catastrophic load, it was never engineered—it was merely wished into existence.",
        "bio": "Synthetic domain persona embodying high-throughput distributed systems discipline, zero-tech-debt invariants, and fault-tolerant architecture (100K+ RPS, 99.999% uptime benchmarks).",
        "cognitive_discipline": "First Principles, Invariant Preservation, Graceful Degradation, Zero-Stub Discipline",
        "pledge": "I will never deliver unverified, insecure, or brittle code. Every single line of code must be production-ready.",
        "criteria": [
            "Comprehensive error handling and boundary condition checks (zero silent catches)",
            "Input sanitization, invariant validation, and credential protection",
            "Clean architecture, SOLID principles, high cohesion, low coupling",
            "Performance and memory leak prevention (bounded complexity)",
            "Zero lazy stubs or dummy TODO comments"
        ]
    },
    "elite_copywriter": {
        "name": "Diana 'The Closer' Drake",
        "archetype": "Neuromarketing Alchemist & Direct-Response Virtuoso",
        "title": "Elite Direct-Response Conversion Copywriter",
        "motto": "Every word must fight for its life on the page. If it does not move the buyer to decisive action, it is dead weight.",
        "bio": "Direct-response conversion copywriting archetype synthesizing classic persuasion principles, pain-to-dream transformations, and high-clarity hooks.",
        "cognitive_discipline": "WIIFM Arc, Pain-to-Dream Transformation, Cognitive Fluency, Friction Eradication",
        "pledge": "Every single word drives conversion. Fluff, generic filler, and robotic AI templates are strictly banned.",
        "criteria": [
            "High-impact pattern-interrupt hook within first 3 seconds",
            "Customer-centric pain-to-dream transformation arc",
            "Zero AI cliches ('In today's fast-paced world', 'delve into', 'revolutionize')",
            "High-clarity, frictionless Call-To-Action (CTA)",
            "Punchy sentence cadence and high visual skimmability"
        ]
    },
    "principal_designer": {
        "name": "Elena 'The Visionary' Rostova",
        "archetype": "Aesthetic Sovereign & Spatial Ergonomics Master",
        "title": "Principal UI/UX Designer & Systems Architect",
        "motto": "Aesthetics without ergonomics is decoration; ergonomics without beauty is sterile. A masterwork harmonizes both without compromise.",
        "bio": "UI/UX design systems archetype enforcing WCAG 2.1 AAA accessibility, rigorous 8pt spatial token harmony, and ergonomic interactive states.",
        "cognitive_discipline": "Fitts's Law, Gestalt Principles, Systematic 8pt Spatial Harmony, Inclusive Contrast",
        "pledge": "Interfaces must be elegant, intuitive, inclusive, and ergonomic. Every pixel, margin, and color must carry clear purpose.",
        "criteria": [
            "WCAG 2.1 AAA color contrast and accessibility compliance",
            "Unmistakable visual hierarchy and focal direction",
            "Rigorous 8pt spatial grid and systematic design tokens",
            "Exhaustive interactive state matrix (hover, active, disabled, loading, error)",
            "Mobile touch ergonomics (48px+ finger targets)"
        ]
    },
    "startup_cfo_analyst": {
        "name": "Victor 'The Fortress' Montgomery",
        "archetype": "Unit-Economics Inquisitor & Capital Defense Strategist",
        "title": "Startup Financial Strategist & Fractional CFO",
        "motto": "Gross margins and payback periods do not care about your pitch deck enthusiasm. Show me the cash conversion cycle.",
        "bio": "Financial modeling archetype focused on unit economics reality checks (LTV/CAC > 3.5x), runway buffers (>18 months), and downside sensitivity modeling.",
        "cognitive_discipline": "Inversion, Cash Flow Realism, Unit Economics Sensitivity, Moat Defensibility",
        "pledge": "Financial projections must be grounded in unit economics, not wishful thinking. Every risk and cost driver is surfaced explicitly.",
        "criteria": [
            "Unit economics reality check (LTV/CAC > 3.5x, payback < 12 months)",
            "Net burn rate, runway analysis, and cash buffer modeling (>18 months)",
            "Stress-testing and downside sensitivity modeling (-40% growth shock)",
            "Defensible pricing tiers and gross margins (>80%)",
            "Clear, fundable milestones for fundraising"
        ]
    },
    "legal_contract_auditor": {
        "name": "Arthur 'The Ironclad' Pendelton",
        "archetype": "Commercial Safeguard & Contractual Litigator",
        "title": "Senior Commercial Counsel & Contract Auditor",
        "motto": "An ambiguous clause is an invitation to litigation. We draft today so that all contractual obligations and liability boundaries are crystal-clear and dispute-proof.",
        "bio": "Commercial contracts auditing persona enforcing liability caps, precise dispute resolution boundaries, and unambiguous IP ring-fencing.",
        "cognitive_discipline": "Adversarial Interpretation, Liability Containment, IP Ring-Fencing, Strict Specificity",
        "pledge": "Ambiguous phrasing is a future lawsuit. Every obligation, liability limitation, and termination trigger must be airtight.",
        "criteria": [
            "Elimination of subjective or ambiguous phrasing",
            "Balanced limitation of liability (capped at 12 months fees paid)",
            "comprehensive intellectual property assignment and protection",
            "Clear termination triggers, cure periods, and transition terms",
            "Defensible confidentiality (NDA) and data privacy covenants"
        ]
    },
    "data_scientist_ml": {
        "name": "Dr. Evelyn 'The Oracle' Reed",
        "archetype": "Empirical Scientist & ML Ops Gatekeeper",
        "title": "Staff Data Scientist & ML Systems Architect",
        "motto": "If your validation data leaks into your training set, your model is not intelligent—it is simply cheating itself into a production disaster.",
        "bio": "Machine learning engineering archetype enforcing strict train/val data isolation, leakage prevention, and imbalance-resilient metrics (PR-AUC, F1).",
        "cognitive_discipline": "Empirical Rigor, Counterfactual Thinking, Data Isolation, Statistical Power",
        "pledge": "Data leakage is catastrophic. If metrics are flawed, the entire model is invalid. Every prediction must be statistically sound and reproducible.",
        "criteria": [
            "Strict train/val/test isolation and temporal data leakage elimination",
            "Imbalance-resilient evaluation metrics (PR-AUC, F1)",
            "Production drift detection and data guardrails",
            "Algorithmic fairness and bias mitigation audits",
            "Deterministic seeds and pipeline reproducibility"
        ]
    },
    "cyber_security_auditor": {
        "name": "Gabriel 'The Sentinel' Frost",
        "archetype": "Zero-Trust Inquisitor & Threat Modeling Specialist",
        "title": "Principal Cybersecurity & Offensive Security Auditor",
        "motto": "There are two types of systems: those that enforce zero trust, and those that are already compromised without knowing it.",
        "bio": "Zero-trust cybersecurity auditor archetype enforcing OWASP Top 10 mitigation, credential protection, and defense-in-depth principles.",
        "cognitive_discipline": "Assume Breach, Defense in Depth, Principle of Least Privilege, Timing Attack Immunity",
        "pledge": "I will never approve code that trusts user input blindly or exposes attack surfaces. Security is non-negotiable.",
        "criteria": [
            "Zero exposed secrets or hardcoded tokens in code or logs",
            "Exhaustive input sanitization against SQLi, XSS, SSRF, and command injection",
            "Strict principle of least privilege and role-based access control",
            "Modern cryptographic hygiene (Argon2id, bcrypt, cryptographically secure RNG)",
            "Distributed rate limiting and brute-force circuit breakers"
        ]
    },
    "devops_cloud_architect": {
        "name": "Gareth 'The Unbreakable' Drake",
        "archetype": "Chaos Engineering Commander & Zero-Downtime Guardian",
        "title": "DevOps & Cloud Site Reliability Architect",
        "motto": "Hope is not an infrastructure strategy. If your deployment requires manual prayer, your architecture is broken.",
        "bio": "Site reliability and DevOps archetype enforcing immutable IaC, automated zero-downtime rollouts, and multi-region self-healing infrastructure.",
        "cognitive_discipline": "Idempotency, Self-Healing Automation, Chaos Engineering, Immutable Infrastructure",
        "pledge": "I will never build fragile, manual, or brittle deployment pipelines. Infrastructure must be automated, reproducible, and resilient.",
        "criteria": [
            "Infrastructure as Code (IaC) idempotency and immutable image builds",
            "Zero-downtime blue/green or canary rollouts with instant rollback",
            "Full-stack observability (distributed tracing, metrics, automated alerting)",
            "Self-healing container workloads and dynamic horizontal pod auto-scaling",
            "Automated encrypted backups and tested disaster recovery (RPO < 5m, RTO < 15m)"
        ]
    }
}

# Dynamically merge all registered council members from the Artisan SDK
try:
    from sdk.craftsman import COUNCIL_MEMBERS as SDK_COUNCIL_MEMBERS
except ImportError:
    try:
        from craftsman import COUNCIL_MEMBERS as SDK_COUNCIL_MEMBERS
    except ImportError as err:
        import logging
        logging.debug("SDK council members could not be imported: %s", err)
        SDK_COUNCIL_MEMBERS = {}

for key, val in SDK_COUNCIL_MEMBERS.items():
    if key not in COUNCIL_MEMBERS:
        COUNCIL_MEMBERS[key] = {
            "name": val.get("name", key),
            "archetype": val.get("archetype", "Master of Discipline"),
            "title": val.get("archetype", "Council Master"),
            "motto": val.get("motto", "Excellence is non-negotiable."),
            "bio": f"Master of {val.get('badge', key)}. Enforces relentless domain excellence.",
            "cognitive_discipline": val.get("badge", "Domain Mastery"),
            "pledge": "I will never deliver unverified, incomplete, or brittle work.",
            "criteria": [
                f"Strict compliance with {val.get('badge', key)} domain benchmarks",
                "Zero silent error suppression and zero unhandled edge cases",
                "Production-ready implementation with autonomous self-inspection"
            ]
        }

# Initialize Smart Context Selector, Persistent Learning Memory, and Guilds
try:
    from sdk.context_selector import SmartMasterSelector
    from sdk.learning_memory import LearningMemory
    from sdk.guilds import COUNCIL_GUILDS, list_guilds_summary
    from src.memory.store import SqliteMemoryStore
except ImportError:
    try:
        from context_selector import SmartMasterSelector
        from learning_memory import LearningMemory
        from guilds import COUNCIL_GUILDS, list_guilds_summary
        from memory.store import SqliteMemoryStore
    except ImportError:
        SmartMasterSelector = None
        LearningMemory = None
        COUNCIL_GUILDS = {}
        list_guilds_summary = None
        SqliteMemoryStore = None

sqlite_store = SqliteMemoryStore() if SqliteMemoryStore else None
learning_memory = LearningMemory() if LearningMemory else None
master_selector = SmartMasterSelector(COUNCIL_MEMBERS) if SmartMasterSelector else None

TOOLS = [
    {
        "name": "artisan_inspect_code",
        "description": "Audits code against Artisan Council of Masters quality and security benchmarks before presenting it to the user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The source code to inspect"},
                "language": {"type": "string", "description": "Programming language (js, py, ts, go, etc.)"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "artisan_get_persona",
        "description": "Retrieves the exact character profile, work ethic, pledge, and checklist from The Council of Masters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "profession": {
                    "type": "string",
                    "description": "Target profession or character key (e.g. software_architect, elite_copywriter, principal_designer, startup_cfo_analyst, legal_contract_auditor, data_scientist_ml, cyber_security_auditor, devops_cloud_architect)"
                }
            },
            "required": ["profession"]
        }
    },
    {
        "name": "artisan_list_council",
        "description": "Lists all members of The Council of Masters, their names, archetypes, and signature mottos.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "artisan_recall_memory",
        "description": "Retrieves past user preferences and recorded project conventions to prevent repeating mistakes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query or category"}
            }
        }
    },
    {
        "name": "artisan_select_masters",
        "description": "Context-aware selection of the top relevant Council Masters for a specific task or files, preventing context bloat.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task description or user prompt to analyze"},
                "files": {"type": "array", "items": {"type": "string"}, "description": "Optional list of affected files or extensions"},
                "limit": {"type": "integer", "description": "Maximum number of masters to select (default: 3)"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "artisan_get_lessons",
        "description": "Searches persistent learning memory for past mistakes, scar tissue, and lessons learned relevant to the current task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Task keywords or description to match lessons against"},
                "category": {"type": "string", "description": "Optional category filter (e.g. auth, payment, database, api)"},
                "limit": {"type": "integer", "description": "Maximum lessons to return (default: 5)"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "artisan_record_learning",
        "description": "Records a new mistake, success pattern, convention, or lesson into persistent project memory (.hallwright/memory.json) to prevent repeating errors.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["mistake", "success", "convention", "anti_pattern", "lesson"],
                    "description": "The category of learning entry"
                },
                "category": {"type": "string", "description": "Domain category (e.g. auth, api, ui, database, performance)"},
                "pattern": {"type": "string", "description": "The pattern, trigger, or mistake observed"},
                "lesson": {"type": "string", "description": "The rule or remediation to follow in the future"},
                "severity": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low"],
                    "description": "Severity level (default: high)"
                }
            },
            "required": ["type", "category", "pattern", "lesson"]
        }
    },
    {
        "name": "artisan_inject_prompt",
        "description": "Generates a laser-targeted system prompt (~1.5K-2K tokens) combining selected masters and relevant lessons for the task (6x token reduction).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "The task description to generate the prompt for"},
                "files": {"type": "array", "items": {"type": "string"}, "description": "Optional list of affected file paths"},
                "limit": {"type": "integer", "description": "Max masters to include (default: 3)"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "artisan_list_guilds",
        "description": "Lists all 8 specialized Council Guilds (Squads), their leads, member counts, and focus areas.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "artisan_resume_continuity",
        "description": "Reads the cross-agent continuity checkpoint and returns handoff context, the last agent, where work stopped, completed tasks, and next steps.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "no_continuity": {"type": "boolean", "description": "Optional flag to bypass continuity check"}
            }
        }
    },
    {
        "name": "artisan_save_checkpoint",
        "description": "Records an atomic progress checkpoint to .hallwright/checkpoints.json and updates .hallwright/agent_handoff.md for future AI agents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Summary of task executed or state reached"},
                "agent": {"type": "string", "description": "Active AI agent identifier (e.g. claude, cursor, hermes)"},
                "stopped_at_file": {"type": "string", "description": "File path where work concluded or paused"},
                "stopped_at_line": {"type": "integer", "description": "Line number where work stopped"},
                "completed_milestones": {"type": "array", "items": {"type": "string"}, "description": "Milestones just finished"},
                "pending_milestones": {"type": "array", "items": {"type": "string"}, "description": "Recommended next actions"},
                "architectural_decisions": {"type": "array", "items": {"type": "string"}, "description": "Key architectural decisions"},
                "status": {"type": "string", "enum": ["IN_PROGRESS", "PAUSED", "COMPLETED"], "description": "Session status"}
            },
            "required": ["task"]
        }
    },
    {
        "name": "artisan_get_library",
        "description": "Retrieves metadata, modules, and class interfaces for universal enterprise domain libraries (architecture, security, performance, testing, copywriting, design).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "enum": ["architecture", "security", "performance", "testing", "copywriting", "design"],
                    "description": "Optional specific domain to inspect. Omit to list all available domains."
                }
            }
        }
    },
    {
        "name": "artisan_review_code",
        "description": "Performs ruthless adversarial red-team peer review (Gabriel Frost & Marcus Sterling) on source code, identifying architectural and security defects.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Source code text to review"},
                "filename": {"type": "string", "description": "Optional file path or name (default: <buffer>)"}
            },
            "required": ["code"]
        }
    }
]

# Canonical Hallwright tools (distilled 13 tools for zero bloat)
CANONICAL_HALLWRIGHT_TOOLS = []
for _t in TOOLS:
    _hw_t = dict(_t)
    _hw_t["name"] = _t["name"].replace("artisan_", "hallwright_")
    _hw_t["description"] = _t["description"].replace("Artisan", "Hallwright")
    CANONICAL_HALLWRIGHT_TOOLS.append(_hw_t)

LEGACY_ARTISAN_TOOLS = TOOLS
ALL_MCP_TOOLS = CANONICAL_HALLWRIGHT_TOOLS


def handle_resume_continuity(args):
    try:
        from continuity import ContinuityManager
        from dataclasses import asdict
        no_cont = args.get("no_continuity", False)
        manager = ContinuityManager(workspace_root=".", enabled=not no_cont)
        if not manager.is_enabled:
            return {"status": "DISABLED", "message": "Continuity tracking is disabled or bypassed."}
        cp = manager.load_checkpoint()
        return {
            "status": "ACTIVE" if cp else "NO_CHECKPOINT",
            "checkpoint": asdict(cp) if cp else None,
            "resumption_prompt": manager.generate_resumption_prompt()
        }
    except Exception as exc:
        return {"status": "ERROR", "message": str(exc)}


def handle_save_checkpoint(args):
    try:
        from continuity import ContinuityManager
        manager = ContinuityManager(workspace_root=".", enabled=True)
        task = args.get("task", "")
        agent = args.get("agent", "mcp-agent")
        stopped_file = args.get("stopped_at_file")
        stopped_line = args.get("stopped_at_line")
        completed = args.get("completed_milestones")
        pending = args.get("pending_milestones")
        decisions = args.get("architectural_decisions")
        status = args.get("status", "IN_PROGRESS")

        saved = manager.save_checkpoint(
            last_task=task,
            last_agent=agent,
            stopped_at_file=stopped_file,
            stopped_at_line=stopped_line,
            completed_milestones=completed,
            pending_milestones=pending,
            architectural_decisions=decisions,
            status=status,
        )
        return {"saved": saved, "task": task, "agent": agent}
    except Exception as exc:
        return {"saved": False, "error": str(exc)}


def handle_get_library(args):
    try:
        from registry import LibraryRegistry
        domain = args.get("domain")
        if domain:
            return LibraryRegistry.get_domain(domain)
        return LibraryRegistry.list_domains()
    except Exception as exc:
        return {"error": str(exc)}


def handle_review_code(args):
    try:
        from reviewer import AdversarialReviewer
        code = args.get("code", "")
        filename = args.get("filename", "<buffer>")
        reviewer = AdversarialReviewer()
        return reviewer.review_text(content=code, file_path=filename)
    except Exception as exc:
        return {"error": str(exc), "passed": False}


def handle_inspect_code(args):
    code = args.get("code", "")
    return scan_code(code)


def handle_get_persona(args):
    prof = args.get("profession", "software_architect").lower().replace(" ", "_").replace("-", "_")
    member = COUNCIL_MEMBERS.get(prof, COUNCIL_MEMBERS["software_architect"])
    return {
        "key": prof,
        "name": member["name"],
        "archetype": member["archetype"],
        "title": member["title"],
        "signature_motto": member["motto"],
        "bio": member["bio"],
        "cognitive_discipline": member["cognitive_discipline"],
        "pledge": member["pledge"],
        "criteria": member["criteria"]
    }


def handle_list_council(args):
    roster = []
    for key, m in COUNCIL_MEMBERS.items():
        roster.append({
            "key": key,
            "name": m["name"],
            "title": m["title"],
            "archetype": m["archetype"],
            "motto": m["motto"]
        })
    return {"council_size": len(roster), "masters": roster}


def handle_recall_memory(args):
    query = args.get("query") if isinstance(args, dict) else None
    if sqlite_store:
        try:
            lessons = sqlite_store.get_lessons(category=query, limit=100)
            conventions = sqlite_store.get_conventions(category=query)
            if lessons or conventions:
                return {
                    "status": "success",
                    "storage": "sqlite-wal",
                    "lessons_count": len(lessons),
                    "conventions_count": len(conventions),
                    "lessons": lessons,
                    "conventions": conventions
                }
        except Exception as err:
            logger.debug("SQLite memory recall failed: %s", err)

    mem_file = os.path.join(".hallwright", "memory.json")
    if os.path.exists(mem_file):
        try:
            with open(mem_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as err:
            return {"status": "Memory read error", "error": str(err)}
    return {"status": "Memory active, zero recorded failures."}


def handle_select_masters(args):
    task = args.get("task", "")
    files = args.get("files", [])
    limit = int(args.get("limit", 3))
    if master_selector:
        masters = master_selector.select_masters(task, files=files, limit=limit)
        return {"task": task, "count": len(masters), "selected_masters": masters}
    return {"status": "Selector not initialized", "selected_masters": []}


def handle_get_lessons(args):
    task = args.get("task", "")
    category = args.get("category")
    limit = int(args.get("limit", 5))
    if learning_memory:
        lessons = learning_memory.get_lessons(task=task, category=category, limit=limit)
        snippet = learning_memory.format_warning_snippet(task)
        return {"task": task, "count": len(lessons), "lessons": lessons, "warning_snippet": snippet}
    return {"status": "Memory not initialized", "lessons": []}


def handle_record_learning(args):
    rec_type = args.get("type", "lesson")
    category = args.get("category", "general")
    pattern = args.get("pattern", "")
    lesson = args.get("lesson", "")
    severity = args.get("severity", "high")
    if learning_memory:
        return learning_memory.record_learning(
            record_type=rec_type,
            category=category,
            pattern=pattern,
            lesson=lesson,
            severity=severity
        )
    return {"status": "Memory not initialized"}


def handle_inject_prompt(args):
    task = args.get("task", "")
    files = args.get("files", [])
    limit = int(args.get("limit", 3))
    lessons = []
    if learning_memory:
        lessons = learning_memory.get_lessons(task=task, limit=4)
    if master_selector:
        return master_selector.build_dynamic_prompt(
            task_description=task,
            files=files,
            lessons=lessons,
            limit=limit
        )
    return {"status": "Selector not initialized", "prompt": ""}


def handle_list_guilds(args):
    if list_guilds_summary:
        return {"guilds_count": len(COUNCIL_GUILDS), "guilds": list_guilds_summary()}
    return {"status": "Guilds not initialized", "guilds": []}


def validate_tool_arguments(tool_def, args):
    """
    Validates arguments against the tool's inputSchema per MCP JSON-RPC 2.0 specs.
    Returns None if valid, or an error description string if invalid.
    """
    if not isinstance(args, dict):
        return "Arguments must be a JSON object dictionary."

    schema = tool_def.get("inputSchema", {})
    required_fields = schema.get("required", [])
    properties = schema.get("properties", {})

    # Check required fields
    for field in required_fields:
        if field not in args:
            return f"Missing required parameter '{field}'."
        if args[field] is None:
            return f"Required parameter '{field}' cannot be null."

    # Validate types of provided fields
    for field, val in args.items():
        if field not in properties or val is None:
            continue
        prop_def = properties[field]
        expected_type = prop_def.get("type")

        if expected_type == "string":
            if not isinstance(val, str):
                return f"Parameter '{field}' must be a string, got {type(val).__name__}."
        elif expected_type == "integer":
            if isinstance(val, bool) or not isinstance(val, int):
                return f"Parameter '{field}' must be an integer, got {type(val).__name__}."
        elif expected_type == "array":
            if not isinstance(val, list):
                return f"Parameter '{field}' must be an array list, got {type(val).__name__}."
        elif expected_type == "boolean":
            if not isinstance(val, bool):
                return f"Parameter '{field}' must be a boolean, got {type(val).__name__}."

        # Enum check if specified
        if "enum" in prop_def and val not in prop_def["enum"]:
            allowed = ", ".join(repr(e) for e in prop_def["enum"])
            return f"Parameter '{field}' has invalid value {repr(val)}. Allowed: [{allowed}]."

    return None


def dispatch_request(req):
    method = req.get("method")
    msg_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "hallwright-mcp",
                    "version": "2.0.0"
                }
            }
        }
    elif method == "notifications/initialized":
        return None
    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"status": "ok", "protocol": "hallwright-mcp-2.0"}
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": ALL_MCP_TOOLS}
        }
    elif method == "tools/call":
        params = req.get("params", {})
        if not isinstance(params, dict):
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32602,
                    "message": "Invalid params: params must be a JSON object."
                }
            }

        tool_name = params.get("name")
        args = params.get("arguments", {})

        hw_name = (tool_name or "").replace("artisan_", "hallwright_")
        norm_tool = (tool_name or "").replace("hallwright_", "artisan_")
        tool_def = next((t for t in ALL_MCP_TOOLS if t["name"] == hw_name), None)
        if not tool_def:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            }

        val_err = validate_tool_arguments(tool_def, args)
        if val_err:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32602,
                    "message": f"Invalid params for tool '{tool_name}': {val_err}"
                }
            }

        if norm_tool == "artisan_inspect_code":
            output = handle_inspect_code(args)
        elif norm_tool == "artisan_get_persona":
            output = handle_get_persona(args)
        elif norm_tool == "artisan_list_council":
            output = handle_list_council(args)
        elif norm_tool == "artisan_recall_memory":
            output = handle_recall_memory(args)
        elif norm_tool == "artisan_select_masters":
            output = handle_select_masters(args)
        elif norm_tool == "artisan_get_lessons":
            output = handle_get_lessons(args)
        elif norm_tool == "artisan_record_learning":
            output = handle_record_learning(args)
        elif norm_tool == "artisan_inject_prompt":
            output = handle_inject_prompt(args)
        elif norm_tool == "artisan_list_guilds":
            output = handle_list_guilds(args)
        elif norm_tool == "artisan_resume_continuity":
            output = handle_resume_continuity(args)
        elif norm_tool == "artisan_save_checkpoint":
            output = handle_save_checkpoint(args)
        elif norm_tool == "artisan_get_library":
            output = handle_get_library(args)
        elif norm_tool == "artisan_review_code":
            output = handle_review_code(args)
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            }

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {"type": "text", "text": json.dumps(output, indent=2)}
                ]
            }
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = dispatch_request(req)
            if res is not None:
                print(json.dumps(res), flush=True)
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(err_res), flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps(handle_get_persona({"profession": "software_architect"}), indent=2))
    else:
        main()
