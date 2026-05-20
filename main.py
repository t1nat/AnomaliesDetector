import sys
from datetime import datetime, timezone

from events import EventManager
from models import Device, NetworkPacket
from services import AnomalyDetector, DatabaseService, FileLogger, TrafficAnalyzer
from services.packet_loader import PacketLoader
from simulation import TrafficSimulator
from ui.console import STYLE_HEADER, STYLE_INFO, console
from ui.i18n import set_language, t
from rich.prompt import Prompt
from ui.live_feed import LiveDetector
from ui.menu import run_menu
from ui.report import show_report
from rich.panel import Panel


def main() -> None:
    if sys.stdin.isatty():
        lang_choice = Prompt.ask("Language", choices=["en", "bg"], default="en")
        set_language(lang_choice)

    console.print(Panel(f"[bold bright_green]{t('app.title')} [/]", border_style="bright_green"))

    database = DatabaseService()
    event_manager = EventManager()
    logger = FileLogger()
    detector = AnomalyDetector(event_manager)
    live_detector = LiveDetector(detector, event_manager)
    simulator = TrafficSimulator(seed=42)
    loader = PacketLoader()

    def persist_and_log_anomaly(anomaly) -> None:
        logger.log_anomaly(anomaly)
        database.save_anomaly(anomaly)
        # Increment device anomaly count
        if anomaly.packet_id:
            database.increment_device_anomaly_count(anomaly.packet_id)

    event_manager.subscribe_anomaly_detected(persist_and_log_anomaly)
    event_manager.subscribe_ddos_suspected(logger.log_ddos_suspected)
    event_manager.subscribe_unusual_traffic(logger.log_unusual_traffic)

    def ensure_devices_for_packets(packets: list[NetworkPacket]) -> None:
        counts: dict[str, int] = {}
        for packet in packets:
            counts[packet.source_ip] = counts.get(packet.source_ip, 0) + 1

        existing_devices = {device.ip_address: device for device in database.get_all_devices()}
        for source_ip, increment in counts.items():
            existing = existing_devices.get(source_ip)
            if existing:
                existing.packet_count += increment
                existing.last_seen = datetime.now(timezone.utc)
                database.save_device(existing)
            else:
                database.save_device(
                    Device(
                        ip_address=source_ip,
                        device_type="simulated",
                        is_blacklisted=False,
                        first_seen=datetime.now(timezone.utc),
                        last_seen=datetime.now(timezone.utc),
                        packet_count=increment,
                    )
                )

    def process_packets(packets: list[NetworkPacket], title: str) -> None:
        if not packets:
            console.print(f"[bold yellow]{t('msg.no_packets_to_process')}[/]")
            return

        ensure_devices_for_packets(packets)
        for packet in packets:
            packet.device_id = database.get_device_id_by_ip(packet.source_ip)
            database.save_packet(packet)

        live_detector.run_batch(packets, 1, 1)

        analyzer = TrafficAnalyzer(packets)
        console.print(f"[bright_white]{title}[/]")
        console.print(f"[bright_white]{t('msg.packets_processed')}[/] {len(packets)}")
        console.print(f"[bright_white]{t('msg.top_ips')}[/] {analyzer.get_top_ips(3)}")
        console.print(f"[bright_white]Protocol counts:[/] {analyzer.group_by_protocol()}")

    def run_simulation() -> None:
        batches = [
            simulator.generate_normal_traffic(packet_count=25),
            simulator.generate_normal_traffic(packet_count=25),
            simulator.generate_normal_traffic(packet_count=25),
            simulator.generate_ddos_traffic("192.168.1.10", packet_count=120),
            simulator.generate_port_scan_traffic("192.168.1.55", port_count=30),
            [simulator.generate_sample_batch()[-1]],
        ]

        console.print(f"[bold bright_green]{t('msg.starting_simulation', batches=len(batches))}[/]")
        all_packets: list[NetworkPacket] = []
        all_anomalies = []

        for index, batch in enumerate(batches, start=1):
            ensure_devices_for_packets(batch)
            for packet in batch:
                packet.device_id = database.get_device_id_by_ip(packet.source_ip)
                database.save_packet(packet)
            all_packets.extend(batch)
            all_anomalies.extend(live_detector.run_batch(batch, index, len(batches)))

        analyzer = TrafficAnalyzer(all_packets)
        console.print(f"[bold bright_green]{t('msg.simulation_complete')}[/]")
        console.print(f"[bright_white]{t('msg.packets_processed')}[/] {len(all_packets)}")
        console.print(f"[bright_white]{t('msg.anomalies_detected')}[/] {len(all_anomalies)}")
        console.print(f"[bright_white]{t('msg.top_ips')}[/] {analyzer.get_top_ips(5)}")
        console.print(f"[bright_white]{t('msg.suspicious_packets')}[/] {len(analyzer.get_suspicious_packets())}")

    def clear_database() -> None:
        database.clear_all()

    try:
        if sys.stdin.isatty():
            run_menu(run_simulation, process_packets, lambda: show_report(database), clear_database, loader)
        else:
            run_simulation()
    finally:
        database.close()


if __name__ == "__main__":
    main()