from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class NetworkPacket:
    source_ip: str
    dest_ip: str
    protocol: str
    size: int
    port: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    device_id: int | None = None
    id: int | None = None