"""Hallwright Enterprise Copywriting Library: Keep-A-Changelog Builder.

Constructs semantic, auditable changelogs conforming to the Keep-a-Changelog
and Semantic Versioning (SemVer) specifications.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import datetime


@dataclass
class VersionRelease:
    """Represents a discrete version release with categorized entries."""
    version: str
    date: str
    added: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    deprecated: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    fixed: List[str] = field(default_factory=list)
    security: List[str] = field(default_factory=list)


class ChangelogBuilder:
    """Enterprise Changelog document generator."""

    def __init__(self, project_name: str = "Project"):
        self.project_name = project_name
        self.releases: List[VersionRelease] = []

    def add_release(
        self,
        version: str,
        date_str: Optional[str] = None,
        added: Optional[List[str]] = None,
        changed: Optional[List[str]] = None,
        deprecated: Optional[List[str]] = None,
        removed: Optional[List[str]] = None,
        fixed: Optional[List[str]] = None,
        security: Optional[List[str]] = None,
    ) -> "ChangelogBuilder":
        """Record a new version release."""
        date_val = date_str or datetime.date.today().isoformat()
        rel = VersionRelease(
            version=version,
            date=date_val,
            added=list(added or []),
            changed=list(changed or []),
            deprecated=list(deprecated or []),
            removed=list(removed or []),
            fixed=list(fixed or []),
            security=list(security or []),
        )
        self.releases.append(rel)
        return self

    def render_markdown(self) -> str:
        """Render complete Keep-a-Changelog compliant markdown."""
        lines = [
            f"# Changelog: {self.project_name}",
            "",
            "All notable changes to this project will be documented in this file.",
            "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),",
            "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
            "",
        ]

        for rel in self.releases:
            lines.append(f"## [{rel.version}] - {rel.date}")
            lines.append("")

            categories = [
                ("Added", rel.added),
                ("Changed", rel.changed),
                ("Deprecated", rel.deprecated),
                ("Removed", rel.removed),
                ("Fixed", rel.fixed),
                ("Security", rel.security),
            ]

            for cat_name, items in categories:
                if items:
                    lines.append(f"### {cat_name}")
                    for it in items:
                        lines.append(f"- {it}")
                    lines.append("")

        return "\n".join(lines)
