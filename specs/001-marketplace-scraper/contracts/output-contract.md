# Output Format Contract

## Overview
The generated README.md follows the awesome-go curated list format with structured sections and consistent formatting.

## Structure

```markdown
# Awesome Claude Plugins

Brief description of the curated list.

## Contents

- [Marketplaces](#marketplaces)
- [Audio and Music](#audio-and-music)
- [Authentication and OAuth](#authentication-and-oauth)
- [Blockchain](#blockchain)
- ...

## Marketplaces

| Marketplace | Description | URL |
|-------------|-------------|-----|
| Marketplace Name | Brief description | https://example.com |

## Category Name

### Marketplace Name

| Plugin | Description | Author | Version |
|--------|-------------|--------|---------|
| Plugin Name | Description of the plugin with key features and use cases | author | v1.0.0 |
| Another Plugin | Another description highlighting unique capabilities | author2 | v2.1.0 |

### Another Marketplace

| Plugin | Description | Author | Version |
|--------|-------------|--------|---------|
| Third Plugin | Description focusing on benefits and integration options | author3 | v0.5.0 |

## Contributing

Guidelines for contributing new marketplaces and plugins.
```

## Formatting Rules

### Headings
- `#` for main title
- `##` for major sections (Contents, Marketplaces, Categories)
- `###` for marketplace subsections within categories

### Links
- Plugin links: `[Plugin Name](url)`
- Follow GitHub repository URLs when available
- Include organization/user prefix in readable name

### Descriptions
- Keep under 200 characters
- Start with capital letter, end with period
- Highlight key features, use cases, or unique capabilities
- Use present tense for features

### Categories
- Use title case for category names
- Group related functionality together
- Maintain consistent category names across marketplaces
- Order categories logically (development workflow, then specialized tools)

### Plugin Tables
- Four columns: Plugin, Description, Author, Version
- Sort plugins alphabetically by name within each marketplace
- Include plugin name as link to repository when available
- Truncate descriptions to fit table cells (under 150 characters)
- Show version information when available, default to "latest" if not specified
- Group plugins by marketplace within each category section

## Validation Rules

- All links must be accessible (checked during generation)
- No duplicate plugin entries within same marketplace
- Categories must be from approved list
- Markdown must be valid and render correctly
- Table formatting must be consistent