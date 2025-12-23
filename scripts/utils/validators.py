#!/usr/bin/env python3
"""
Data validation utilities
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class Validator:
    """Data validation utilities."""

    @staticmethod
    def validate_marketplace_data(data: Dict[str, Any]) -> bool:
        """Validate marketplace data structure."""
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in data:
                logger.error("Missing required field '%s' in marketplace data", field)
                return False

        if not isinstance(data.get("name"), str) or not data["name"].strip():
            logger.error("Invalid marketplace name")
            return False

        return True

    @staticmethod
    def validate_plugin_data(data: Dict[str, Any]) -> bool:
        """Validate plugin data structure."""
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in data:
                logger.error("Missing required field '%s' in plugin data", field)
                return False

        if not isinstance(data.get("name"), str) or not data["name"].strip():
            logger.error("Invalid plugin name")
            return False

        return True

    @staticmethod
    def validate_json_data(data: Any) -> bool:
        """Validate that data is valid JSON structure."""
        if not isinstance(data, (dict, list)):
            logger.error("Data is not a valid JSON structure")
            return False
        return True