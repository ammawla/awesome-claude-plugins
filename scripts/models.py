# Marketplace scraper data models

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class Marketplace:
    """Represents a marketplace containing plugins."""
    id: str
    name: str
    description: str
    url: Optional[str] = None
    source_url: Optional[str] = None
    enabled: bool = True
    plugin_count: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Marketplace':
        """Create Marketplace from dictionary data."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            url=data.get("url"),
            source_url=data.get("source_url"),
            enabled=data.get("enabled", True)
        )

@dataclass
class Plugin:
    """Represents an individual plugin."""
    id: str
    name: str
    description: str
    category: Optional[str] = None
    marketplace_id: Optional[str] = None
    url: Optional[str] = None
    tags: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Plugin':
        """Create Plugin from dictionary data."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category"),
            marketplace_id=data.get("marketplace_id"),
            url=data.get("url"),
            tags=data.get("tags", [])
        )

@dataclass
class Source:
    """Represents a data source configuration."""
    id: str
    url: str
    format: str = "json"
    enabled: bool = True
    priority: int = 999

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Source':
        """Create Source from dictionary data."""
        return cls(
            id=data.get("id", ""),
            url=data.get("url", ""),
            format=data.get("format", "json"),
            enabled=data.get("enabled", True),
            priority=data.get("priority", 999)
        )