from __future__ import annotations

from datetime import datetime

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from services import DatabaseService
from ui.console import SEVERITY_STYLES, STYLE_INFO, STYLE_MUTED, STYLE_TABLE_H, console


def show_report(database: DatabaseService) -> None:
    console.print(Panel("[bold bright_green]Database Report[/]", border_style="bright_green"))
    console.print(_build_anomaly_table(database))
    console.print(_build_device_table(database))


def _build_anomaly_table(database: DatabaseService) -> Table:
    table = Table(title="Detected Anomalies", header_style=STYLE_TABLE_H)
    table.add_column("ID", style=STYLE_INFO)
    table.add_column("Type", style=STYLE_INFO)
    table.add_column("Severity", style=STYLE_INFO)
    table.add_column("Packet ID", style=STYLE_INFO)
    table.add_column("Detected At", style=STYLE_MUTED)
    table.add_column("Description", style=STYLE_INFO)

    anomalies = database.get_all_anomalies()
    if not anomalies:
        table.add_row("-", "-", "-", "-", "-", "No anomalies stored yet")
        return table

    for anomaly in anomalies:
        severity_style = SEVERITY_STYLES.get(anomaly.severity, STYLE_INFO)
        table.add_row(
            str(anomaly.id or "-"),
            anomaly.type,
            Text(anomaly.severity, style=severity_style),
            str(anomaly.packet_id or "-"),
            _format_datetime(anomaly.detected_at),
            anomaly.description,
        )
    return table


def _build_device_table(database: DatabaseService) -> Table:
    table = Table(title="Devices", header_style=STYLE_TABLE_H)
    table.add_column("ID", style=STYLE_INFO)
    table.add_column("IP Address", style=STYLE_INFO)
    table.add_column("Device Type", style=STYLE_INFO)
    table.add_column("Blacklisted", style=STYLE_INFO)
    table.add_column("Packet Count", style=STYLE_INFO)
    table.add_column("First Seen", style=STYLE_MUTED)
    table.add_column("Last Seen", style=STYLE_MUTED)

    devices = database.get_all_devices()

    if not devices:
        table.add_row("-", "-", "-", "-", "-", "No devices stored yet", "-")
        return table

    for device in devices:
        table.add_row(
            str(device.id or "-"),
            device.ip_address,
            device.device_type,
            "yes" if device.is_blacklisted else "no",
            str(device.packet_count),
            _format_datetime(device.first_seen),
            _format_datetime(device.last_seen),
        )
    return table


def _format_datetime(value: datetime) -> str:
    return value.isoformat(timespec="seconds")
