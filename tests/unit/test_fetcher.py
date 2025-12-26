import unittest
from unittest.mock import MagicMock, patch
import requests
from scripts.utils.fetcher import Fetcher

class TestFetcher(unittest.TestCase):
    """Test cases for Fetcher utility."""

    def setUp(self):
        self.fetcher = Fetcher()
        self.mock_response = MagicMock()
        self.fetcher.session.get = MagicMock(return_value=self.mock_response)
        
    def test_fetch_plugin_manifest_success(self):
        """Test fetching marketplace.json successfully."""
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {
            "plugins": [{"name": "plugin1", "description": "desc1"}]
        }
        
        result = self.fetcher.fetch_plugin_manifest("owner", "repo")
        self.assertIsNotNone(result)
        self.assertEqual(len(result["plugins"]), 1)

    def test_fetch_plugin_manifest_not_found(self):
        """Test fetching marketplace.json when not found."""
        self.mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("Not Found")
        
        result = self.fetcher.fetch_plugin_manifest("owner", "repo")
        self.assertIsNone(result)

    def test_fetch_plugin_config_success(self):
        """Test fetching plugin.json successfully."""
        self.mock_response.status_code = 200
        self.mock_response.raise_for_status.side_effect = None
        self.mock_response.json.return_value = {
            "name": "single-plugin",
            "description": "single desc"
        }
        
        result = self.fetcher.fetch_plugin_config("owner", "repo")
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "single-plugin")

    def test_fetch_plugins_fallback_to_plugin_json(self):
        """Test fallback to plugin.json when marketplace.json is missing."""
        # Setup mock to fail for marketplace.json and succeed for plugin.json
        def side_effect(url, timeout=30):
            if "marketplace.json" in url:
                mock_resp = MagicMock()
                mock_resp.raise_for_status.side_effect = requests.exceptions.RequestException("Not Found")
                return mock_resp
            elif "plugin.json" in url:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "name": "single-plugin",
                    "description": "single desc",
                    "version": "1.0.0"
                }
                return mock_resp
            return MagicMock()

        self.fetcher.session.get = MagicMock(side_effect=side_effect)

        marketplace_data = {"repoOwner": "owner", "repoName": "repo", "id": "test-mp"}
        plugins = self.fetcher.fetch_plugins_from_marketplace(marketplace_data)

        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["name"], "single-plugin")
        self.assertTrue("plugin.json" in plugins[0]["manifest_url"])

    def test_fetch_plugins_marketplace_priority(self):
        """Test that marketplace.json takes priority over plugin.json."""
        # Setup mock to succeed for marketplace.json
        def side_effect(url, timeout=30):
            if "marketplace.json" in url:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "plugins": [{"name": "mp-plugin", "description": "desc"}]
                }
                return mock_resp
            elif "plugin.json" in url:
                 # Should not be called if marketplace.json succeeds, but if it is, return something else to verify
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "name": "single-plugin",
                    "description": "desc"
                }
                return mock_resp
            return MagicMock()

        self.fetcher.session.get = MagicMock(side_effect=side_effect)

        marketplace_data = {"repoOwner": "owner", "repoName": "repo", "id": "test-mp"}
        plugins = self.fetcher.fetch_plugins_from_marketplace(marketplace_data)

        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0]["name"], "mp-plugin")
        # Ensure we didn't get the single plugin
        self.assertNotEqual(plugins[0]["name"], "single-plugin")

if __name__ == '__main__':
    unittest.main()
