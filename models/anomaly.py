from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class Anomaly:
    packet_id: int | None
    type: str
    severity: str
    description: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_resolved: bool = False
    id: int | None = None