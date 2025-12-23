# Configuration Contract

## Overview
The config.yaml file defines data sources and generation settings for the marketplace scraper.

## Schema

```yaml
# Configuration file for marketplace scraper
version: "1.0"

# Data sources configuration
sources:
  - id: "primary-source"
    url: "https://example.com/marketplaces.json"
    format: "json"
    enabled: true
    priority: 1
    timeout: 30  # seconds

  - id: "secondary-source"
    url: "https://another.com/plugins.json"
    format: "json"
    enabled: true
    priority: 2

# Generation settings
generation:
  output_file: "README.md"
  template_dir: "templates"
  category_order:
    - "Code Analysis"
    - "Testing"
    - "Documentation"
    - "Development Tools"
  include_marketplace_tables: true
  include_plugin_categories: true

# Validation settings
validation:
  require_categories: true
  max_description_length: 500
  allowed_formats: ["json"]

# Logging settings
logging:
  level: "INFO"
  file: "scraper.log"
```

## Field Descriptions

### sources (required)
Array of data source configurations.

**Fields:**
- `id`: Unique identifier for the source
- `url`: HTTP/HTTPS URL to fetch data from
- `format`: Data format (currently only "json" supported)
- `enabled`: Whether to include this source (default: true)
- `priority`: Processing order, lower numbers first (default: 999)
- `timeout`: Request timeout in seconds (default: 30)

### generation (optional)
Settings for README generation.

**Fields:**
- `output_file`: Path for generated README (default: "README.md")
- `template_dir`: Directory containing Jinja2 templates
- `category_order`: Preferred order of plugin categories
- `include_marketplace_tables`: Generate marketplace overview table
- `include_plugin_categories`: Organize plugins by categories

### validation (optional)
Data validation rules.

**Fields:**
- `require_categories`: Require category field for all plugins
- `max_description_length`: Maximum description length
- `allowed_formats`: List of supported data formats

### logging (optional)
Logging configuration.

**Fields:**
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `file`: Log file path (default: console only)