# Quick Start: Marketplace Scraper Scripts

**Date**: 2025-12-23
**Feature**: Marketplace Scraper Scripts

## Overview

The marketplace scraper is a Python CLI tool that fetches Claude marketplace and plugin data from configured sources and generates a curated README.md with organized tables of marketplaces and categorized plugins.

## Prerequisites

- Python 3.8 or higher
- `pip` package manager
- Internet connection (for fetching marketplace data)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/awesome-claude-plugins.git
   cd awesome-claude-plugins
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python scripts/marketplace_scraper.py --help
   ```

## Quick Start

### 1. Basic Usage

Generate a README from the default configuration:

```bash
python scripts/marketplace_scraper.py generate-readme
```

This will:
- Read `config.yaml` for marketplace sources
- Fetch marketplace and plugin data from GitHub
- Generate `README.md` with organized plugin listings

### 2. Validate Configuration

Before generating, validate your configuration:

```bash
python scripts/marketplace_scraper.py validate-config
```

Test network connectivity to sources:

```bash
python scripts/marketplace_scraper.py validate-config --check-sources
```

### 3. List Available Sources

View configured marketplace sources:

```bash
python scripts/marketplace_scraper.py list-sources
```

Get sources in JSON format:

```bash
python scripts/marketplace_scraper.py list-sources --format json
```

## Configuration

### Basic Configuration

Create a `config.yaml` file:

```yaml
sources:
  - id: my-marketplace
    name: My Claude Marketplace
    url: https://raw.githubusercontent.com/myorg/marketplace-data/main/marketplaces.json
    enabled: true
    priority: 1
```

### Advanced Configuration

```yaml
sources:
  - id: official-marketplace
    name: Official Claude Plugins
    url: https://api.github.com/repos/anthropics/claude-plugins/contents/marketplaces
    enabled: true
    priority: 1

  - id: community-marketplace
    name: Community Plugins
    url: https://raw.githubusercontent.com/community/claude-plugins/main/marketplaces.json
    enabled: true
    priority: 2

  - id: disabled-source
    name: Experimental Plugins
    url: https://example.com/experimental.json
    enabled: false  # Skip this source
    priority: 99
```

## Examples

### Generate README with Custom Output

```bash
python scripts/marketplace_scraper.py generate-readme --output docs/plugins.md
```

### Dry Run (Validate Without Writing)

```bash
python scripts/marketplace_scraper.py generate-readme --dry-run
```

### Use Custom Configuration

```bash
python scripts/marketplace_scraper.py --config my-config.yaml generate-readme
```

## Expected Output

After successful execution, you'll see output like:

```
Successfully generated README with 12 marketplaces and 606 plugins!
```

The generated `README.md` will contain:

- **Table of Contents** with category links
- **Marketplaces Table** listing all discovered marketplaces
- **Categorized Plugin Sections** with tables showing:
  - Plugin name (linked to repository)
  - Description
  - Author
  - Version

## Troubleshooting

### Common Issues

**"Config file config.yaml not found"**
- Ensure you're running from the repository root
- Create a `config.yaml` file with marketplace sources

**"No marketplaces found"**
- Check your source URLs are accessible
- Verify the JSON format matches expected structure
- Use `validate-config --check-sources` to test connectivity

**"Network timeout errors"**
- The tool handles network issues gracefully
- Check your internet connection
- Some marketplaces may be temporarily unavailable

### Debug Mode

Enable verbose logging:

```bash
python scripts/marketplace_scraper.py --verbose generate-readme
```

## Integration Examples

### CI/CD Pipeline

Add to your GitHub Actions workflow:

```yaml
- name: Update Plugin README
  run: |
    python scripts/marketplace_scraper.py generate-readme
    git add README.md
    git commit -m "Update plugin listings" || true
```

### Scheduled Updates

Use cron for regular updates:

```bash
# Update every Monday at 9 AM
0 9 * * 1 cd /path/to/repo && python scripts/marketplace_scraper.py generate-readme
```

## Development

### Running Tests

```bash
# Unit tests
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# All tests
python -m pytest tests/ -v
```

### Adding New Sources

1. Add source configuration to `config.yaml`
2. Test with `validate-config --check-sources`
3. Generate README to verify data parsing
4. Commit changes

## Support

- Check the generated logs for detailed error information
- Validate your `config.yaml` syntax with an online YAML validator
- Ensure marketplace repositories follow the expected `marketplace.json` format