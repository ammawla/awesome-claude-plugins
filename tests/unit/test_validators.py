#!/usr/bin/env python3
"""
Unit tests for validators module
"""

import unittest
from scripts.utils.validators import Validator

class TestValidators(unittest.TestCase):
    """Test cases for Validator class."""

    def test_validate_marketplace_data_valid(self):
        """Test validation of valid marketplace data."""
        valid_data = {
            "name": "Test Marketplace",
            "description": "A test marketplace",
            "enabled": True
        }
        self.assertTrue(Validator.validate_marketplace_data(valid_data))

    def test_validate_marketplace_data_missing_name(self):
        """Test validation fails when name is missing."""
        invalid_data = {
            "description": "A test marketplace",
            "enabled": True
        }
        self.assertFalse(Validator.validate_marketplace_data(invalid_data))

    def test_validate_marketplace_data_empty_name(self):
        """Test validation fails when name is empty."""
        invalid_data = {
            "name": "",
            "description": "A test marketplace",
            "enabled": True
        }
        self.assertFalse(Validator.validate_marketplace_data(invalid_data))

    def test_validate_plugin_data_valid(self):
        """Test validation of valid plugin data."""
        valid_data = {
            "name": "Test Plugin",
            "description": "A test plugin",
            "category": "Development Tools"
        }
        self.assertTrue(Validator.validate_plugin_data(valid_data))

    def test_validate_plugin_data_missing_description(self):
        """Test validation fails when description is missing."""
        invalid_data = {
            "name": "Test Plugin",
            "category": "Development Tools"
        }
        self.assertFalse(Validator.validate_plugin_data(invalid_data))

    def test_validate_json_data_valid(self):
        """Test validation of valid JSON data."""
        self.assertTrue(Validator.validate_json_data({"key": "value"}))
        self.assertTrue(Validator.validate_json_data([1, 2, 3]))

    def test_validate_json_data_invalid(self):
        """Test validation fails for invalid JSON data."""
        self.assertFalse(Validator.validate_json_data("string"))
        self.assertFalse(Validator.validate_json_data(123))
        self.assertFalse(Validator.validate_json_data(None))

if __name__ == '__main__':
    unittest.main()