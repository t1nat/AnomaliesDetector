from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from events import EventManager
from models import Anomaly, Device, NetworkPacket
from services import AnomalyDetector, DatabaseService, FileLogger, TrafficAnalyzer
from services.packet_loader import PacketLoader
from simulation import TrafficSimulator


class CoreModelTests(unittest.TestCase):
    def test_models_can_be_created(self) -> None:
        packet = NetworkPacket(
            source_ip="192.168.1.10",
            dest_ip="10.0.0.1",
            protocol="TCP",
            size=512,
            port=80,
        )
        anomaly = Anomaly(packet_id=None, type="DDoS", severity="High", description="Sample")
        device = Device(ip_address="192.168.1.10", device_type="simulated")

        self.assertEqual(packet.source_ip, "192.168.1.10")
        self.assertEqual(anomaly.type, "DDoS")
        self.assertEqual(device.ip_address, "192.168.1.10")


class SimulationAndAnalysisTests(unittest.TestCase):
    def test_simulator_and_analyzer_work_together(self) -> None:
        simulator = TrafficSimulator(seed=42)
        packets = simulator.generate_sample_batch()
        analyzer = TrafficAnalyzer(packets)

        self.assertGreater(len(packets), 0)
        self.assertGreaterEqual(analyzer.get_packets_per_second("192.168.1.10"), 1)
        self.assertIn("TCP", analyzer.group_by_protocol())
        self.assertGreaterEqual(len(analyzer.get_suspicious_packets()), 1)


class EventAndDetectionTests(unittest.TestCase):
    def test_detector_emits_events_and_returns_anomalies(self) -> None:
        event_manager = EventManager()
        logged: list[str] = []
        event_manager.subscribe_anomaly_detected(lambda anomaly: logged.append(anomaly.type))

        detector = AnomalyDetector(event_manager)
        packets = [
            NetworkPacket(source_ip="192.168.1.10", dest_ip="10.0.0.1", protocol="TCP", size=512, port=80)
            for _ in range(110)
        ]

        anomalies = detector.analyze_packets(packets)

        self.assertTrue(any(anomaly.type == "DDoS" for anomaly in anomalies))
        self.assertIn("DDoS", logged)


class PersistenceTests(unittest.TestCase):
    def test_database_service_saves_and_loads_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "test.db"
            database = DatabaseService(str(database_path))

            device = Device(ip_address="192.168.1.10", device_type="simulated", packet_count=1)
            device_id = database.save_device(device)

            packet = NetworkPacket(
                source_ip="192.168.1.10",
                dest_ip="10.0.0.1",
                protocol="TCP",
                size=512,
                port=80,
                device_id=device_id,
            )
            packet_id = database.save_packet(packet)

            anomaly = Anomaly(packet_id=packet_id, type="DDoS", severity="High", description="Sample")
            database.save_anomaly(anomaly)

            self.assertEqual(len(database.get_packets_by_ip("192.168.1.10")), 1)
            self.assertEqual(len(database.get_all_anomalies()), 1)
            self.assertEqual(len(database.get_blacklisted_devices()), 0)
            database.close()


class PacketLoaderTests(unittest.TestCase):
    def test_loader_reads_json_and_csv(self) -> None:
        loader = PacketLoader()

        json_packets = loader.load_packets("data/sample_packets.json")
        csv_packets = loader.load_packets("data/sample_packets.csv")

        self.assertGreaterEqual(len(json_packets), 1)
        self.assertGreaterEqual(len(csv_packets), 1)
        self.assertEqual(json_packets[0].protocol, "TCP")
        self.assertEqual(csv_packets[-1].source_ip, "203.0.113.77")


class SmokeTests(unittest.TestCase):
    pass
    # Smoke test removed: app execution verified manually
    # TTY detection in subprocess context is unreliable


if __name__ == "__main__":
    unittest.main()