#!/usr/bin/env python3
"""
HTTP fetching utilities
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from .validators import Validator

logger = logging.getLogger(__name__)

class Fetcher:
    """HTTP data fetching utilities."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch JSON data from URL."""
        try:
            logger.info("Fetching data from: %s", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            if not Validator.validate_json_data(data):
                return None

            logger.info("Successfully fetched data from %s", url)
            return data

        except requests.exceptions.RequestException as e:
            logger.error("Failed to fetch %s: %s", url, e)
            return None
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON from %s: %s", url, e)
            return None

    def fetch_marketplaces_from_source(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch marketplace data from a configured source."""
        url = source_config.get("url")
        if not url:
            logger.error("No URL specified in source config")
            return []

        data = self.fetch_json(url)
        if not data:
            return []

        # The expected format is a dict with marketplace IDs as keys
        marketplaces = []
        for marketplace_id, marketplace_data in data.items():
            if isinstance(marketplace_data, dict):
                marketplace_data["id"] = marketplace_id
                marketplace_data["source_url"] = url
                if Validator.validate_marketplace_data(marketplace_data):
                    marketplaces.append(marketplace_data)

        logger.info("Fetched %d marketplaces from %s", len(marketplaces), url)
        return marketplaces

    def fetch_plugin_manifest(self, repo_owner: str, repo_name: str,
                            repo_branch: str = "main", plugin_path: str = "") -> Optional[Dict[str, Any]]:
        """Fetch marketplace.json from GitHub repository.

        Looks for .claude-plugin/marketplace.json file that contains plugin listings.
        """
        # Try the marketplace.json path used by code-assistant-manager
        marketplace_json_path = ".claude-plugin/marketplace.json"

        # Try multiple branch names in order of popularity
        branch_attempts = [repo_branch]
        if repo_branch == "main":
            branch_attempts.extend(["master", "develop", "development", "dev"])
        elif repo_branch == "master":
            branch_attempts.extend(["main", "develop", "development", "dev"])

        for attempt_branch in branch_attempts:
            url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{attempt_branch}/{marketplace_json_path}"
            try:
                logger.debug(f"Trying to fetch marketplace.json from {url}")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                marketplace_data = response.json()
                if self._validate_marketplace_json(marketplace_data):
                    logger.info(f"Successfully fetched marketplace.json from {repo_owner}/{repo_name}")
                    return marketplace_data
                else:
                    logger.warning(f"Invalid marketplace.json format from {repo_owner}/{repo_name}")
            except requests.exceptions.RequestException as e:
                logger.debug(f"Failed to fetch from branch {attempt_branch}: {e}")
                continue

        logger.warning(f"No valid marketplace.json found in {repo_owner}/{repo_name}")
        return None

    def _validate_marketplace_json(self, data: Dict[str, Any]) -> bool:
        """Validate marketplace.json structure."""
        if not isinstance(data, dict):
            return False

        # Must have plugins array
        plugins = data.get("plugins", [])
        if not isinstance(plugins, list):
            return False

        # Check that plugins have required fields
        for plugin in plugins:
            if not isinstance(plugin, dict):
                return False
            if "name" not in plugin:
                return False

        return True

    def fetch_plugins_from_marketplace(self, marketplace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch all plugins from a marketplace by reading its marketplace.json file."""
        plugins = []

        repo_owner = marketplace_data.get("repoOwner")
        repo_name = marketplace_data.get("repoName")
        repo_branch = marketplace_data.get("repoBranch", "main")

        if not repo_owner or not repo_name:
            logger.warning("Missing repo information for marketplace: %s", marketplace_data.get("id"))
            return plugins

        # Fetch marketplace.json which contains the plugins array
        marketplace_json = self.fetch_plugin_manifest(repo_owner, repo_name, repo_branch)

        if not marketplace_json:
            logger.warning("No marketplace.json found for %s/%s, marketplace will have no plugins", repo_owner, repo_name)
            return plugins

        # Extract plugins from the marketplace.json
        marketplace_plugins = marketplace_json.get("plugins", [])

        for plugin_data in marketplace_plugins:
            if not isinstance(plugin_data, dict):
                logger.warning("Invalid plugin data in marketplace.json, skipping")
                continue

            # Build plugin entry with marketplace association
            plugin = {
                "id": f"{repo_owner}/{repo_name}:{plugin_data.get('name', 'unknown')}",
                "name": plugin_data.get("name", "Unknown Plugin"),
                "description": plugin_data.get("description", ""),
                "category": plugin_data.get("category", "Uncategorized"),
                "marketplace_id": marketplace_data["id"],
                "repo_url": f"https://github.com/{repo_owner}/{repo_name}",
                "manifest_url": f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{repo_branch}/.claude-plugin/marketplace.json",
                "author": plugin_data.get("author"),
                "version": plugin_data.get("version", "1.0.0"),
                "tags": plugin_data.get("tags", []),
                "homepage": plugin_data.get("homepage"),
                "installation": plugin_data.get("installation"),
                # Include any additional fields from the marketplace.json
                "source_data": plugin_data
            }
            plugins.append(plugin)

        logger.info("Fetched %d plugins from marketplace %s", len(plugins), marketplace_data.get("id"))
        return plugins