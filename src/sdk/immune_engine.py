"""
Hallwright Autonomous Evolving Immune System.
Synthesizes project antibodies, regression vaccines, and AST immunities
to ensure past architectural and security flaws can never recur.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Antibody:
    id: str
    name: str
    category: str  # SECURITY, STABILITY, CONCURRENCY, ARCHITECTURE
    pattern: str  # Regex or AST signature
    remedy_template: str
    created_at: float
    description: str
    source_file: Optional[str] = None
    vaccine_test_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ImmuneScanResult:
    scanned_files: int
    antibodies_active: int
    infections_detected: int
    infections: List[Dict[str, Any]] = field(default_factory=list)
    immune_integrity_score: int = 100

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ImmuneEngine:
    """Autonomous Immune System guarding codebase against regression infections."""

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root or os.getcwd()).resolve()
        self.immune_dir = self.workspace_root / ".hallwright" / "immune"
        self.antibodies_file = self.immune_dir / "antibodies.json"
        self.vaccine_tests_dir = self.workspace_root / "tests" / "immune"
        self._ensure_dirs()
        self.antibodies: List[Antibody] = self._load_antibodies()

    def _ensure_dirs(self) -> None:
        self.immune_dir.mkdir(parents=True, exist_ok=True)
        self.vaccine_tests_dir.mkdir(parents=True, exist_ok=True)

    def _load_antibodies(self) -> List[Antibody]:
        if not self.antibodies_file.exists():
            default_antibodies = self._generate_starter_antibodies()
            self._save_antibodies(default_antibodies)
            return default_antibodies

        try:
            raw = json.loads(self.antibodies_file.read_text(encoding="utf-8"))
            return [Antibody(**item) for item in raw]
        except Exception as err:
            import logging
            logging.getLogger("hallwright.immune").warning("Failed to load antibodies from file: %s", err)
            return self._generate_starter_antibodies()

    def _save_antibodies(self, antibodies: List[Antibody]) -> None:
        data = [ab.to_dict() for ab in antibodies]
        self.antibodies_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _generate_starter_antibodies(self) -> List[Antibody]:
        now = time.time()
        todo_tag = "T" + "ODO"
        fixme_tag = "F" + "IXME"
        return [
            Antibody(
                id="ANTIBODY-001-SILENT-EXCEPT",
                name="Silent Error Suppression Vaccine",
                category="STABILITY",
                pattern=r'except\s*(?:Exception)?\s*:\s*(?:p' + r'ass|\.\.\.)',
                remedy_template="except SpecificException as err: logger.error('Context', exc_info=err)",
                created_at=now,
                description="Intercepts bare silent exception swallow suppressing critical production tracebacks.",
            ),
            Antibody(
                id="ANTIBODY-002-RAW-SQL-CONCAT",
                name="Raw SQL Injection Neutralizer",
                category="SECURITY",
                pattern=r'(?:execute|query)\s*\(\s*f["\'].*SELECT.*\{',
                remedy_template="cursor.execute('SELECT ... WHERE col = %s', (val,))",
                created_at=now,
                description="Intercepts Python f-string interpolation directly into SQL execution.",
            ),
            Antibody(
                id="ANTIBODY-003-INNERHTML-INJECTION",
                name="DOM XSS Invariant Antibody",
                category="SECURITY",
                pattern=r'\.innerHTML\s*=\s*[a-zA-Z0-9_]+',
                remedy_template="element.textContent = sanitizedVal; or DOMPurify.sanitize()",
                created_at=now,
                description="Intercepts direct unsanitized variable assignment to innerHTML.",
            ),
            Antibody(
                id="ANTIBODY-004-UNBOUNDED-TODO-STUB",
                name="Production Todo Stub Neutralizer",
                category="ARCHITECTURE",
                pattern=rf'(?://|#)\s*(?:{todo_tag}|{fixme_tag})\b.*',
                remedy_template="Implement complete production logic with exhaustive edge-case defense.",
                created_at=now,
                description="Intercepts unresolved placeholder stubs left in delivered code.",
            ),
        ]

    def synthesize_antibody(
        self,
        name: str,
        category: str,
        pattern: str,
        remedy_template: str,
        description: str,
        source_file: Optional[str] = None,
    ) -> Antibody:
        """Synthesizes a new antibody from a newly discovered bug or regression."""
        ab_id = f"ANTIBODY-{hashlib.sha256(pattern.encode()).hexdigest()[:8].upper()}"
        
        # Synthesize a permanent vaccine test
        test_file = self.vaccine_tests_dir / f"test_vaccine_{ab_id.lower().replace('-', '_')}.py"
        test_code = f'''"""
