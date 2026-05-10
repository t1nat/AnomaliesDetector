from __future__ import annotations

import csv
import json
import ipaddress
from datetime import datetime, timezone
from pathlib import Path

from models import NetworkPacket
from ui.console import console


class PacketLoader:
    def load_packets(self, file_path: str) -> list[NetworkPacket]:
        path = Path(file_path)
        if not path.exists():
            console.print(f"[bold yellow]File not found:[/] {path}")
            return []

        if path.suffix.lower() == ".json":
            return self._load_json(path)
        if path.suffix.lower() == ".csv":
            return self._load_csv(path)

        console.print(f"[bold yellow]Unsupported file type:[/] {path.suffix}")
        return []

    def _load_json(self, path: Path) -> list[NetworkPacket]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            console.print(f"[bold yellow]Skipping invalid JSON file:[/] {error}")
            return []

        rows = payload.get("packets", []) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            console.print("[bold yellow]JSON file must contain a list of packets.[/]")
            return []

        return self._build_packets(rows, path.name)

    def _load_csv(self, path: Path) -> list[NetworkPacket]:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return self._build_packets(rows, path.name)

    def _build_packets(self, rows: list[dict[str, object]], file_name: str) -> list[NetworkPacket]:
        packets: list[NetworkPacket] = []
        for index, row in enumerate(rows, start=1):
            packet = self._packet_from_row(row, file_name, index)
            if packet is not None:
                packets.append(packet)
        return packets

    def _packet_from_row(self, row: dict[str, object], file_name: str, row_index: int) -> NetworkPacket | None:
        try:
            source_ip = str(row["source_ip"]).strip()
            dest_ip = str(row["dest_ip"]).strip()
            protocol = str(row["protocol"]).strip().upper()
            size = int(row["size"])
            port = int(row["port"])

            ipaddress.ip_address(source_ip)
            ipaddress.ip_address(dest_ip)
            if protocol not in {"TCP", "UDP", "ICMP"}:
                raise ValueError("protocol must be TCP, UDP, or ICMP")
            if size <= 0:
                raise ValueError("size must be greater than 0")
            if port < 1 or port > 65_535:
                raise ValueError("port must be between 1 and 65535")

            timestamp = row.get("timestamp")
            if timestamp:
                timestamp_value = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            else:
                timestamp_value = datetime.now(timezone.utc)

            return NetworkPacket(
                source_ip=source_ip,
                dest_ip=dest_ip,
                protocol=protocol,
                size=size,
                port=port,
                timestamp=timestamp_value,
            )
        except (KeyError, ValueError, TypeError) as error:
            console.print(f"[bold yellow]Skipping invalid row {row_index} in {file_name}:[/] {error}")
            return None
