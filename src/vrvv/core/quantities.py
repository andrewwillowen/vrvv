"""
Base units and conversions of physical quantities.
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class StandardData:
    """Canonical placeholder container for normalized ingest outputs."""

    metadata: dict[str, object] = field(default_factory=dict)
