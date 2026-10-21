"""
Persistent Learning Memory Engine for Hallwright
Part of the Hallwright Autonomous Craftsmanship Protocol.

Records AI agent mistakes, successes, conventions, and past scar tissue
in `.hallwright/memory.json`, dynamically retrieving relevant lessons
to prevent repeated errors across sessions.
"""

import os
import json
import re
import tempfile
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger("hallwright.memory")

try:
    from src.memory.store import SqliteMemoryStore
except ImportError:
    try:
        from memory.store import SqliteMemoryStore
    except ImportError:
        SqliteMemoryStore = None

DEFAULT_MEMORY_PATH = os.path.join(".hallwright", "memory.json")


def normalize_token(word: str) -> str:
    """Normalizes token, stripping apostrophes and inflectional suffixes in Uzbek and English."""
    w = word.lower().strip()
    w = w.replace("‘", "'").replace("’", "'").replace("`", "'")
    w = w.replace("o'", "o").replace("g'", "g").replace("'", "")
    # Uzbek suffix stemming
    w = re.sub(r"(ning|dan|dir|lar|lik|chi|miz|siz|ga|ka|qa|da|ni|si|i)$", "", w)
    # English suffix stemming
    w = re.sub(r"(ing|tion|ment|able|ity|ed|es|s)$", "", w)
    return w if len(w) >= 2 else word.lower()


