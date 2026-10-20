"""
Hallwright SDK & Craftsmanship Engine
"""

from .craftsman import CraftsmanAgent, COUNCIL_MEMBERS
from .context_selector import SmartMasterSelector
from .learning_memory import LearningMemory
from .guilds import COUNCIL_GUILDS, list_guilds_summary, get_guild_for_master
from .agent_mesh import AgentMesh, AgentMessage, AgentContract
from .pdk import (
    PluginManifest,
    PluginRule,
    PluginContext,
    RuleViolation,
    PluginRegistry,
    sign_manifest,
    verify_manifest_signature,
)
from .plugin_loader import PluginLoader
from .search_engine import SearchEngine, SearchHit, SearchResultSet, SearchScope
from .prompt_engine import PromptEngine, PromptQualityScore, OptimizationResult
from .web_healer import AutonomousWebHealer, HealingResult

__all__ = [
    "CraftsmanAgent",
    "COUNCIL_MEMBERS",
    "SmartMasterSelector",
    "LearningMemory",
    "COUNCIL_GUILDS",
    "list_guilds_summary",
    "get_guild_for_master",
    "AgentMesh",
    "AgentMessage",
    "AgentContract",
    "PluginManifest",
    "PluginRule",
    "PluginContext",
    "RuleViolation",
    "PluginRegistry",
    "sign_manifest",
    "verify_manifest_signature",
    "PluginLoader",
    "SearchEngine",
    "SearchHit",
    "SearchResultSet",
    "SearchScope",
    "PromptEngine",
    "PromptQualityScore",
    "OptimizationResult",
    "AutonomousWebHealer",
    "HealingResult",
]