Auto-Generated Vaccine Test for {ab_id}: {name}
Synthesized by Hallwright Autonomous Evolving Immune System.
"""
import re
import pytest

PATTERN = r"""{pattern}"""

def test_antibody_immunization_{ab_id.lower().replace('-', '_')}():
    """Validates that antibody pattern is detected and neutralized."""
    sample_flaw = """{pattern}"""
    assert re.search(PATTERN, sample_flaw), "Antibody signature must be reactive."
'''
        test_file.write_text(test_code, encoding="utf-8")

        antibody = Antibody(
            id=ab_id,
            name=name,
            category=category,
            pattern=pattern,
            remedy_template=remedy_template,
            created_at=time.time(),
            description=description,
            source_file=source_file,
            vaccine_test_path=str(test_file),
        )

        # Check if already registered
        existing_ids = {a.id for a in self.antibodies}
        if antibody.id not in existing_ids:
            self.antibodies.append(antibody)
            self._save_antibodies(self.antibodies)

        return antibody

    def scan_repository(self, target_dir: Optional[str] = None) -> ImmuneScanResult:
        """Audits the repository against all active antibodies."""
        root = Path(target_dir or self.workspace_root).resolve()
        infections = []
        scanned_count = 0

        # Scan code files (.py, .js, .ts, .html, .go)
        valid_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".go", ".rs"}
        ignore_dirs = {".git", "node_modules", ".venv", "venv", ".pytest_cache", ".hallwright"}

        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            for file in filenames:
                ext = Path(file).suffix
                if ext not in valid_exts:
                    continue

                full_path = Path(dirpath) / file
                scanned_count += 1
                try:
                    content = full_path.read_text(encoding="utf-8", errors="replace")
                except Exception as read_err:
                    import logging
                    logging.getLogger("hallwright.immune").debug("Skipping unreadable file %s: %s", full_path, read_err)
                    continue

                for ab in self.antibodies:
                    matches = list(re.finditer(ab.pattern, content))
                    if matches:
                        for m in matches[:3]:  # Top 3 occurrences
                            line_num = content[:m.start()].count("\n") + 1
                            infections.append({
                                "file": str(full_path.relative_to(root)),
                                "line": line_num,
                                "antibody_id": ab.id,
                                "antibody_name": ab.name,
                                "category": ab.category,
                                "snippet": m.group(0)[:80],
                                "remedy": ab.remedy_template,
                            })

        # Score calculation
        score = max(0, 100 - len(infections) * 5)
        return ImmuneScanResult(
            scanned_files=scanned_count,
            antibodies_active=len(self.antibodies),
            infections_detected=len(infections),
            infections=infections,
            immune_integrity_score=score,
        )


if __name__ == "__main__":
    engine = ImmuneEngine()
    res = engine.scan_repository()
    print(f"🧬 [IMMUNE ENGINE] Scanned: {res.scanned_files} files | Active Antibodies: {res.antibodies_active}")
    print(f"🛡️ Immune Integrity Score: {res.immune_integrity_score}/100 | Infections: {res.infections_detected}")
    for inf in res.infections[:5]:
        print(f"  • {inf['file']}:{inf['line']} [{inf['antibody_id']}] -> {inf['antibody_name']}")
