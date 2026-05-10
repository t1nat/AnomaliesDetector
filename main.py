from datetime import datetime, timezone

from events import EventManager
from models import Device
from services import AnomalyDetector, DatabaseService, FileLogger, TrafficAnalyzer
from simulation import TrafficSimulator


def main() -> None:
    simulator = TrafficSimulator(seed=42)
    batches = [
        simulator.generate_normal_traffic(packet_count=25),
        simulator.generate_normal_traffic(packet_count=25),
        simulator.generate_normal_traffic(packet_count=25),
        simulator.generate_ddos_traffic("192.168.1.10", packet_count=120),
        simulator.generate_port_scan_traffic("192.168.1.55", port_count=30),
        [
            simulator.generate_sample_batch()[-1],
        ],
    ]

    packets = [packet for batch in batches for packet in batch]

    database = DatabaseService()

    for source_ip in sorted({packet.source_ip for packet in packets}):
        database.save_device(
            Device(
                ip_address=source_ip,
                device_type="simulated",
                is_blacklisted=False,
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                packet_count=sum(1 for packet in packets if packet.source_ip == source_ip),
            )
        )

    event_manager = EventManager()
    logger = FileLogger()

    def persist_and_log_anomaly(anomaly) -> None:
        logger.log_anomaly(anomaly)
        database.save_anomaly(anomaly)

    event_manager.subscribe_anomaly_detected(persist_and_log_anomaly)
    event_manager.subscribe_ddos_suspected(logger.log_ddos_suspected)
    event_manager.subscribe_unusual_traffic(logger.log_unusual_traffic)

    detector = AnomalyDetector(event_manager)
    anomalies = []

    try:
        for batch in batches:
            for packet in batch:
                packet.device_id = database.get_device_id_by_ip(packet.source_ip)
                database.save_packet(packet)
            anomalies.extend(detector.analyze_packets(batch))

        analyzer = TrafficAnalyzer(packets)

        print("Network Anomaly Detection System")
        print(f"Packets processed: {len(packets)}")
        print(f"Anomalies detected: {len(anomalies)}")
        print(f"Top IPs: {analyzer.get_top_ips(3)}")
        print(f"Protocol counts: {analyzer.group_by_protocol()}")
        print(f"Suspicious packets: {len(analyzer.get_suspicious_packets())}")
    finally:
        database.close()


if __name__ == "__main__":
    main()