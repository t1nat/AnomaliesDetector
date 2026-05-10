from __future__ import annotations

from collections.abc import Callable

from models import Anomaly, NetworkPacket


class EventManager:
    def __init__(self) -> None:
        self._anomaly_detected_subscribers: list[Callable[[Anomaly], None]] = []
        self._ddos_suspected_subscribers: list[Callable[[str], None]] = []
        self._unusual_traffic_subscribers: list[Callable[[NetworkPacket], None]] = []

    def subscribe_anomaly_detected(self, callback: Callable[[Anomaly], None]) -> None:
        self._anomaly_detected_subscribers.append(callback)

    def subscribe_ddos_suspected(self, callback: Callable[[str], None]) -> None:
        self._ddos_suspected_subscribers.append(callback)

    def subscribe_unusual_traffic(self, callback: Callable[[NetworkPacket], None]) -> None:
        self._unusual_traffic_subscribers.append(callback)

    def emit_anomaly_detected(self, anomaly: Anomaly) -> None:
        for subscriber in self._anomaly_detected_subscribers:
            subscriber(anomaly)

    def emit_ddos_suspected(self, source_ip: str) -> None:
        for subscriber in self._ddos_suspected_subscribers:
            subscriber(source_ip)

    def emit_unusual_traffic(self, packet: NetworkPacket) -> None:
        for subscriber in self._unusual_traffic_subscribers:
            subscriber(packet)