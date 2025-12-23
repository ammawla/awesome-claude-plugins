# CLI Command Contracts: Marketplace Scraper Scripts

**Date**: 2025-12-23
**Feature**: Marketplace Scraper Scripts

## Overview

The marketplace scraper provides three CLI commands with defined input/output contracts for programmatic usage and testing.

## Command Contracts

### 1. generate-readme

Generates README.md from configured marketplace sources.

**Command**: `python -m marketplace_scraper generate-readme [OPTIONS]`

**Input Parameters:**
```yaml
--config: string (optional, default: "config.yaml")
  Path to configuration file containing marketplace sources

--output: string (optional, default: "README.md")
  Path where generated README.md will be written

--dry-run: boolean (optional, default: false)
  If true, validate configuration and sources without writing output file
```

**Success Response (exit code 0):**
```json
{
  "status": "success",
  "message": "Successfully generated README with {marketplace_count} marketplaces and {plugin_count} plugins!",
  "data": {
    "marketplaces_processed": 12,
    "plugins_collected": 606,
    "output_file": "README.md"
  }
}
```

**Error Responses:**
- **Exit code 1**: Configuration file not found or invalid
- **Exit code 2**: Network errors or inaccessible marketplaces
- **Exit code 3**: Output file write failure

**Side Effects:**
- Creates/overwrites README.md file
- Logs processing details to stderr
- Network requests to GitHub API

### 2. validate-config

Validates configuration file format and marketplace accessibility.

**Command**: `python -m marketplace_scraper validate-config [OPTIONS]`

**Input Parameters:**
```yaml
--config: string (optional, default: "config.yaml")
  Path to configuration file to validate

--check-sources: boolean (optional, default: false)
  If true, test network connectivity to marketplace repositories
```

**Success Response (exit code 0):**
```json
{
  "status": "success",
  "message": "Configuration is valid",
  "data": {
    "sources_found": 1,
    "sources_enabled": 1,
    "marketplace_accessible": true
  }
}
```

**Error Responses:**
- **Exit code 1**: Configuration file not found
- **Exit code 2**: Invalid YAML syntax
- **Exit code 3**: Invalid source configuration
- **Exit code 4**: Network connectivity test failed

**Validation Rules:**
- YAML syntax must be valid
- Sources array must exist and contain valid URLs
- Source objects must have required fields (id, url)
- URLs must be accessible (when --check-sources is used)

### 3. list-sources

Lists configured sources with status information.

**Command**: `python -m marketplace_scraper list-sources [OPTIONS]`

**Input Parameters:**
```yaml
--config: string (optional, default: "config.yaml")
  Path to configuration file

--format: string (optional, choices: ["table", "json"], default: "table")
  Output format for source list
```

**Success Response (exit code 0):**

**Table Format (default):**
```
Configured Sources:
--------------------------------------------------
ID                URL                                           Enabled  Priority
claude-marketplaces https://raw.githubusercontent.com/...         Yes      1
```

**JSON Format:**
```json
[
  {
    "id": "claude-marketplaces",
    "name": "Claude Marketplace Sources",
    "url": "https://raw.githubusercontent.com/...",
    "enabled": true,
    "priority": 1
  }
]
```

**Error Responses:**
- **Exit code 1**: Configuration file not found or invalid

## Data Contracts

### Source Configuration Schema
```yaml
sources:
  - id: string (required)          # Unique identifier
    name: string (optional)        # Human-readable name
    url: string (required)         # HTTP/HTTPS URL to fetch marketplace data
    enabled: boolean (optional)    # Whether to process this source (default: true)
    priority: integer (optional)   # Processing order (lower = higher priority, default: 999)
```

### Marketplace Data Schema
```json
[
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "repoOwner": "string",
    "repoName": "string",
    "repoBranch": "string",
    "pluginPath": "string"
  }
]
```

### Plugin Data Schema
```json
{
  "plugins": [
    {
      "name": "string",
      "description": "string",
      "category": "string",
      "author": "string",
      "version": "string",
      "tags": ["string"],
      "homepage": "string",
      "installation": "string"
    }
  ]
}
```

## Error Handling Contract

All commands follow consistent error handling:
- **Exit codes**: 0 (success), 1-9 (specific errors)
- **Error messages**: Human-readable, logged to stderr
- **Graceful degradation**: Network failures don't crash the entire process
- **Logging levels**: INFO (progress), WARNING (recoverable issues), ERROR (fatal issues)

## Testing Contracts

### Unit Test Contracts
- **Config validation**: Invalid YAML → exit code 2
- **Source processing**: Malformed URLs → warning logged, source skipped
- **Plugin parsing**: Missing required fields → plugin skipped with warning

### Integration Test Contracts
- **End-to-end generation**: Valid config → README.md created with expected structure
- **Network failure**: Unreachable sources → partial success with warnings
- **Data validation**: Invalid marketplace.json → marketplace skipped with error logged