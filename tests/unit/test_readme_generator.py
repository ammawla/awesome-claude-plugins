#!/usr/bin/env python3
"""
Unit tests for ReadmeGenerator
"""

import unittest
from scripts.generators.readme_generator import ReadmeGenerator

class TestReadmeGenerator(unittest.TestCase):
    """Test cases for ReadmeGenerator."""

    def setUp(self):
        self.generator = ReadmeGenerator()

    def test_generate_marketplaces_table_escapes_pipes(self):
        """Test that pipes in marketplace descriptions are escaped."""
        sample_marketplaces = [
            {
                "id": "test-marketplace",
                "name": "Test Marketplace",
                "description": "Description with | pipe",
                "url": "https://github.com/test/test"
            }
        ]
        self.generator.add_marketplaces(sample_marketplaces)
        content = self.generator.generate_marketplaces_table()
        
        # Expect the pipe to be escaped
        self.assertIn("Description with \\| pipe", content)
        
    def test_generate_marketplaces_table_removes_newlines(self):
        """Test that newlines in marketplace descriptions are replaced."""
        sample_marketplaces = [
            {
                "id": "test-marketplace",
                "name": "Test Marketplace",
                "description": "Description with \n newline",
                "url": "https://github.com/test/test"
            }
        ]
        self.generator.add_marketplaces(sample_marketplaces)
        content = self.generator.generate_marketplaces_table()
        
        # Expect newline to be removed/replaced with space
        self.assertNotIn("\n", content.split("|")[2]) # Check the description cell specifically

if __name__ == '__main__':
    unittest.main()
