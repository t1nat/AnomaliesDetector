from __future__ import annotations

from collections import Counter

from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn

from events import EventManager
from models import Anomaly, NetworkPacket
from services import AnomalyDetector
from ui.console import (
    STYLE_ANOMALY,
    STYLE_HEADER,
    STYLE_INFO,
    STYLE_MUTED,
    STYLE_OK,
    STYLE_WARN,
    console,
)
from ui.i18n import t


class LiveDetector:
    def __init__(self, detector: AnomalyDetector, event_manager: EventManager) -> None:
        self._detector = detector
        self._event_manager = event_manager

    def run_batch(self, packets: list[NetworkPacket], batch_index: int, total_batches: int) -> list[Anomaly]:
        console.print()
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=36, complete_style="green", finished_style="green"),
            TextColumn("{task.completed}/{task.total}"),
            TextColumn("[bright_white]{task.fields[count]} packets"),
            TextColumn("[dim white]{task.fields[elapsed]}"),
            TimeElapsedColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"[bold bright_green]Batch {batch_index}/{total_batches}",
                total=100,
                count=len(packets),
                elapsed="",
            )
            progress.update(task, completed=100, elapsed="done")

        console.print(f"[bold bright_green]Batch {batch_index}/{total_batches}[/]  [bright_white]{len(packets)} packets[/]")
        self._print_rule_checks(packets)
        anomalies = self._detector.analyze_packets(packets)
        self._print_z_score_status(packets, anomalies)
        self._print_anomaly_summary(anomalies)
        return anomalies

    def _print_rule_checks(self, packets: list[NetworkPacket]) -> None:
        counts = Counter(packet.source_ip for packet in packets)
        ports_by_ip: dict[str, set[int]] = {}
        for packet in packets:
            ports_by_ip.setdefault(packet.source_ip, set()).add(packet.port)

        if any(packet.size > 65_000 for packet in packets):
            console.print(t("live.rule.size_check", value=65000, status_tag="[bold yellow]⚠[/]", status_text="threshold hit"))
        else:
            console.print(t("live.rule.size_check", value=65000, status_tag="[green]✓[/]", status_text="clean"))

        top_source_ip, top_count = counts.most_common(1)[0]
        if top_count > 100:
            console.print(t("live.rule.ddos_check", threshold=100, status_tag="[bold yellow]⚠[/]", ip_info=f"{top_source_ip} → {top_count} packets"))
        else:
            console.print(t("live.rule.ddos_check", threshold=100, status_tag="[green]✓[/]", ip_info="clean"))

        port_scan_target = None
        for source_ip, port_set in ports_by_ip.items():
            if len(port_set) > 20:
                port_scan_target = (source_ip, len(port_set))
                break

        if port_scan_target:
            console.print(
                t("live.rule.port_scan", threshold=20, status_tag="[bold yellow]⚠[/]", ip_info=f"{port_scan_target[0]} → {port_scan_target[1]} ports")
            )
        else:
            console.print(t("live.rule.port_scan", threshold=20, status_tag="[green]✓[/]", ip_info="clean"))

    def _print_z_score_status(self, packets: list[NetworkPacket], anomalies: list[Anomaly]) -> None:
        counts = Counter(packet.source_ip for packet in packets)
        if not counts:
            console.print(t("live.zscore.no_packets"))
            return

        source_ip, current_count = counts.most_common(1)[0]
        history = self._detector._packet_history.get(source_ip, [])

        if len(history) < 3:
            console.print(t("live.zscore.building", current=len(history), needed=3))
            return

        anomaly = next((item for item in anomalies if item.type == "ZScoreAnomaly"), None)
        if anomaly:
            console.print(t("live.zscore.anomaly", severity=anomaly.severity))
        else:
            console.print(t("live.zscore.clean", count=current_count))

    def _print_anomaly_summary(self, anomalies: list[Anomaly]) -> None:
        if not anomalies:
            console.print(t("live.no_anomalies"))
            return

        for anomaly in anomalies:
            console.print(t("live.anomaly_fired_line", type=anomaly.type, severity=anomaly.severity, description=anomaly.description))
