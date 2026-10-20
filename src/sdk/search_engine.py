"""
Hallwright High-Performance Multi-Index Search Engine
Empowered by The Council of Masters & Domain Guilds.

Provides unified, lightning-fast semantic and pattern search across:
1. The Council of Masters (64 Titans + 8 Guilds)
2. Project Memory & Scar Tissue (.hallwright/memory.json, SQLite WAL)
3. Enterprise Domain Libraries & Modules (src/libraries/)
4. PDK Plugins & Autonomous Subagents (.agents/)
5. Local Codebase & AST Patterns (Multi-language source tree)
6. Live Web & Technical Documentation Search (DuckDuckGo Realtime)
"""

import os
import re
import json
import logging
import html
import urllib.request
import urllib.parse
from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("hallwright.search")


class SearchScope(str, Enum):
    ALL = "all"
    COUNCIL = "council"
    MEMORY = "memory"
    CODE = "code"
    LIBRARIES = "libraries"
    PLUGINS = "plugins"
    WEB = "web"


@dataclass
class SearchHit:
    category: str
    title: str
    score: float
    snippet: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "title": self.title,
            "score": round(self.score, 1),
            "snippet": self.snippet,
            "metadata": self.metadata,
        }


@dataclass
class SearchResultSet:
    query: str
    scope: str
    total_hits: int
    hits: List[SearchHit] = field(default_factory=list)
    by_category: Dict[str, List[SearchHit]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "scope": self.scope,
            "total_hits": self.total_hits,
            "by_category": {
                cat: [h.to_dict() for h in hits_list]
                for cat, hits_list in self.by_category.items()
            },
            "hits": [h.to_dict() for h in self.hits],
        }

    def format_terminal(self) -> str:
        lines = []
        lines.append("=" * 80)
        lines.append(f"  🔍 HALLWRIGHT UNIFIED SEARCH ENGINE")
        lines.append(f"     Query: '{self.query}' | Scope: {self.scope} | Total Hits: {self.total_hits}")
        lines.append("=" * 80)

        if not self.hits:
            lines.append("\n  ℹ️  No matching records found across specified index scopes.")
            lines.append("     Try broader search terms (e.g., 'auth', 'database', 'css', 'perf').\n")
            return "\n".join(lines)

        category_labels = {
            "council": ("🏛️", "THE COUNCIL OF MASTERS & GUILDS"),
            "libraries": ("📦", "ENTERPRISE DOMAIN LIBRARIES"),
            "memory": ("🧠", "PROJECT MEMORY & SCAR TISSUE"),
            "plugins": ("🔌", "PDK PLUGINS & SUBAGENTS"),
            "code": ("💻", "WORKSPACE CODEBASE MATCHES"),
            "web": ("🌐", "LIVE WEB SEARCH & DOCUMENTATION"),
        }

        for cat, (icon, label) in category_labels.items():
            cat_hits = self.by_category.get(cat, [])
            if not cat_hits:
                continue

            lines.append(f"\n{icon}  {label} ({len(cat_hits)} hits):")
            lines.append("─" * 80)
            for hit in cat_hits:
                score_badge = f"[{hit.score:.0f} pts]"
                lines.append(f"  • {hit.title:<45} {score_badge:>32}")
                if hit.snippet:
                    for sline in hit.snippet.strip().split("\n")[:3]:
                        lines.append(f"    │ {sline}")
                if "path" in hit.metadata:
                    loc = hit.metadata["path"]
                    if "line" in hit.metadata:
                        loc += f":{hit.metadata['line']}"
                    lines.append(f"    └─ Location: {loc}")

        lines.append("\n" + "=" * 80 + "\n")
        return "\n".join(lines)


