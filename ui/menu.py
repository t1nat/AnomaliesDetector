from __future__ import annotations

import ipaddress
from pathlib import Path
from typing import Callable

from models import NetworkPacket
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from services.packet_loader import PacketLoader
from ui.console import STYLE_HEADER, STYLE_INFO, STYLE_MUTED, STYLE_OK, STYLE_WARN, console
from ui.i18n import t


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
                "\n".join([
                    f"[bold bright_green]{t('app.title')}[/]",
                    t('menu.options'),
                ]),
                border_style="bright_green",
                title=f"[bold bright_green]{t('menu.title')}[/]",
            )
        )

        choice = Prompt.ask(f"[bold bright_white]{t('prompt.choice')}[/]", choices=["1", "2", "3", "4", "5", "6"], default="1")

        if choice == "1":
            run_simulation()
        elif choice == "2":
            packet = _prompt_for_packet()
            process_packets([packet], "manual packet")
        elif choice == "3":
            file_path = _resolve_data_path(Prompt.ask(t('prompt.file_name'), default="sample_packets.json"))
            packets = loader.load_packets(str(file_path))
            if packets:
                process_packets(packets, f"file: {file_path.name}")
            else:
                console.print(f"[bold yellow]{t('msg.no_valid_packets')}[/]")
        elif choice == "4":
            show_report()
        elif choice == "5":
            if Confirm.ask(t('confirm.clear_db'), default=False):
                clear_database()
                console.print(f"[green]{t('msg.database_cleared')}[/]")
        elif choice == "6":
            console.print(f"[dim white]{t('msg.exiting')}[/]")
            break


def _prompt_for_packet() -> NetworkPacket:
    source_ip = _prompt_ip(t("prompt.source_ip"))
    dest_ip = _prompt_ip(t("prompt.dest_ip"))
    protocol = Prompt.ask(t("prompt.protocol"), choices=["TCP", "UDP", "ICMP"], default="TCP")
    size = IntPrompt.ask(t("prompt.size"), default=512, show_default=True)
    while size <= 0:
        console.print(f"[bold yellow]{t('err.size_positive')}[/]")
        size = IntPrompt.ask(t("prompt.size"), default=512, show_default=True)
    port = IntPrompt.ask(t("prompt.port"), default=80, show_default=True)
    while port < 1 or port > 65_535:
        console.print(f"[bold yellow]{t('err.port_range')}[/]")
        port = IntPrompt.ask(t("prompt.port"), default=80, show_default=True)

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
                console.print(f"[bold yellow]{t('err.invalid_ip')}[/]")


def _resolve_data_path(file_name: str) -> Path:
    candidate = Path(file_name)
    if candidate.exists():
        return candidate

    data_candidate = Path("data") / file_name
    if data_candidate.exists():
        return data_candidate

    return candidate
