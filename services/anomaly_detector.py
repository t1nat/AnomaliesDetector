from __future__ import annotations

from statistics import mean, pstdev

from events import EventManager
from models import Anomaly, NetworkPacket


class AnomalyDetector:
    def __init__(self, event_manager: EventManager) -> None:
        self._event_manager = event_manager
        self._packet_history: dict[str, list[int]] = {}

    def analyze_packets(self, packets: list[NetworkPacket]) -> list[Anomaly]:
        anomalies: list[Anomaly] = []

        packets_per_source: dict[str, list[NetworkPacket]] = {}
        ports_per_source: dict[str, set[int]] = {}

        for packet in packets:
            packets_per_source.setdefault(packet.source_ip, []).append(packet)
            ports_per_source.setdefault(packet.source_ip, set()).add(packet.port)

            if packet.size > 65_000:
                anomaly = Anomaly(
                    packet_id=packet.id,
                    type="UnusualSize",
                    severity="Medium",
                    description=f"Packet size {packet.size} bytes exceeded the unusual size threshold.",
                )
                anomalies.append(anomaly)
                self._event_manager.emit_unusual_traffic(packet)
                self._event_manager.emit_anomaly_detected(anomaly)

        for source_ip, source_packets in packets_per_source.items():
            if len(source_packets) > 100:
                anomaly = Anomaly(
                    packet_id=source_packets[-1].id,
                    type="DDoS",
                    severity="High",
                    description=f"Source IP {source_ip} generated {len(source_packets)} packets in the sample batch.",
                )
                anomalies.append(anomaly)
                self._event_manager.emit_ddos_suspected(source_ip)
                self._event_manager.emit_anomaly_detected(anomaly)

            if len(ports_per_source[source_ip]) > 20:
                anomaly = Anomaly(
                    packet_id=source_packets[-1].id,
                    type="PortScan",
                    severity="High",
                    description=f"Source IP {source_ip} touched {len(ports_per_source[source_ip])} destination ports.",
                )
                anomalies.append(anomaly)
                self._event_manager.emit_anomaly_detected(anomaly)

        anomalies.extend(self._detect_z_score_anomalies(packets_per_source))

        return anomalies

    def _detect_z_score_anomalies(self, packets_per_source: dict[str, list[NetworkPacket]]) -> list[Anomaly]:
        anomalies: list[Anomaly] = []

        for source_ip, source_packets in packets_per_source.items():
            current_count = len(source_packets)
            history = self._packet_history.setdefault(source_ip, [])

            if len(history) >= 3:
                average = mean(history)
                deviation = pstdev(history)

                if deviation > 0:
                    z_score = (current_count - average) / deviation

                    if abs(z_score) > 8:
                        severity = "Critical"
                    elif abs(z_score) > 5:
                        severity = "High"
                    elif abs(z_score) > 3:
                        severity = "Medium"
                    else:
                        severity = "Low"

                    if abs(z_score) > 3:
                        anomaly = Anomaly(
                            packet_id=source_packets[-1].id,
                            type="ZScoreAnomaly",
                            severity=severity,
                            description=f"Source IP {source_ip} deviated from its baseline with Z-score {z_score:.2f}.",
                        )
                        anomalies.append(anomaly)
                        self._event_manager.emit_anomaly_detected(anomaly)

            history.append(current_count)

        return anomalies