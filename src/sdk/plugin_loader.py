"""
Hallwright Zero-Overhead Plugin Loader
Dynamically discovers and loads external gatekeeper plugins from .hallwright/plugins/.
Part of Pillar V: Zero-Overhead Plugin & Ecosystem (Bosqich 55-57).
"""

import os
import sys
import importlib.util
from typing import List, Optional
from .pdk import PluginRegistry, PluginManifest, verify_manifest_signature


class PluginLoader:
    def __init__(self, plugins_dir: Optional[str] = None, secret_key: Optional[str] = None) -> None:
        self.plugins_dir = plugins_dir or os.path.join(os.getcwd(), ".hallwright", "plugins")
        self.secret_key = secret_key
        self.registry = PluginRegistry()

    def discover_and_load(self) -> PluginRegistry:
        if not os.path.isdir(self.plugins_dir):
            return self.registry

        for entry in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, entry)
            if entry.endswith(".py"):
                self._load_python_plugin(plugin_path)
            elif os.path.isdir(plugin_path):
                init_file = os.path.join(plugin_path, "__init__.py")
                if os.path.isfile(init_file):
                    self._load_python_plugin(init_file)

        return self.registry

    def _load_python_plugin(self, file_path: str) -> None:
        module_name = f"hallwright_plugin_{os.path.splitext(os.path.basename(file_path))[0]}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)

                # Look for register_plugin function or MANIFEST attribute
                if hasattr(mod, "get_manifest"):
                    manifest = mod.get_manifest()
                    if isinstance(manifest, PluginManifest):
                        if self.secret_key and manifest.signature:
                            if not verify_manifest_signature(manifest.to_dict(), self.secret_key):
                                return
                        self.registry.register_plugin(manifest)
                elif hasattr(mod, "MANIFEST") and isinstance(mod.MANIFEST, PluginManifest):
                    self.registry.register_plugin(mod.MANIFEST)
        except Exception as load_err:
            import logging
            logging.getLogger("hallwright.sdk.plugin").warning("Plugin load failed for %s: %s", file_path, load_err)
