from __future__ import annotations

import random
from datetime import datetime, timezone

from models import NetworkPacket


class TrafficSimulator:
    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)

    def generate_normal_traffic(self, packet_count: int = 20) -> list[NetworkPacket]:
        source_ips = [f"192.168.1.{host}" for host in range(10, 21)]
        dest_ips = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]
        protocols = ["TCP", "UDP", "ICMP"]

        packets: list[NetworkPacket] = []
        for _ in range(packet_count):
            packets.append(
                NetworkPacket(
                    source_ip=self._random.choice(source_ips),
                    dest_ip=self._random.choice(dest_ips),
                    protocol=self._random.choice(protocols),
                    size=self._random.randint(64, 1500),
                    port=self._random.choice([53, 80, 443, 8080]),
                    timestamp=datetime.now(timezone.utc),
                )
            )
        return packets

    def generate_ddos_traffic(self, source_ip: str, packet_count: int = 120) -> list[NetworkPacket]:
        return [
            NetworkPacket(
                source_ip=source_ip,
                dest_ip="10.0.0.1",
                protocol="TCP",
                size=512,
                port=80,
                timestamp=datetime.now(timezone.utc),
            )
            for _ in range(packet_count)
        ]

    def generate_port_scan_traffic(self, source_ip: str, port_count: int = 30) -> list[NetworkPacket]:
        return [
            NetworkPacket(
                source_ip=source_ip,
                dest_ip="10.0.0.1",
                protocol="TCP",
                size=128,
                port=port,
                timestamp=datetime.now(timezone.utc),
            )
            for port in range(1, port_count + 1)
        ]

    def generate_sample_batch(self) -> list[NetworkPacket]:
        packets = self.generate_normal_traffic()
        packets.extend(self.generate_ddos_traffic("192.168.1.10"))
        packets.extend(self.generate_port_scan_traffic("192.168.1.55"))
        packets.append(
            NetworkPacket(
                source_ip="203.0.113.77",
                dest_ip="10.0.0.1",
                protocol="UDP",
                size=66_000,
                port=53,
                timestamp=datetime.now(timezone.utc),
            )
        )
        return packets