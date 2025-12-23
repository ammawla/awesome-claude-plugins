#!/usr/bin/env python3
"""
Integration tests for marketplace scraper
"""

import unittest
import tempfile
import os
import json
from scripts.config import Config
from scripts.utils.fetcher import Fetcher
from scripts.generators.readme_generator import ReadmeGenerator

class TestIntegration(unittest.TestCase):
    """Integration tests for the marketplace scraper."""

    def test_full_workflow(self):
        """Test the complete workflow from config to README generation."""
        # Create test config
        config_data = """
sources:
  - id: "test-source"
    url: "http://httpbin.org/json"
    format: "json"
    enabled: true
generation:
  output_file: "test_readme.md"
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_data)
            config_file = f.name

        # Create test output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            output_file = f.name

        try:
            # Test config loading
            config = Config(config_file)
            self.assertEqual(len(config.sources), 1)
            self.assertEqual(config.sources[0]["id"], "test-source")

            # Test README generator
            generator = ReadmeGenerator()

            # Add sample data
            sample_marketplaces = [
                {
                    "id": "test-marketplace",
                    "name": "Test Marketplace",
                    "description": "A test marketplace",
                    "url": "https://github.com/test/test"
                }
            ]

            sample_plugins = [
                {
                    "id": "test-plugin",
                    "name": "Test Plugin",
                    "description": "A test plugin",
                    "category": "Development Tools",
                    "marketplace_id": "test-marketplace",
                    "url": "https://github.com/test/plugin"
                }
            ]

            generator.add_marketplaces(sample_marketplaces)
            generator.add_plugins(sample_plugins)

            content = generator.generate_readme()

            # Verify content structure
            self.assertIn("# Awesome Claude Plugins", content)
            self.assertIn("## Contents", content)
            self.assertIn("## Marketplaces", content)
            self.assertIn("Test Marketplace", content)
            self.assertIn("Test Plugin", content)

            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Verify file was written
            self.assertTrue(os.path.exists(output_file))
            with open(output_file, 'r', encoding='utf-8') as f:
                written_content = f.read()
                self.assertEqual(written_content, content)

        finally:
            # Cleanup
            if os.path.exists(config_file):
                os.unlink(config_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

if __name__ == '__main__':
    unittest.main()