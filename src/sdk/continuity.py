"""Hallwright Enterprise SDK: Universal Cross-Agent Continuity & Checkpoint Memory Engine.

Allows any connected AI agent (Cursor, Claude Code, GitHub Copilot, Antigravity,
Hermes, OpenCode, Codex, Aider) to instantly understand previous accomplishments,
the exact file and task where work stopped, and recommended next steps.

COMPLETELY OPTIONAL: Can be skipped via --no-continuity, ARTISAN_NO_CONTINUITY=1,
or configuration flag.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

try:
    from src.memory.store import SqliteMemoryStore
except ImportError:
    try:
        from memory.store import SqliteMemoryStore
    except ImportError:
        SqliteMemoryStore = None

logger = logging.getLogger("hallwright.continuity")


@dataclass
class CheckpointData:
    """Structured memory checkpoint capturing the exact state of work."""
    last_updated: float = field(default_factory=time.time)
    last_agent: str = "generic-agent"
    last_task: str = "Initial setup"
    stopped_at_file: Optional[str] = None
    stopped_at_line: Optional[int] = None
    completed_milestones: List[str] = field(default_factory=list)
    pending_milestones: List[str] = field(default_factory=list)
    architectural_decisions: List[str] = field(default_factory=list)
    context_notes: List[str] = field(default_factory=list)
    status: str = "IN_PROGRESS"  # IN_PROGRESS, PAUSED, COMPLETED


class ContinuityManager:
    """Cross-agent state persistence and handoff memory manager.

    Ensures that when a user switches between AI assistants, the incoming
    assistant seamlessly picks up from the exact file and state without
    re-investigating from scratch.
    """

    def __init__(self, workspace_root: str = ".", enabled: Optional[bool] = None):
        self.workspace_root = os.path.abspath(workspace_root)
        self.artisan_dir = os.path.join(self.workspace_root, ".hallwright")
        self.checkpoint_file = os.path.join(self.artisan_dir, "checkpoints.json")
        self.handoff_file = os.path.join(self.artisan_dir, "agent_handoff.md")

        self.db_path = os.path.join(self.artisan_dir, "memory.db")
        self.store = SqliteMemoryStore(self.db_path) if SqliteMemoryStore else None

        # Determine if enabled
        if enabled is not None:
            self._enabled = enabled
        else:
            env_val = (os.environ.get("HALLWRIGHT_NO_CONTINUITY") or os.environ.get("ARTISAN_NO_CONTINUITY", "")).lower()
            if env_val in ("1", "true", "yes"):
                self._enabled = False
            else:
                self._enabled = self._check_config_enabled()

    def _check_config_enabled(self) -> bool:
        """Check hallwright.config.json if continuity is explicitly disabled."""
        for cfg_name in ["hallwright.config.json"]:
            config_path = os.path.join(self.workspace_root, cfg_name)
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                        if isinstance(cfg, dict) and "continuity" in cfg:
                            cont = cfg["continuity"]
                            if isinstance(cont, dict):
                                return bool(cont.get("enabled", True))
                            elif isinstance(cont, bool):
                                return cont
                except (OSError, json.JSONDecodeError, KeyError) as err:
                    logger.debug("Failed reading config %s: %s", config_path, err)
        return True

    @property
    def is_enabled(self) -> bool:
        """Return whether continuity tracking is active."""
        return self._enabled

    def disable(self) -> None:
        """Dynamically disable continuity tracking for this session."""
        self._enabled = False

    def enable(self) -> None:
        """Dynamically enable continuity tracking for this session."""
        self._enabled = True

    def load_checkpoint(self) -> Optional[CheckpointData]:
        """Load current checkpoint data, returning None if disabled or non-existent."""
        if not self._enabled:
            return None

        if self.store:
            try:
                latest = self.store.get_latest_checkpoint()
                if latest:
                    extra = latest.get("extra_data", {})
                    return CheckpointData(
                        last_updated=latest.get("updated_at", time.time()),
                        last_agent=latest.get("agent_name", "unknown-agent"),
                        last_task=latest.get("task", "Unknown"),
                        stopped_at_file=latest.get("stopped_at_file"),
                        stopped_at_line=latest.get("stopped_at_line"),
                        completed_milestones=extra.get("completed_milestones", []),
                        pending_milestones=extra.get("pending_milestones", []),
                        architectural_decisions=extra.get("architectural_decisions", []),
                        context_notes=extra.get("context_notes", []),
                        status=latest.get("status", "IN_PROGRESS"),
                    )
            except Exception as store_err:
                logger.debug("Failed reading checkpoint from SQLite: %s", store_err)

        if not os.path.exists(self.checkpoint_file):
            return None

        try:
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return CheckpointData(
                    last_updated=data.get("last_updated", time.time()),
                    last_agent=data.get("last_agent", "unknown-agent"),
                    last_task=data.get("last_task", "Unknown"),
                    stopped_at_file=data.get("stopped_at_file"),
                    stopped_at_line=data.get("stopped_at_line"),
                    completed_milestones=data.get("completed_milestones", []),
                    pending_milestones=data.get("pending_milestones", []),
                    architectural_decisions=data.get("architectural_decisions", []),
                    context_notes=data.get("context_notes", []),
                    status=data.get("status", "IN_PROGRESS"),
                )
        except Exception:
            return None

    def save_checkpoint(
        self,
        last_task: str,
        last_agent: str = "hallwright-agent",
        stopped_at_file: Optional[str] = None,
        stopped_at_line: Optional[int] = None,
        completed_milestones: Optional[List[str]] = None,
        pending_milestones: Optional[List[str]] = None,
        architectural_decisions: Optional[List[str]] = None,
        context_notes: Optional[List[str]] = None,
        status: str = "IN_PROGRESS",
    ) -> bool:
        """Record an atomic checkpoint. Returns False if continuity is disabled."""
        if not self._enabled:
            return False

        os.makedirs(self.artisan_dir, exist_ok=True)

        existing = self.load_checkpoint() or CheckpointData()

        # Merge milestones
        merged_completed = list(existing.completed_milestones)
        if completed_milestones:
            for m in completed_milestones:
                if m not in merged_completed:
                    merged_completed.append(m)

        merged_pending = list(pending_milestones) if pending_milestones is not None else list(existing.pending_milestones)
        # Remove completed from pending
        merged_pending = [p for p in merged_pending if p not in merged_completed]

        merged_decisions = list(existing.architectural_decisions)
        if architectural_decisions:
            for d in architectural_decisions:
                if d not in merged_decisions:
                    merged_decisions.append(d)

        merged_notes = list(existing.context_notes)
        if context_notes:
            for n in context_notes:
                if n not in merged_notes:
                    merged_notes.append(n)

        checkpoint = CheckpointData(
            last_updated=time.time(),
            last_agent=last_agent,
            last_task=last_task,
            stopped_at_file=stopped_at_file or existing.stopped_at_file,
            stopped_at_line=stopped_at_line if stopped_at_line is not None else existing.stopped_at_line,
            completed_milestones=merged_completed,
            pending_milestones=merged_pending,
            architectural_decisions=merged_decisions,
            context_notes=merged_notes,
            status=status,
        )

        if self.store:
            try:
                cp_id = f"cp_{int(checkpoint.last_updated*1000)}"
                session_id = f"sess_{int(checkpoint.last_updated)}"
                extra = {
                    "completed_milestones": checkpoint.completed_milestones,
                    "pending_milestones": checkpoint.pending_milestones,
                    "architectural_decisions": checkpoint.architectural_decisions,
                    "context_notes": checkpoint.context_notes,
                }
                self.store.save_checkpoint(
                    checkpoint_id=cp_id,
                    session_id=session_id,
                    agent_name=checkpoint.last_agent,
                    task=checkpoint.last_task,
                    stopped_at_file=checkpoint.stopped_at_file,
                    stopped_at_line=checkpoint.stopped_at_line,
                    status=checkpoint.status,
                    extra_data=extra
                )
            except Exception as store_err:
                logger.debug("Failed saving checkpoint to SQLite: %s", store_err)

        try:
            with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(asdict(checkpoint), f, indent=2)

            self._write_handoff_markdown(checkpoint)
            return True
        except Exception:
            return False

    def _write_handoff_markdown(self, cp: CheckpointData) -> None:
        """Write human and AI-readable handoff document."""
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cp.last_updated))
        lines = [
            "# 🤝 Hallwright Universal Agent Handoff",
            "",
            f"> **Last Agent Active:** `{cp.last_agent}`",
            f"> **Last Checkpoint:** {date_str}",
            f"> **Status:** `{cp.status}`",
            "",
            "## 📍 Current Position",
            f"- **Last Task Executed:** {cp.last_task}",
            f"- **Stopped At File:** `{cp.stopped_at_file or 'N/A'}`" + (f":{cp.stopped_at_line}" if cp.stopped_at_line else ""),
            "",
        ]

        if cp.completed_milestones:
            lines.append("## ✅ Completed Milestones")
            for m in cp.completed_milestones:
                lines.append(f"- [x] {m}")
            lines.append("")

        if cp.pending_milestones:
            lines.append("## 🎯 Recommended Next Steps (Pending)")
            for p in cp.pending_milestones:
                lines.append(f"- [ ] {p}")
            lines.append("")

        if cp.architectural_decisions:
            lines.append("## 🏛️ Architectural Decisions Recorded")
            for d in cp.architectural_decisions:
                lines.append(f"- {d}")
            lines.append("")

        if cp.context_notes:
            lines.append("## 📝 Scars & Context Notes")
            for n in cp.context_notes:
                lines.append(f"- {n}")
            lines.append("")

        lines.extend([
            "---",
            "*Note: This continuity handoff is completely optional. Pass `--no-continuity` to bypass.*",
        ])

        try:
            with open(self.handoff_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except OSError as write_err:
            return

    def generate_resumption_prompt(self) -> str:
        """Generate a direct context prompt for any incoming LLM agent."""
        cp = self.load_checkpoint()
        if not cp:
            return (
                "No previous Hallwright checkpoint found or continuity is disabled.\n"
                "Starting with a fresh context. Run 'hallwright status' to inspect current project."
            )

        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cp.last_updated))
        prompt_parts = [
            f"=== HALLWRIGHT CONTINUITY HANDOFF ({date_str}) ===",
            f"PREVIOUS AGENT: {cp.last_agent}",
            f"LAST COMPLETED TASK: {cp.last_task}",
        ]

        if cp.stopped_at_file:
            loc = f"{cp.stopped_at_file}" + (f":{cp.stopped_at_line}" if cp.stopped_at_line else "")
            prompt_parts.append(f"STOPPED AT FILE: {loc}")

        if cp.completed_milestones:
            prompt_parts.append("\nRECENTLY COMPLETED:")
            for m in cp.completed_milestones[-5:]:
                prompt_parts.append(f"  ✓ {m}")

        if cp.pending_milestones:
            prompt_parts.append("\nRECOMMENDED NEXT ACTIONS:")
            for p in cp.pending_milestones:
                prompt_parts.append(f"  → {p}")

        if cp.architectural_decisions:
            prompt_parts.append("\nKEY ARCHITECTURAL DECISIONS:")
            for d in cp.architectural_decisions[-4:]:
                prompt_parts.append(f"  • {d}")

        prompt_parts.append("================================================")
        return "\n".join(prompt_parts)

    def clear(self) -> bool:
        """Remove checkpoint files."""
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
            if os.path.exists(self.handoff_file):
                os.remove(self.handoff_file)
            return True
        except Exception:
            return False
