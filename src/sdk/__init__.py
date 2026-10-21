"""
Hallwright SDK & Craftsmanship Engine
"""

__version__ = "0.10.87"

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
from .web_healer import AutonomousWebHealer, HealingResult
from .visual_learner import VisualPCLearner
from .visual_primitives import VisualPrimitivesEngine
from .visual_transmuter import VisualTransmuter

__all__ = [
    "VisualPCLearner",
    "VisualPrimitivesEngine",
    "VisualTransmuter",
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