# Semantic domain synonym expansion mapping (Multilingual Uzbek + English)
SYNONYM_MAP: Dict[str, List[str]] = {
    # Auth & Security & Credentials
    "login": ["auth", "authentication", "session", "credential", "kirish", "parol", "user"],
    "signup": ["auth", "registration", "user", "royxat", "ro'yxat"],
    "password": ["auth", "hash", "secret", "credential", "parol", "bcrypt", "argon2"],
    "parol": ["password", "auth", "hash", "secret", "credential", "login", "shifrlash", "xavfsizlik"],
    "jwt": ["auth", "token", "signature", "bearer", "maxfiy"],
    "auth": ["authentication", "session", "credential", "login", "signup", "password", "parol", "himoya", "xavfsizlik"],
    "security": ["xavfsizlik", "himoya", "auth", "xss", "sqli", "injection", "credential", "secret", "guard"],
    "xavfsizlik": ["security", "auth", "himoya", "sanitization", "xss", "sqli", "csrf", "secret"],
    "himoya": ["security", "guard", "defense", "protection", "xavfsizlik", "sanitization"],
    "token": ["jwt", "bearer", "secret", "auth", "credential"],

    # Payments & Checkout & Cart
    "payment": ["stripe", "billing", "charge", "checkout", "idempotency", "tolov", "to'lov", "savat", "karta", "order"],
    "stripe": ["payment", "billing", "charge", "idempotency", "checkout"],
    "billing": ["payment", "stripe", "charge", "invoice", "tolov"],
    "money": ["payment", "finance", "billing", "pul"],
    "tolov": ["payment", "stripe", "billing", "charge", "checkout", "idempotency", "savat", "karta", "narx"],
    "to'lov": ["payment", "stripe", "billing", "charge", "checkout", "idempotency", "savat", "karta"],
    "savat": ["cart", "checkout", "payment", "order", "buyurtma", "tolov"],
    "cart": ["savat", "checkout", "payment", "order", "buyurtma"],
    "order": ["buyurtma", "checkout", "payment", "savat"],
    "buyurtma": ["order", "checkout", "payment", "savat"],

    # Database & Storage & SQL
    "db": ["database", "sql", "query", "migration", "baza", "jadval"],
    "database": ["db", "sql", "query", "migration", "sqlite", "postgres", "mysql", "baza", "jadval", "schema"],
    "sql": ["database", "query", "injection", "orm", "sqli", "baza"],
    "sqlite": ["database", "sql", "baza", "wal", "store", "memory", "storage"],
    "postgres": ["database", "sql", "pool", "baza"],
    "mysql": ["database", "sql", "pool", "baza"],
    "baza": ["database", "db", "sql", "sqlite", "postgres", "query", "jadval", "schema", "migration", "sorov", "so'rov"],
    "jadval": ["table", "database", "baza", "schema", "column"],
    "query": ["sql", "database", "orm", "sorov", "so'rov"],
    "sorov": ["query", "sql", "database"],

    # Memory & State & Cache & Checkpoints
    "memory": ["xotira", "cache", "kesh", "store", "persist", "checkpoint", "sqlite", "state"],
    "xotira": ["memory", "cache", "kesh", "store", "persist", "saqlash", "checkpoint", "sqlite", "yodda", "state"],
    "xotirani": ["memory", "cache", "kesh", "store", "persist", "saqlash", "xotira", "sqlite"],
    "kesh": ["cache", "memory", "speed", "tezlik", "latency"],
    "cache": ["kesh", "memory", "speed", "latency", "optimization"],
    "store": ["memory", "storage", "baza", "persist", "saqlash"],
    "persist": ["memory", "store", "saqlash", "sqlite", "checkpoint"],
    "checkpoint": ["continuity", "state", "restore", "resume", "tiklash", "memory"],

    # Subtitles & Timing & Media
    "subtitle": ["subtitr", "vtt", "srt", "caption", "timing", "sync", "offset", "scrubber", "titr"],
    "subtitles": ["subtitle", "subtitr", "vtt", "srt", "caption"],
    "subtitr": ["subtitle", "vtt", "srt", "caption", "timing", "sync", "vaqt", "titr", "transcription", "audio", "video"],
    "subtitrlar": ["subtitle", "subtitles", "vtt", "srt", "caption", "subtitr"],
    "titr": ["subtitle", "subtitr", "caption", "srt", "vtt"],
    "caption": ["subtitle", "subtitr", "srt", "vtt"],
    "srt": ["subtitle", "subtitr", "vtt", "timing", "caption"],
    "vtt": ["subtitle", "subtitr", "srt", "timing", "caption"],
    "timing": ["vaqt", "sync", "offset", "delay", "timestamp", "duration"],
    "vaqt": ["time", "timing", "sync", "offset", "timestamp"],
    "sync": ["timing", "offset", "alignment", "vaqt", "sinxron"],

    # Performance & Speed & Optimization
    "speed": ["performance", "latency", "cache", "slow", "tezlik", "optimization"],
    "slow": ["performance", "latency", "bottleneck", "optimization", "sekin", "kechikish"],
    "tezlik": ["speed", "performance", "latency", "kechikish", "cache", "optimization", "samaradorlik", "tez"],
    "kechikish": ["latency", "delay", "slow", "tezlik", "performance"],
    "latency": ["speed", "tezlik", "kechikish", "slow", "performance"],
    "performance": ["speed", "tezlik", "latency", "cache", "optimization"],

    # UI & UX & Design & Color
    "css": ["ui", "design", "style", "layout", "theme", "rang"],
    "frontend": ["ui", "design", "component", "react", "html"],
    "ui": ["design", "frontend", "layout", "contrast", "dizayn", "interfeys"],
    "ux": ["design", "ui", "usability", "dizayn", "ergonomics"],
    "design": ["dizayn", "ui", "ux", "style", "css", "layout", "contrast", "palette"],
    "dizayn": ["design", "ui", "ux", "style", "css", "color", "palette", "rang", "interfeys"],
    "rang": ["color", "palette", "contrast", "design", "dizayn", "style", "theme"],
    "ranglar": ["color", "colors", "palette", "dizayn", "design"],
    "interfeys": ["ui", "interface", "design", "dizayn", "frontend"],

    # Errors & Defects & Remedies & Vaccines
    "error": ["defect", "bug", "exception", "failure", "xato", "muammo"],
    "defect": ["error", "bug", "flaw", "issue", "xato", "muammo"],
    "xato": ["error", "defect", "bug", "exception", "muammo", "kamchilik", "failure"],
    "muammo": ["problem", "issue", "defect", "bug", "xato", "nosozlik"],
    "bug": ["error", "defect", "issue", "xato"],
    "vaccine": ["vaksina", "immunity", "guardrail", "rule", "healed", "defect"],
    "vaksina": ["vaccine", "immunity", "guardrail", "rule", "davolash", "healer"],
    "typeerror": ["type", "typeguard", "runtime", "none", "null", "guard"],
    "keyerror": ["dictionary", "dict", "lookup", "get", "fallback", "runtime"],
    "zerodivision": ["math", "division", "zero", "guard", "runtime"],

    # Testing & Verification
    "test": ["sinov", "pytest", "audit", "verification", "assertion", "coverage", "tekshirish"],
    "sinov": ["test", "pytest", "audit", "tekshiruv"],
    "tekshirish": ["verification", "audit", "test", "check", "inspect"]
}


