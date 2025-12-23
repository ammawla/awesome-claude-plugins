#!/usr/bin/env python3
"""
Unit tests for config module
"""

import unittest
import tempfile
import os
from scripts.config import Config

class TestConfig(unittest.TestCase):
    """Test cases for Config class."""

    def test_load_default_config(self):
        """Test loading default configuration when no file exists."""
        config = Config("nonexistent.yaml")
        self.assertEqual(len(config.sources), 0)
        self.assertEqual(config.generation["output_file"], "README.md")

    def test_load_config_from_file(self):
        """Test loading configuration from YAML file."""
        config_data = """
version: "1.0"
sources:
  - id: "test-source"
    url: "https://example.com/data.json"
    format: "json"
    enabled: true
generation:
  output_file: "custom.md"
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_data)
            temp_file = f.name

        try:
            config = Config(temp_file)
            self.assertEqual(len(config.sources), 1)
            self.assertEqual(config.sources[0]["id"], "test-source")
            self.assertEqual(config.generation["output_file"], "custom.md")
        finally:
            os.unlink(temp_file)

    def test_get_enabled_sources(self):
        """Test filtering enabled sources."""
        config_data = """
sources:
  - id: "enabled"
    url: "https://example.com/1.json"
    enabled: true
    priority: 2
  - id: "disabled"
    url: "https://example.com/2.json"
    enabled: false
    priority: 1
  - id: "default-enabled"
    url: "https://example.com/3.json"
    priority: 3
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_data)
            temp_file = f.name

        try:
            config = Config(temp_file)
            enabled = config.get_enabled_sources()
            self.assertEqual(len(enabled), 2)
            # Should be sorted by priority (lower first)
            self.assertEqual(enabled[0]["id"], "enabled")
            self.assertEqual(enabled[1]["id"], "default-enabled")
        finally:
            os.unlink(temp_file)

if __name__ == '__main__':
    unittest.main()