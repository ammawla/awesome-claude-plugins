# Data Model: Marketplace Scraper Scripts

**Date**: 2025-12-23
**Feature**: Marketplace Scraper Scripts

## Overview

The marketplace scraper operates on three primary data entities: Marketplaces, Plugins, and Sources. These entities are extracted from GitHub-based marketplace repositories and structured for README generation.

## Core Entities

### Marketplace
Represents a Claude plugin marketplace repository.

**Fields:**
- `id` (string, required): Unique identifier (e.g., "anthropic-agent-skills")
- `name` (string, required): Human-readable marketplace name
- `description` (string, optional): Marketplace description
- `repo_owner` (string, required): GitHub repository owner
- `repo_name` (string, required): GitHub repository name
- `repo_branch` (string, optional): Default branch (default: "main")
- `repo_url` (string, computed): Full GitHub repository URL
- `plugin_count` (integer, computed): Number of plugins in marketplace

**Validation Rules:**
- `repo_owner` and `repo_name` must be non-empty strings
- `id` must be unique across all marketplaces
- Repository must exist and be accessible

**Relationships:**
- One-to-many with Plugin (marketplace contains multiple plugins)

### Plugin
Represents an individual Claude plugin with metadata.

**Fields:**
- `id` (string, required): Unique identifier combining marketplace and plugin name
- `name` (string, required): Plugin name
- `description` (string, required): Plugin description
- `category` (string, required): Plugin category (e.g., "Development Tools", "Code Quality")
- `marketplace_id` (string, required): Reference to parent marketplace
- `repo_url` (string, optional): Plugin's GitHub repository URL
- `manifest_url` (string, computed): URL to marketplace.json containing this plugin
- `author` (string, optional): Plugin author/maintainer
- `version` (string, optional): Plugin version (default: "latest")
- `tags` (array of strings, optional): Plugin tags/keywords
- `homepage` (string, optional): Plugin homepage URL
- `installation` (string, optional): Installation instructions
- `source_data` (object, optional): Raw plugin data from marketplace.json

**Validation Rules:**
- `name` and `description` must be non-empty strings
- `category` must be a valid category string
- `marketplace_id` must reference an existing marketplace

**Relationships:**
- Many-to-one with Marketplace (plugin belongs to one marketplace)

### Source
Represents a data source configuration for marketplace repositories.

**Fields:**
- `id` (string, required): Unique source identifier
- `name` (string, optional): Human-readable source name
- `url` (string, required): URL to fetch marketplace data from
- `enabled` (boolean, optional): Whether source is active (default: true)
- `priority` (integer, optional): Processing priority (lower numbers processed first)

**Validation Rules:**
- `url` must be a valid HTTP/HTTPS URL
- `id` must be unique across all sources

## Data Flow

1. **Source Processing**: Sources are loaded from config.yaml and processed in priority order
2. **Marketplace Discovery**: Each source URL is fetched to obtain marketplace repository information
3. **Plugin Extraction**: For each marketplace, marketplace.json is fetched and parsed to extract plugin data
4. **Data Merging**: Plugins from all marketplaces are merged, with marketplace attribution preserved
5. **Categorization**: Plugins are grouped by category for README generation

## State Transitions

### Marketplace States
- `discovered`: Repository identified from source data
- `fetching`: marketplace.json being downloaded
- `processed`: Plugins successfully extracted
- `failed`: Repository inaccessible or invalid data

### Plugin States
- `parsed`: Successfully extracted from marketplace.json
- `validated`: Passed data validation checks
- `merged`: Combined with plugins from other marketplaces
- `categorized`: Assigned to appropriate category

## Constraints & Business Rules

1. **Uniqueness**: Plugin IDs must be unique across all marketplaces
2. **Completeness**: Plugins without required fields (name, description) are skipped
3. **Categorization**: All plugins must have a valid category
4. **Source Reliability**: Failed sources don't stop processing of other sources
5. **Data Freshness**: marketplace.json files are cached for 1 hour to improve performance, with fresh fetches for expired or missing cache entries

## Error Handling

- **Network Failures**: Log errors and continue with available marketplaces
- **Invalid JSON**: Skip malformed marketplace.json files
- **Missing Fields**: Skip plugins with missing required fields
- **Duplicate IDs**: Overwrite with last encountered plugin (log warning)