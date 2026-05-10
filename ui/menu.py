from __future__ import annotations

import ipaddress
from pathlib import Path
from typing import Callable

from models import NetworkPacket
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from services.packet_loader import PacketLoader
from ui.console import STYLE_HEADER, STYLE_INFO, STYLE_MUTED, STYLE_OK, STYLE_WARN, console


def run_menu(
    run_simulation: Callable[[], None],
    process_packets: Callable[[list[NetworkPacket], str], None],
    show_report: Callable[[], None],
    clear_database: Callable[[], None],
    loader: PacketLoader,
) -> None:
    while True:
        console.print(
            Panel(
                "\n".join(
                    [
                        "[bold bright_green]Network Anomaly Detection System[/]",
                        "[bright_white]1[/]  Run simulation (auto)",
                        "[bright_white]2[/]  Add packet manually (type it)",
                        "[bright_white]3[/]  Load packets from file (JSON/CSV)",
                        "[bright_white]4[/]  Show database report",
                        "[bright_white]5[/]  Clear database",
                        "[bright_white]6[/]  Exit",
                    ]
                ),
                border_style="bright_green",
                title="[bold bright_green]Menu[/]",
            )
        )

        choice = Prompt.ask("[bold bright_white]>[/]", choices=["1", "2", "3", "4", "5", "6"], default="1")

        if choice == "1":
            run_simulation()
        elif choice == "2":
            packet = _prompt_for_packet()
            process_packets([packet], "manual packet")
        elif choice == "3":
            file_path = _resolve_data_path(Prompt.ask("File name", default="sample_packets.json"))
            packets = loader.load_packets(str(file_path))
            if packets:
                process_packets(packets, f"file: {file_path.name}")
            else:
                console.print("[bold yellow]No valid packets were loaded.[/]")
        elif choice == "4":
            show_report()
        elif choice == "5":
            if Confirm.ask("Clear all database records?", default=False):
                clear_database()
                console.print("[green]Database cleared.[/]")
        elif choice == "6":
            console.print("[dim white]Exiting...[/]")
            break


def _prompt_for_packet() -> NetworkPacket:
    source_ip = _prompt_ip("Source IP")
    dest_ip = _prompt_ip("Dest IP")
    protocol = Prompt.ask("Protocol [TCP/UDP/ICMP]", choices=["TCP", "UDP", "ICMP"], default="TCP")
    size = IntPrompt.ask("Size (bytes)", default=512, show_default=True)
    while size <= 0:
        console.print("[bold yellow]Size must be greater than 0.[/]")
        size = IntPrompt.ask("Size (bytes)", default=512, show_default=True)
    port = IntPrompt.ask("Port", default=80, show_default=True)
    while port < 1 or port > 65_535:
        console.print("[bold yellow]Port must be between 1 and 65535.[/]")
        port = IntPrompt.ask("Port", default=80, show_default=True)

    return NetworkPacket(
        source_ip=source_ip,
        dest_ip=dest_ip,
        protocol=protocol,
        size=size,
        port=port,
    )


def _prompt_ip(label: str) -> str:
    while True:
        value = Prompt.ask(label)
        try:
            ipaddress.ip_address(value)
            return value
        except ValueError:
            console.print("[bold yellow]Enter a valid IP address.[/]")


def _resolve_data_path(file_name: str) -> Path:
    candidate = Path(file_name)
    if candidate.exists():
        return candidate

    data_candidate = Path("data") / file_name
    if data_candidate.exists():
        return data_candidate

    return candidate
