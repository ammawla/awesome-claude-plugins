#!/usr/bin/env python3
"""
README generator for marketplace scraper
"""

import logging
from typing import List, Dict, Any
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class ReadmeGenerator:
    """Generates README content from marketplace and plugin data."""

    def __init__(self):
        self.marketplaces: List[Dict[str, Any]] = []
        self.plugins: List[Dict[str, Any]] = []

    def add_marketplaces(self, marketplaces: List[Dict[str, Any]]):
        """Add marketplace data."""
        self.marketplaces.extend(marketplaces)

    def add_plugins(self, plugins: List[Dict[str, Any]]):
        """Add plugin data."""
        self.plugins.extend(plugins)

    def generate_title(self) -> str:
        """Generate the README title."""
        return "# Awesome Claude Plugins\n\nA curated list of awesome Claude marketplaces and plugins to enhance your Claude Code experience.\n\n"

    def generate_table_of_contents(self) -> str:
        """Generate table of contents."""
        lines = ["## Contents\n"]
        lines.append("- [Marketplaces](#marketplaces)")

        # Group plugins by category
        categories = self._get_categories()
        for category in sorted(categories.keys()):
            anchor = category.lower().replace(" ", "-").replace("&", "")
            lines.append(f"- [{category}](#{anchor})")

        lines.append("- [Contributing](#contributing)")
        lines.append("")
        return "\n".join(lines)

    def generate_marketplaces_table(self) -> str:
        """Generate marketplaces table."""
        if not self.marketplaces:
            return ""

        lines = ["## Marketplaces\n\n"]
        lines.append("| Marketplace | Description |")
        lines.append("|-------------|-------------|")

        for marketplace in sorted(self.marketplaces, key=lambda x: x.get("name", "")):
            name = marketplace.get("name", marketplace.get("id", "Unknown"))
            description = marketplace.get("description", "")[
                :100
            ]  # Truncate long descriptions

            # Construct URL from repoOwner and repoName if available
            repo_owner = marketplace.get("repoOwner")
            repo_name = marketplace.get("repoName")
            if repo_owner and repo_name:
                url = f"https://github.com/{repo_owner}/{repo_name}"
                name_cell = f"[{name}]({url})"
            else:
                name_cell = name

            lines.append(f"| {name_cell} | {description} |")

        lines.append("")
        return "\n".join(lines)

    def generate_plugins_by_category(self) -> str:
        """Generate plugins organized by category with table format."""
        if not self.plugins:
            return ""

        # Group plugins by category
        categories = defaultdict(list)
        for plugin in self.plugins:
            category = plugin.get("category", "Uncategorized")
            categories[category].append(plugin)

        lines = []
        for category in sorted(categories.keys()):
            lines.append(f"## {category}\n")

            # Group plugins by marketplace within category
            marketplace_plugins = defaultdict(list)
            for plugin in categories[category]:
                marketplace_id = plugin.get("marketplace_id", "unknown")
                marketplace_plugins[marketplace_id].append(plugin)

            for marketplace_id, plugins in marketplace_plugins.items():
                marketplace_name = self._get_marketplace_name(marketplace_id)
                if marketplace_name:
                    lines.append(f"### {marketplace_name}\n")

                # Table header
                lines.append("| Plugin | Description | Author | Version |")
                lines.append("|--------|-------------|--------|---------|")

                # Sort plugins alphabetically
                sorted_plugins = sorted(plugins, key=lambda p: p.get("name", ""))

                for plugin in sorted_plugins:
                    name = plugin.get("name", "Unknown Plugin")
                    description = (
                        plugin.get("description", "").replace("\n", " ").strip()
                    )
                    # Truncate description for table readability
                    if len(description) > 150:
                        description = description[:147] + "..."
                    author_data = plugin.get("author", "")
                    # Handle author as string or dict with name
                    if isinstance(author_data, dict):
                        author = author_data.get("name", "")
                    else:
                        author = str(author_data)
                    version = plugin.get("version", "latest")
                    homepage_url = plugin.get("homepage", "")

                    # Create name cell with hyperlink if homepage URL exists
                    if homepage_url:
                        name_cell = f"[{name}]({homepage_url})"
                    else:
                        name_cell = name

                    # Escape pipe characters in description
                    description = description.replace("|", "\\|")

                    lines.append(
                        f"| {name_cell} | {description} | {author} | {version} |"
                    )

                lines.append("")

            lines.append("")

        return "\n".join(lines)

    def generate_contributing(self) -> str:
        """Generate contributing section."""
        return """## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details on how to add new marketplaces or plugins.

To add a new plugin or marketplace:
1. Fork this repository
2. Add the entry to the appropriate section
3. Ensure the plugin is verified and documented
4. Submit a pull request with a clear description
"""

    def generate_readme(self) -> str:
        """Generate complete README content."""
        sections = [
            self.generate_title(),
            self.generate_table_of_contents(),
            self.generate_marketplaces_table(),
            self.generate_plugins_by_category(),
            self.generate_contributing(),
        ]

        content = "".join(sections)

        # Validate markdown format
        if not self.validate_markdown(content):
            logger.warning("Generated markdown failed validation")
        else:
            logger.info("Generated markdown validation successful")

        return content

    def _get_categories(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get plugins grouped by category."""
        categories = defaultdict(list)
        for plugin in self.plugins:
            category = plugin.get("category", "Uncategorized")
            categories[category].append(plugin)
        return categories

    def _get_marketplace_name(self, marketplace_id: str) -> str:
        """Get marketplace name by ID."""
        for marketplace in self.marketplaces:
            if marketplace.get("id") == marketplace_id:
                return marketplace.get("name", marketplace_id)
        return marketplace_id

    def validate_markdown(self, content: str) -> bool:
        """Basic markdown validation for generated content."""
        try:
            # Check for balanced brackets in links [text](url)
            link_pattern = r"\[([^\]]*)\]\(([^)]*)\)"
            links = re.findall(link_pattern, content)

            for text, url in links:
                if not text.strip():
                    logger.warning("Found empty link text in markdown")
                    return False
                if not url.strip():
                    logger.warning("Found empty URL in markdown link")
                    return False

            # Basic check for table structure - just ensure tables have separators
            lines = content.split("\n")
            table_started = False
            has_separator = False

            for line in lines:
                if "|" in line and not line.strip().startswith("#"):
                    if (
                        "|---" in line
                        or "|:--" in line
                        or ":---" in line
                        or "---:" in line
                    ):
                        has_separator = True
                        table_started = False
                    elif not table_started:
                        table_started = True
                    # else: continuing table row

            # If we found tables, ensure they have separators
            if table_started and not has_separator:
                logger.warning("Found table without proper separator")
                return False

            logger.info("Markdown validation passed")
            return True

        except Exception as e:
            logger.error(f"Markdown validation failed: {e}")
            return False