class LearningMemory:
    """
    Persistent learning memory manager for Hallwright AI coding assistants.
    Supports JSON persistence, SQLite WAL caching, and automated immune system syncing.
    """

    def __init__(self, memory_path: Optional[str] = None, workspace_root: Optional[str] = None):
        if memory_path:
            self.memory_path = memory_path
        elif workspace_root:
            self.memory_path = os.path.join(workspace_root, ".hallwright", "memory.json")
        else:
            self.memory_path = DEFAULT_MEMORY_PATH
        self._ensure_storage()
        db_dir = os.path.dirname(self.memory_path) or ".hallwright"
        self.db_path = os.path.join(db_dir, "memory.db")
        if SqliteMemoryStore:
            self.store = SqliteMemoryStore(db_path=self.db_path)
            if os.path.exists(self.memory_path):
                self.store.sync_from_json(self.memory_path)
        else:
            self.store = None

    def _ensure_storage(self) -> None:
        """Ensures that the memory directory and json file exist with valid schema."""
        dir_name = os.path.dirname(self.memory_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        if not os.path.exists(self.memory_path):
            initial_data = {
                "version": "2.0.0",
                "project": "Hallwright Engineering Core",
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
                "scarTissue": [
                    {
                        "id": "scar-001",
                        "category": "auth",
                        "pattern": "plain password comparison",
                        "lesson": "Never use plain password equality or plaintext storage; always use constant-time comparison and bcrypt/argon2id hashing.",
                        "severity": "critical"
                    },
                    {
                        "id": "scar-002",
                        "category": "payment",
                        "pattern": "non-idempotent payment charge",
                        "lesson": "Always require and verify idempotency keys on payment transactions to prevent double charges.",
                        "severity": "critical"
                    },
                    {
                        "id": "scar-003",
                        "category": "database",
                        "pattern": "unindexed foreign key joins / N+1 loops",
                        "lesson": "Always batch queries and ensure index coverage on foreign keys to prevent table scans and N+1 query cascades.",
                        "severity": "high"
                    }
                ],
                "mistakes": [],
                "successes": [],
                "conventions": [
                    {
                        "id": "conv-001",
                        "category": "quality",
                        "rule": "100% test pass rate and pre-commit gatekeeper 100/100 score required before commit."
                    }
                ],
                "anti_patterns": [
                    {
                        "id": "anti-001",
                        "pattern": "bare exception suppression / empty catch",
                        "reason": "Silently swallows catastrophic exceptions, making bugs impossible to debug."
                    }
                ],
                "lessons": []
            }
            self._write_atomic(initial_data)

    def load_data(self) -> Dict[str, Any]:
        """Loads memory data safely from JSON."""
        if not os.path.exists(self.memory_path):
            self._ensure_storage()

        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure essential keys exist
                for key in ["scarTissue", "mistakes", "successes", "conventions", "anti_patterns", "lessons"]:
                    if key not in data:
                        data[key] = []
                return data
        except (json.JSONDecodeError, OSError) as load_err:
            logger.debug("Memory json load fallback: %s", load_err)
            return {
                "version": "2.0.0",
                "scarTissue": [],
                "mistakes": [],
                "successes": [],
                "conventions": [],
                "anti_patterns": [],
                "lessons": []
            }

    def _write_atomic(self, data: Dict[str, Any]) -> None:
        """Writes JSON data atomically to prevent corruption."""
        dir_name = os.path.dirname(self.memory_path) or "."
        fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="hallwright_mem_", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, self.memory_path)
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError as cleanup_err:
                    import logging
                    logging.debug("Failed to remove temp memory file: %s", cleanup_err)
            raise

    def sync_with_immune_system(self, immune_path: Optional[str] = None) -> int:
        """Dynamically ingests evolved vaccines from immune_system.json into SQLite and memory."""
        if immune_path is None:
            dir_name = os.path.dirname(self.memory_path) or ".hallwright"
            immune_path = os.path.join(dir_name, "immune_system.json")
        if not os.path.exists(immune_path):
            return 0
        try:
            with open(immune_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as sync_err:
            logger.debug("Failed reading immune system for sync: %s", sync_err)
            return 0

        imported = 0
        vaccines = data.get("vaccines", [])
        for v in vaccines:
            vid = v.get("id") or f"vac-{imported+1:03d}"
            cat = v.get("category", "runtime")
            pat = v.get("error_signature", "")
            sol = v.get("web_solution", "")
            rule = v.get("guardrail_rule", "INVARIANT")
            lesson = f"{sol} [Invariant: {rule}]" if sol else rule
            if pat and lesson and self.store:
                self.store.record_lesson(
                    lesson_id=vid,
                    category=cat,
                    pattern=pat,
                    lesson=lesson,
                    auditor="ImmuneSystem",
                    severity="CRITICAL"
                )
                imported += 1
        return imported

    def get_lessons(self, task: str = "", category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves relevant lessons, mistakes, scar tissue, and active immune vaccines matching the task or category.
        Employs multilingual stemming, BM25-like weighting, and fuzzy token matching.
        """
        data = self.load_data()
        all_items: List[Dict[str, Any]] = []

        # Combine items from scarTissue, mistakes, lessons, and anti_patterns
        for item in data.get("scarTissue", []):
            all_items.append({**item, "source": "scarTissue"})
        for item in data.get("mistakes", []):
            all_items.append({**item, "source": "mistake"})
        for item in data.get("lessons", []):
            all_items.append({**item, "source": "lesson"})
        for item in data.get("anti_patterns", []):
            all_items.append({
                "id": item.get("id"),
                "category": item.get("category", "code"),
                "pattern": item.get("pattern", ""),
                "lesson": f"Avoid anti-pattern: {item.get('pattern')}. {item.get('reason', '')}",
                "severity": "high",
                "source": "anti_pattern"
            })

        # Dynamically load active evolved vaccines from immune_system.json
        dir_name = os.path.dirname(self.memory_path) or ".hallwright"
        immune_path = os.path.join(dir_name, "immune_system.json")
        if os.path.exists(immune_path):
            try:
                with open(immune_path, "r", encoding="utf-8") as f:
                    imm_data = json.load(f)
                for v in imm_data.get("vaccines", []):
                    sol = v.get("web_solution", "")
                    rule = v.get("guardrail_rule", "INVARIANT")
                    all_items.append({
                        "id": v.get("id"),
                        "category": v.get("category", "runtime"),
                        "pattern": v.get("error_signature", ""),
                        "lesson": f"{sol} [Invariant: {rule}]" if sol else rule,
                        "severity": "critical",
                        "generation": v.get("generation", 1),
                        "source": "vaccine"
                    })
            except (json.JSONDecodeError, OSError) as imm_err:
                logger.debug("Immune system ledger skipped or empty: %s", imm_err)

        if not task and not category:
            # Sort with priority to critical items and vaccines
            all_items.sort(key=lambda x: (
                1 if x.get("source") == "vaccine" else 0,
                1 if (x.get("severity") or "").lower() == "critical" else 0
            ), reverse=True)
            return all_items[:limit]

        clean_task = (task or "").lower().strip()
        raw_tokens = set(re.findall(r"\b[a-z0-9_\-\.]{2,}\b", clean_task))
        task_tokens = set(raw_tokens)
        for t in list(raw_tokens):
            norm_t = normalize_token(t)
            task_tokens.add(norm_t)
            if t in SYNONYM_MAP:
                task_tokens.update(SYNONYM_MAP[t])
            if norm_t in SYNONYM_MAP:
                task_tokens.update(SYNONYM_MAP[norm_t])

        scored_items = []

        for item in all_items:
            score = 0.0
            item_cat = (item.get("category") or "").lower()
            item_pattern = (item.get("pattern") or "").lower()
            item_lesson = (item.get("lesson") or "").lower()

            # Category filter/boost
            if category:
                if category.lower() in item_cat:
                    score += 5.0
                else:
                    continue  # Strict category filter if specified

            # Full phrase matching boost
            if clean_task and len(clean_task) >= 3:
                if clean_task in item_pattern:
                    score += 6.0
                elif clean_task in item_lesson:
                    score += 4.5
                elif clean_task in item_cat:
                    score += 5.0

            # Token overlap & Stem matching
            for token in task_tokens:
                tok_norm = normalize_token(token)
                # Category match
                if token in item_cat:
                    score += 3.5
                elif tok_norm in item_cat:
                    score += 2.5

                # Pattern match
                if token in item_pattern:
                    score += 3.0
                elif tok_norm in item_pattern:
                    score += 2.0

                # Lesson match
                if token in item_lesson:
                    score += 2.0
                elif tok_norm in item_lesson:
                    score += 1.2

            # Severity boost
            sev = (item.get("severity") or "").lower()
            if sev == "critical":
                score += 2.5
            elif sev == "high":
                score += 1.2

            # Source boost
            src = item.get("source", "")
            if src == "vaccine":
                score += 2.5
            elif src == "scarTissue":
                score += 1.5

            if score > 0:
                scored_items.append((score, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)
        deduped = []
        seen = set()
        for _, itm in scored_items:
            key = (itm.get("category", ""), itm.get("pattern", "")[:60])
            if key not in seen:
                seen.add(key)
                deduped.append(itm)
                if len(deduped) >= limit:
                    break
        return deduped

    def record_learning(
        self,
        record_type: str,
        category: str,
        pattern: str,
        lesson: str,
        severity: str = "high"
    ) -> Dict[str, Any]:
        """
        Records a new learning experience into memory.json and SQLite.
        record_type: 'mistake' | 'success' | 'convention' | 'anti_pattern' | 'lesson' | 'rule' | 'vaccine'
        """
        data = self.load_data()
        now_iso = datetime.now(timezone.utc).isoformat()
        clean_type = record_type.lower().strip()
        cat_clean = category.lower().strip()

        # Mapping to target array
        target_map = {
            "mistake": "mistakes",
            "success": "successes",
            "convention": "conventions",
            "anti_pattern": "anti_patterns",
            "lesson": "lessons",
            "scartissue": "scarTissue",
            "rule": "scarTissue",
            "vaccine": "scarTissue"
        }
        target_key = target_map.get(clean_type, "lessons")
        records = data.setdefault(target_key, [])

        # Check for duplicate by pattern and category
        for existing in records:
            if existing.get("category") == cat_clean and existing.get("pattern") == pattern:
                existing["lesson"] = lesson
                existing["severity"] = severity
                existing["updatedAt"] = now_iso
                data["lastUpdated"] = now_iso
                self._write_atomic(data)
                if self.store:
                    existing_id = existing.get("id") or f"lsn_{int(datetime.now(timezone.utc).timestamp()*1000)}"
                    if clean_type == "convention":
                        self.store.record_convention(existing_id, cat_clean, lesson)
                    else:
                        self.store.record_lesson(existing_id, cat_clean, pattern, lesson, severity=severity)
                return {
                    "status": "updated",
                    "id": existing.get("id"),
                    "category": cat_clean,
                    "target": target_key
                }

        # Generate unique ID
        rec_id = f"{clean_type[:3]}-{len(records) + 1:04d}"
        new_entry = {
            "id": rec_id,
            "category": cat_clean,
            "pattern": pattern,
            "lesson": lesson,
            "severity": severity,
            "recordedAt": now_iso
        }
        records.append(new_entry)
        data["lastUpdated"] = now_iso
        self._write_atomic(data)
        if self.store:
            if clean_type == "convention":
                self.store.record_convention(rec_id, cat_clean, lesson)
            else:
                self.store.record_lesson(rec_id, cat_clean, pattern, lesson, severity=severity)

        return {
            "status": "recorded",
            "id": rec_id,
            "category": cat_clean,
            "target": target_key,
            "total_records": len(records)
        }

    def format_warning_snippet(self, task: str) -> str:
        """
        Returns a ready-to-inject warning markdown block based on matching lessons and active immunity.
        """
        lessons = self.get_lessons(task=task, limit=4)
        if not lessons:
            return ""

        lines = ["## ⚠️ PAST LESSONS & SCAR TISSUE (DO NOT REPEAT):"]
        for item in lessons:
            cat = item.get("category", "code").upper()
            lesson = item.get("lesson", "")
            src = item.get("source", "")
            badge = " [VACCINE]" if src == "vaccine" else ""
            lines.append(f"- **[{cat}{badge}]**: {lesson}")
        return "\n".join(lines)