class SearchEngine:
    """High-speed multi-index search engine for the Hallwright ecosystem."""

    CODE_EXTENSIONS = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".scss",
        ".json", ".md", ".go", ".rs", ".sql", ".sh", ".ps1", ".yaml", ".yml", ".toml"
    }

    IGNORE_DIRS = {
        ".git", "node_modules", "venv", ".venv", "__pycache__", ".pytest_cache",
        "dist", "build", "target", "bin", ".idea", ".vscode", ".hallwright/screenshots"
    }

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = os.path.abspath(workspace_root or os.getcwd())

    def search(self, query: str, scope: str = "all", limit: int = 5) -> SearchResultSet:
        clean_query = (query or "").strip()
        if not clean_query:
            return SearchResultSet(query="", scope=scope, total_hits=0)

        scope_lower = scope.lower()
        all_hits: List[SearchHit] = []
        by_cat: Dict[str, List[SearchHit]] = {}

        # 1. Council of Masters & Guilds
        if scope_lower in ("all", "council"):
            council_hits = self.search_council(clean_query, limit=limit)
            if council_hits:
                by_cat["council"] = council_hits
                all_hits.extend(council_hits)

        # 2. Enterprise Domain Libraries
        if scope_lower in ("all", "libraries", "lib"):
            lib_hits = self.search_libraries(clean_query, limit=limit)
            if lib_hits:
                by_cat["libraries"] = lib_hits
                all_hits.extend(lib_hits)

        # 3. Project Memory & Scar Tissue
        if scope_lower in ("all", "memory", "lessons"):
            mem_hits = self.search_memory(clean_query, limit=limit)
            if mem_hits:
                by_cat["memory"] = mem_hits
                all_hits.extend(mem_hits)

        # 4. Plugins & Subagents
        if scope_lower in ("all", "plugins", "agents"):
            plugin_hits = self.search_plugins(clean_query, limit=limit)
            if plugin_hits:
                by_cat["plugins"] = plugin_hits
                all_hits.extend(plugin_hits)

        # 5. Local Codebase Search
        if scope_lower in ("all", "code", "codebase"):
            code_hits = self.search_code(clean_query, limit=limit)
            if code_hits:
                by_cat["code"] = code_hits
                all_hits.extend(code_hits)

        # 6. Live Web Search (DuckDuckGo Realtime)
        if scope_lower in ("all", "web", "internet"):
            web_hits = self.search_web(clean_query, limit=limit)
            if web_hits:
                by_cat["web"] = web_hits
                all_hits.extend(web_hits)

        # Global ranking by score descending
        all_hits.sort(key=lambda h: h.score, reverse=True)

        return SearchResultSet(
            query=clean_query,
            scope=scope,
            total_hits=len(all_hits),
            hits=all_hits,
            by_category=by_cat,
        )

    def search_council(self, query: str, limit: int = 5) -> List[SearchHit]:
        hits: List[SearchHit] = []
        tokens = [t.lower() for t in re.split(r"\s+", query) if len(t) > 1]
        if not tokens:
            tokens = [query.lower()]

        # Lazy load council members and keywords
        council_members: Dict[str, Any] = {}
        keyword_map: Dict[str, List[str]] = {}
        try:
            from craftsman import COUNCIL_MEMBERS
            council_members = COUNCIL_MEMBERS
        except ImportError:
            try:
                from cli.dashboard import COUNCIL_MEMBERS as DASH_COUNCIL
                council_members = {
                    item[0].lower().replace(" ", "_"): {
                        "name": item[0],
                        "badge": item[1],
                        "archetype": item[2],
                        "motto": item[3],
                    }
                    for item in DASH_COUNCIL
                }
            except ImportError:
                council_members = {}

        try:
            from context_selector import MASTER_KEYWORD_MAP
            keyword_map = MASTER_KEYWORD_MAP
        except ImportError:
            try:
                from src.sdk.context_selector import MASTER_KEYWORD_MAP
                keyword_map = MASTER_KEYWORD_MAP
            except ImportError:
                keyword_map = {}

        # Scan council members
        for key, data in council_members.items():
            name = data.get("name", key)
            archetype = data.get("archetype", "")
            motto = data.get("motto", "")
            badge = data.get("badge", "")
            criteria = " ".join(data.get("criteria", []))
            pledge = data.get("pledge", "")
            k_words = " ".join(keyword_map.get(key, []))

            full_text = f"{name} {archetype} {motto} {badge} {criteria} {pledge} {k_words}".lower()

            score = 0.0
            # Exact query match
            if query.lower() in full_text:
                score += 50.0
            if query.lower() in name.lower():
                score += 40.0
            if query.lower() in badge.lower() or query.lower() in archetype.lower():
                score += 30.0
            if query.lower() in k_words.lower():
                score += 35.0

            # Token overlap
            matched_tokens = sum(1 for t in tokens if t in full_text)
            score += (matched_tokens / len(tokens)) * 30.0

            if score > 20.0:
                snippet = f"{archetype} | {badge}\n\"{motto}\""
                hits.append(SearchHit(
                    category="council",
                    title=name,
                    score=min(100.0, score),
                    snippet=snippet,
                    metadata={"key": key, "badge": badge, "type": "Council Titan"}
                ))

        # Also scan Council Guilds
        try:
            from guilds import COUNCIL_GUILDS
            for g in COUNCIL_GUILDS:
                g_text = f"{g.name} {g.lead_name} {g.focus_area} {' '.join(g.members)}".lower()
                g_score = 0.0
                if query.lower() in g_text:
                    g_score += 45.0
                matched_tokens = sum(1 for t in tokens if t in g_text)
                g_score += (matched_tokens / len(tokens)) * 35.0

                if g_score > 25.0:
                    hits.append(SearchHit(
                        category="council",
                        title=f"Guild: {g.name} (Lead: {g.lead_name})",
                        score=min(100.0, g_score),
                        snippet=f"Focus: {g.focus_area}\nSquad Members: {', '.join(g.members[:4])}...",
                        metadata={"guild_id": g.guild_id, "lead": g.lead_name, "type": "Council Guild"}
                    ))
        except (ImportError, AttributeError) as exc:
            logger.debug("Guilds module unavailable or failed to load: %s", exc)

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]

    def search_libraries(self, query: str, limit: int = 5) -> List[SearchHit]:
        hits: List[SearchHit] = []
        tokens = [t.lower() for t in re.split(r"\s+", query) if len(t) > 1]
        if not tokens:
            tokens = [query.lower()]

        try:
            from registry import DOMAIN_REGISTRY
        except ImportError:
            try:
                from src.libraries.registry import DOMAIN_REGISTRY
            except ImportError:
                DOMAIN_REGISTRY = {}

        for domain_key, domain_data in DOMAIN_REGISTRY.items():
            d_title = domain_data.get("title", domain_key)
            d_desc = domain_data.get("description", "")
            d_text = f"{domain_key} {d_title} {d_desc}".lower()

            # Check domain level
            domain_score = 0.0
            if query.lower() in d_text:
                domain_score += 35.0

            # Scan modules inside domain
            for mod in domain_data.get("modules", []):
                m_name = mod.get("name", "")
                m_class = mod.get("class", "")
                m_purpose = mod.get("purpose", "")
                m_text = f"{m_name} {m_class} {m_purpose} {domain_key}".lower()

                m_score = domain_score
                if query.lower() in m_text:
                    m_score += 40.0
                if query.lower() in m_name.lower() or query.lower() in m_class.lower():
                    m_score += 30.0

                matched_tokens = sum(1 for t in tokens if t in m_text)
                m_score += (matched_tokens / len(tokens)) * 25.0

                if m_score > 20.0:
                    mod_path = f"src/libraries/{domain_key}/{m_name}"
                    snippet = f"Class: {m_class} | {m_purpose}\nDomain: {d_title}"
                    hits.append(SearchHit(
                        category="libraries",
                        title=f"{domain_key.capitalize()}: {m_class} ({m_name})",
                        score=min(100.0, m_score),
                        snippet=snippet,
                        metadata={"domain": domain_key, "module": m_name, "class": m_class, "path": mod_path}
                    ))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]

    def search_memory(self, query: str, limit: int = 5) -> List[SearchHit]:
        hits: List[SearchHit] = []
        tokens = [t.lower() for t in re.split(r"\s+", query) if len(t) > 1]
        if not tokens:
            tokens = [query.lower()]

        entries: List[Dict[str, Any]] = []

        # 1. Try sqlite memory
        sqlite_db = os.path.join(self.workspace_root, ".hallwright", "memory.db")
        if os.path.exists(sqlite_db):
            try:
                import sqlite3
                conn = sqlite3.connect(sqlite_db, timeout=2.0)
                cursor = conn.cursor()
                cursor.execute("SELECT type, category, pattern, lesson, severity, tags FROM learning_records")
                for row in cursor.fetchall():
                    entries.append({
                        "type": row[0],
                        "category": row[1],
                        "pattern": row[2],
                        "lesson": row[3],
                        "severity": row[4],
                        "tags": row[5] or ""
                    })
                conn.close()
            except Exception as exc:
                logger.debug("SQLite memory query failed: %s", exc)

        # 2. Try JSON memory if sqlite yielded nothing or as complement
        if not entries:
            json_file = os.path.join(self.workspace_root, ".hallwright", "memory.json")
            if os.path.exists(json_file):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        mem_data = json.load(f)
                        for section in ("mistakes", "conventions", "lessons", "anti_patterns"):
                            for item in mem_data.get(section, []):
                                if isinstance(item, dict):
                                    item["type"] = section
                                    entries.append(item)
                except Exception as exc:
                    logger.debug("JSON memory query failed: %s", exc)

        for entry in entries:
            pattern = entry.get("pattern", "")
            lesson = entry.get("lesson", "")
            cat = entry.get("category", "general")
            sev = entry.get("severity", "medium")
            tags = entry.get("tags", "")

            full_text = f"{pattern} {lesson} {cat} {tags}".lower()
            score = 0.0

            if query.lower() in full_text:
                score += 45.0
            matched_tokens = sum(1 for t in tokens if t in full_text)
            score += (matched_tokens / len(tokens)) * 35.0

            # Severity boost
            if sev == "critical":
                score += 15.0
            elif sev == "high":
                score += 10.0

            if score > 20.0:
                title = f"[{sev.upper()}] {pattern[:50]}..." if len(pattern) > 50 else f"[{sev.upper()}] {pattern}"
                snippet = f"Lesson: {lesson}\nCategory: {cat} | Severity: {sev}"
                hits.append(SearchHit(
                    category="memory",
                    title=title,
                    score=min(100.0, score),
                    snippet=snippet,
                    metadata={"category": cat, "severity": sev, "type": entry.get("type", "lesson")}
                ))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]

    def search_plugins(self, query: str, limit: int = 5) -> List[SearchHit]:
        hits: List[SearchHit] = []
        tokens = [t.lower() for t in re.split(r"\s+", query) if len(t) > 1]
        if not tokens:
            tokens = [query.lower()]

        plugins_dir = os.path.join(self.workspace_root, ".agents", "plugins")
        if not os.path.isdir(plugins_dir):
            return hits

        for p_name in os.listdir(plugins_dir):
            p_path = os.path.join(plugins_dir, p_name)
            if not os.path.isdir(p_path):
                continue

            manifest_file = os.path.join(p_path, "plugin.json")
            name = p_name
            desc = ""
            if os.path.exists(manifest_file):
                try:
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        name = data.get("name", p_name)
                        desc = data.get("description", "")
                except Exception as exc:
                    logger.debug("Plugin manifest read error for %s: %s", p_name, exc)

            full_text = f"{name} {desc} {p_name}".lower()
            score = 0.0
            if query.lower() in full_text:
                score += 50.0
            matched_tokens = sum(1 for t in tokens if t in full_text)
            score += (matched_tokens / len(tokens)) * 30.0

            if score > 20.0:
                hits.append(SearchHit(
                    category="plugins",
                    title=f"Plugin: {name}",
                    score=min(100.0, score),
                    snippet=desc or "Custom Craftsmanship Plugin",
                    metadata={"path": p_path, "plugin_name": name}
                ))

        # Also scan subagent definitions in .agents/agents/
        agents_dir = os.path.join(self.workspace_root, ".agents", "agents")
        if os.path.isdir(agents_dir):
            for a_file in os.listdir(agents_dir):
                if a_file.endswith(".md"):
                    a_name = a_file[:-3]
                    a_path = os.path.join(agents_dir, a_file)
                    try:
                        with open(a_path, "r", encoding="utf-8", errors="replace") as f:
                            a_content = f.read(1500)
                    except Exception as exc:
                        logger.debug("Agent doc read error for %s: %s", a_file, exc)
                        a_content = ""

                    full_text = f"{a_name} {a_content}".lower()
                    score = 0.0
                    if query.lower() in full_text:
                        score += 45.0
                    if query.lower() in a_name.lower():
                        score += 35.0
                    matched_tokens = sum(1 for t in tokens if t in full_text)
                    score += (matched_tokens / len(tokens)) * 25.0

                    if score > 25.0:
                        snippet_line = a_content.strip().split("\n")[0] if a_content else "Autonomous Craftsman Subagent"
                        hits.append(SearchHit(
                            category="plugins",
                            title=f"Subagent: {a_name}",
                            score=min(100.0, score),
                            snippet=snippet_line,
                            metadata={"path": a_path, "subagent": a_name}
                        ))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]

    def search_code(self, query: str, limit: int = 10, max_files: int = 300) -> List[SearchHit]:
        hits: List[SearchHit] = []
        safe_pattern = re.escape(query)
        try:
            regex = re.compile(safe_pattern, re.IGNORECASE)
        except re.error:
            return hits

        scanned = 0
        for root, dirs, files in os.walk(self.workspace_root):
            # Prune ignored directories in-place
            dirs[:] = [
                d for d in dirs
                if d not in self.IGNORE_DIRS and not d.startswith(".")
            ]

            for file_name in files:
                _, ext = os.path.splitext(file_name)
                if ext.lower() not in self.CODE_EXTENSIONS:
                    continue

                file_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(file_path, self.workspace_root).replace(os.sep, "/")

                # Exclude minified or bundled files
                if file_name.endswith(".min.js") or file_name.endswith(".bundle.js"):
                    continue

                scanned += 1
                if scanned > max_files:
                    break

                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()
                except (OSError, UnicodeDecodeError):
                    continue

                for line_idx, line in enumerate(lines, start=1):
                    if regex.search(line):
                        # Extract 3-line context
                        start_ctx = max(0, line_idx - 2)
                        end_ctx = min(len(lines), line_idx + 1)
                        context_snippet = "".join(lines[start_ctx:end_ctx]).strip()

                        # Scoring
                        score = 50.0
                        stripped = line.strip()
                        if stripped.startswith(("def ", "class ", "function ", "const ", "export ")):
                            score += 35.0  # Definition boost
                        if stripped.startswith(("#", "//", "/*", "*")):
                            score -= 10.0  # Comment penalty

                        hits.append(SearchHit(
                            category="code",
                            title=f"{rel_path}:{line_idx}",
                            score=min(100.0, max(10.0, score)),
                            snippet=context_snippet,
                            metadata={"path": rel_path, "line": line_idx, "file": file_name}
                        ))

                        if len(hits) >= limit * 2:
                            break

            if scanned > max_files or len(hits) >= limit * 2:
                break

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]

    def search_web(self, query: str, limit: int = 5, timeout: float = 4.0) -> List[SearchHit]:
        """Perform real-time web and technical documentation search via DuckDuckGo HTML endpoint.

        Features:
        - Zero third-party dependencies (pure Python standard library).
        - Automatic decoding of target URLs from redirect wrappers.
        - Clean HTML stripping and entity unescaping.
        - Resilient network error handling (never crashes or blocks on offline/timeout).
        """
        clean_q = (query or "").strip()
        if not clean_q:
            return []

        hits: List[SearchHit] = []
        encoded_query = urllib.parse.quote_plus(clean_q)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                content = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            logger.debug("Live web search unavailable or timed out for %r: %s", clean_q, exc)
            return hits

        title_matches = re.findall(
            r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            content,
            re.DOTALL
        )
        snippet_matches = re.findall(
            r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
            content,
            re.DOTALL
        )

        for idx, (raw_href, raw_title) in enumerate(title_matches[:limit]):
            clean_title = html.unescape(re.sub(r'<[^>]+>', '', raw_title)).strip()
            if not clean_title:
                continue

            raw_snippet = snippet_matches[idx] if idx < len(snippet_matches) else ""
            clean_snippet = html.unescape(re.sub(r'<[^>]+>', '', raw_snippet)).strip()

            # Decode target destination from DDG redirect url
            final_url = raw_href
            if "uddg=" in raw_href:
                try:
                    parsed = urllib.parse.urlparse(raw_href)
                    qs = urllib.parse.parse_qs(parsed.query)
                    if "uddg" in qs and qs["uddg"]:
                        final_url = qs["uddg"][0]
                except Exception as parse_exc:
                    logger.debug("Failed to decode target url %r: %s", raw_href, parse_exc)

            # Score web results: top hit starts at 88.0, decaying slightly
            score = max(50.0, 88.0 - (idx * 3.0))

            hits.append(SearchHit(
                category="web",
                title=clean_title,
                score=score,
                snippet=clean_snippet,
                metadata={"url": final_url, "engine": "duckduckgo_live"}
            ))

        return hits

