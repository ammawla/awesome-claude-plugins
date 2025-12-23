#!/usr/bin/env python3
"""
Configuration loading utilities
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for marketplace scraper."""

    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(config_file)
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f) or {}
                logger.info("Loaded configuration from %s", self.config_file)
            else:
                logger.warning("Config file %s not found, using defaults", self.config_file)
                self._config = self._get_defaults()
        except Exception as e:
            logger.error("Failed to load config: %s", e)
            self._config = self._get_defaults()

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "version": "1.0",
            "sources": [],
            "generation": {
                "output_file": "README.md",
                "include_marketplace_tables": True,
                "include_plugin_categories": True
            },
            "logging": {
                "level": "INFO"
            }
        }

    @property
    def sources(self) -> List[Dict[str, Any]]:
        """Get configured sources."""
        return self._config.get("sources", [])

    @property
    def generation(self) -> Dict[str, Any]:
        """Get generation settings."""
        return self._config.get("generation", {})

    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self._config.get("logging", {})

    def get_enabled_sources(self) -> List[Dict[str, Any]]:
        """Get only enabled sources, sorted by priority."""
        enabled = [s for s in self.sources if s.get("enabled", True)]
        return sorted(enabled, key=lambda s: s.get("priority", 999))