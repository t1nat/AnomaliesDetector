from __future__ import annotations

from pathlib import Path

from models import Anomaly, NetworkPacket


class FileLogger:
    def __init__(self, file_path: str = "log.txt") -> None:
        self._path = Path(file_path)

    def log_anomaly(self, anomaly: Anomaly) -> None:
        self._append(f"ANOMALY | {anomaly.detected_at.isoformat()} | {anomaly.type} | {anomaly.severity} | {anomaly.description}")

    def log_ddos_suspected(self, source_ip: str) -> None:
        self._append(f"DDoS | source_ip={source_ip}")

    def log_unusual_traffic(self, packet: NetworkPacket) -> None:
        self._append(
            f"TRAFFIC | {packet.timestamp.isoformat()} | {packet.source_ip} -> {packet.dest_ip} | {packet.protocol} | size={packet.size} | port={packet.port}"
        )

    def _append(self, message: str) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(message + "\n")