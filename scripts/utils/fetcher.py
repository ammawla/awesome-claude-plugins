#!/usr/bin/env python3
"""
HTTP fetching utilities
"""

import requests
import json
import logging
import time
import hashlib
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from .validators import Validator

logger = logging.getLogger(__name__)

class Fetcher:
    """HTTP data fetching utilities."""

    def __init__(self, timeout: int = 30, cache_ttl: int = 3600):
        self.timeout = timeout
        self.cache_ttl = cache_ttl  # Cache TTL in seconds (default 1 hour)
        self.session = requests.Session()
        self.cache: Dict[str, Dict[str, Any]] = {}  # URL -> {data, timestamp}

    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if 'timestamp' not in cache_entry:
            return False
        return (time.time() - cache_entry['timestamp']) < self.cache_ttl

    def _get_cached_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if valid."""
        cache_key = self._get_cache_key(url)
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if self._is_cache_valid(cache_entry):
                logger.debug("Cache hit for: %s", url)
                return cache_entry['data']
            else:
                logger.debug("Cache expired for: %s", url)
                del self.cache[cache_key]
        return None

    def _set_cached_data(self, url: str, data: Dict[str, Any]):
        """Store data in cache."""
        cache_key = self._get_cache_key(url)
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }

    def fetch_json(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch JSON data from URL with caching and performance monitoring."""
        # Check cache first
        cached_data = self._get_cached_data(url)
        if cached_data is not None:
            return cached_data

        start_time = time.time()
        try:
            logger.info("Fetching data from: %s", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            fetch_time = time.time() - start_time
            logger.info("Successfully fetched data from %s in %.2f seconds", url, fetch_time)

            if not Validator.validate_json_data(data):
                return None

            # Cache the successful response
            self._set_cached_data(url, data)

            return data

        except requests.exceptions.RequestException as e:
            fetch_time = time.time() - start_time
            logger.error("Failed to fetch %s in %.2f seconds: %s", url, fetch_time, e)
            return None
        except json.JSONDecodeError as e:
            fetch_time = time.time() - start_time
            logger.error("Failed to parse JSON from %s in %.2f seconds: %s", url, fetch_time, e)
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

    def _fetch_repo_file(self, repo_owner: str, repo_name: str, filename: str, repo_branch: str = "main") -> Optional[Dict[str, Any]]:
        """Fetch a JSON file from a GitHub repository with branch fallback."""
        # Try multiple branch names in order of popularity
        branch_attempts = [repo_branch]
        if repo_branch == "main":
            branch_attempts.extend(["master", "develop", "development", "dev"])
        elif repo_branch == "master":
            branch_attempts.extend(["main", "develop", "development", "dev"])

        for attempt_branch in branch_attempts:
            url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{attempt_branch}/{filename}"
            try:
                logger.debug(f"Trying to fetch {filename} from {url}")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                data = response.json()
                logger.info(f"Successfully fetched {filename} from {repo_owner}/{repo_name}")
                return data
            except requests.exceptions.RequestException as e:
                logger.debug(f"Failed to fetch {filename} from branch {attempt_branch}: {e}")
                continue
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from {url}: {e}")
                continue

        return None

    def fetch_plugin_manifest(self, repo_owner: str, repo_name: str,
                            repo_branch: str = "main", plugin_path: str = "") -> Optional[Dict[str, Any]]:
        """Fetch marketplace.json from GitHub repository.

        Looks for .claude-plugin/marketplace.json file that contains plugin listings.
        """
        data = self._fetch_repo_file(repo_owner, repo_name, ".claude-plugin/marketplace.json", repo_branch)
        
        if data and self._validate_marketplace_json(data):
            return data
            
        logger.warning(f"No valid marketplace.json found in {repo_owner}/{repo_name}")
        return None

    def fetch_plugin_config(self, repo_owner: str, repo_name: str, repo_branch: str = "main") -> Optional[Dict[str, Any]]:
        """Fetch plugin.json from GitHub repository."""
        data = self._fetch_repo_file(repo_owner, repo_name, ".claude-plugin/plugin.json", repo_branch)
        
        if data and self._validate_plugin_json(data):
            logger.info(f"Successfully fetched plugin.json from {repo_owner}/{repo_name}")
            return data
            
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

    def _validate_plugin_json(self, data: Dict[str, Any]) -> bool:
        """Validate plugin.json structure."""
        if not isinstance(data, dict):
            return False
        # Basic requirements for a plugin
        return "name" in data and "description" in data

    def fetch_plugins_from_marketplace(self, marketplace_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch all plugins from a marketplace by reading its marketplace.json or plugin.json file."""
        plugins = []

        repo_owner = marketplace_data.get("repoOwner")
        repo_name = marketplace_data.get("repoName")
        repo_branch = marketplace_data.get("repoBranch", "main")

        if not repo_owner or not repo_name:
            logger.warning("Missing repo information for marketplace: %s", marketplace_data.get("id"))
            return plugins

        # 1. Try fetching marketplace.json (collection of plugins)
        marketplace_json = self.fetch_plugin_manifest(repo_owner, repo_name, repo_branch)

        if marketplace_json:
            # Extract plugins from the marketplace.json
            marketplace_plugins = marketplace_json.get("plugins", [])
            for plugin_data in marketplace_plugins:
                if not isinstance(plugin_data, dict):
                    logger.warning("Invalid plugin data in marketplace.json, skipping")
                    continue
                
                plugins.append(self._create_plugin_entry(
                    plugin_data, marketplace_data, repo_owner, repo_name, repo_branch, is_single=False
                ))
        
        # 2. If no plugins found (or specifically if marketplace.json wasn't there), try plugin.json
        if not plugins:
            plugin_json = self.fetch_plugin_config(repo_owner, repo_name, repo_branch)
            if plugin_json:
                plugins.append(self._create_plugin_entry(
                    plugin_json, marketplace_data, repo_owner, repo_name, repo_branch, is_single=True
                ))

        if not plugins:
            logger.warning("No plugins found for %s/%s", repo_owner, repo_name)

        logger.info("Fetched %d plugins from marketplace %s", len(plugins), marketplace_data.get("id"))
        return plugins

    def _create_plugin_entry(self, plugin_data: Dict[str, Any], marketplace_data: Dict[str, Any], 
                           repo_owner: str, repo_name: str, repo_branch: str, is_single: bool) -> Dict[str, Any]:
        """Create a plugin entry from data."""
        manifest_filename = ".claude-plugin/plugin.json" if is_single else ".claude-plugin/marketplace.json"
        
        return {
            "id": f"{repo_owner}/{repo_name}:{plugin_data.get('name', 'unknown')}",
            "name": plugin_data.get("name", "Unknown Plugin"),
            "description": plugin_data.get("description", ""),
            "category": plugin_data.get("category", "Uncategorized"),
            "marketplace_id": marketplace_data["id"],
            "repo_url": f"https://github.com/{repo_owner}/{repo_name}",
            "repo_branch": repo_branch,
            "manifest_url": f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{repo_branch}/{manifest_filename}",
            "author": plugin_data.get("author"),
            "version": plugin_data.get("version", "1.0.0"),
            "tags": plugin_data.get("tags", []),
            "homepage": plugin_data.get("homepage"),
            "installation": plugin_data.get("installation"),
            # Include any additional fields
            "source_data": plugin_data
        }