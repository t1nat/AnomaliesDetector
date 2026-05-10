from __future__ import annotations

from collections import Counter, defaultdict

from models import NetworkPacket


class TrafficAnalyzer:
    def __init__(self, packets: list[NetworkPacket]) -> None:
        self._packets = packets

    def get_top_ips(self, count: int) -> list[tuple[str, int]]:
        source_counts = Counter(packet.source_ip for packet in self._packets)
        return source_counts.most_common(count)

    def group_by_protocol(self) -> dict[str, int]:
        grouped: dict[str, int] = defaultdict(int)
        for packet in self._packets:
            grouped[packet.protocol] += 1
        return dict(grouped)

    def get_suspicious_packets(self) -> list[NetworkPacket]:
        return [packet for packet in self._packets if packet.size > 65_000]

    def get_packets_per_second(self, source_ip: str) -> int:
        return sum(1 for packet in self._packets if packet.source_ip == source_ip)