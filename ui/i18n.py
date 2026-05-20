from __future__ import annotations

from typing import Any

_LANG = "en"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app.title": "Network Anomaly Detection System",
        "menu.title": "Menu",
        "menu.options": "[bright_white]1[/]  Run simulation (auto)\n[bright_white]2[/]  Add packet manually (type it)\n[bright_white]3[/]  Load packets from file (JSON/CSV)\n[bright_white]4[/]  Show database report\n[bright_white]5[/]  Clear database\n[bright_white]6[/]  Exit",
        "prompt.choice": ">",
        "prompt.file_name": "File name",
        "confirm.clear_db": "Clear all database records?",
        "msg.no_valid_packets": "No valid packets were loaded.",
        "msg.database_cleared": "Database cleared.",
        "msg.exiting": "Exiting...",
        "prompt.source_ip": "Source IP",
        "prompt.dest_ip": "Dest IP",
        "prompt.protocol": "Protocol [TCP/UDP/ICMP]",
        "prompt.size": "Size (bytes)",
        "err.size_positive": "Size must be greater than 0.",
        "prompt.port": "Port",
        "err.port_range": "Port must be between 1 and 65535.",
        "err.invalid_ip": "Enter a valid IP address.",
        "live.rule.size_check": "  [RULE] Size check (> {value} B)      {status_tag}  {status_text}",
        "live.rule.ddos_check": "  [RULE] DDoS check (> {threshold} pkt/IP)    {status_tag}  {ip_info}",
        "live.rule.port_scan": "  [RULE] Port scan (> {threshold} ports/IP)   {status_tag}  {ip_info}",
        "live.zscore.no_packets": "  [Z-SCORE] Baseline                  [dim white]✓[/]  no packets",
        "live.zscore.building": "  [Z-SCORE] Baseline                  [dim white]✓[/]  building history ({current}/{needed})",
        "live.zscore.anomaly": "  [Z-SCORE] Baseline                  [bold red]✗[/]  ANOMALY FIRED  {severity}",
        "live.zscore.clean": "  [Z-SCORE] Baseline                  [green]✓[/]  clean  count={count}",
        "live.no_anomalies": "  [green]✓ No anomalies detected[/]",
        "live.anomaly_fired_line": "  [bold red]✗ ANOMALY FIRED[/]  {type} | {severity} | {description}",
        "report.title": "Database Report",
        "report.anomalies.title": "Detected Anomalies",
        "report.anomalies.none": "No anomalies stored yet",
        "report.devices.title": "Devices",
        "report.devices.none": "No devices stored yet",
        "report.yes": "yes",
        "report.no": "no",
        "msg.no_packets_to_process": "No packets to process.",
        "msg.starting_simulation": "Starting simulation — {batches} batches",
        "msg.simulation_complete": "Simulation complete",
        "msg.packets_processed": "Packets processed:",
        "msg.anomalies_detected": "Anomalies detected:",
        "msg.top_ips": "Top IPs:",
        "msg.suspicious_packets": "Suspicious packets:",
    },
    "bg": {
        "app.title": "Система за откриване на мрежови аномалии",
        "menu.title": "Меню",
        "menu.options": "[bright_white]1[/]  Стартирай симулация (автоматично)\n[bright_white]2[/]  Добави пакет ръчно (въведи)\n[bright_white]3[/]  Зареди пакети от файл (JSON/CSV)\n[bright_white]4[/]  Покажи отчет от базата\n[bright_white]5[/]  Изчисти базата\n[bright_white]6[/]  Изход",
        "prompt.choice": ">",
        "prompt.file_name": "Име на файл",
        "confirm.clear_db": "Да се изчистят ли всички записи от базата?",
        "msg.no_valid_packets": "Не бяха заредени валидни пакети.",
        "msg.database_cleared": "Базата е изчистена.",
        "msg.exiting": "Изход...",
        "prompt.source_ip": "Източник IP",
        "prompt.dest_ip": "Дестинация IP",
        "prompt.protocol": "Протокол [TCP/UDP/ICMP]",
        "prompt.size": "Размер (байт)",
        "err.size_positive": "Размерът трябва да е по-голям от 0.",
        "prompt.port": "Порт",
        "err.port_range": "Портът трябва да е между 1 и 65535.",
        "err.invalid_ip": "Въведете валиден IP адрес.",
        "live.rule.size_check": "  [ПРАВИЛО] Проверка размер (> {value} B)      {status_tag}  {status_text}",
        "live.rule.ddos_check": "  [ПРАВИЛО] DDoS проверка (> {threshold} пакета/IP)    {status_tag}  {ip_info}",
        "live.rule.port_scan": "  [ПРАВИЛО] Проверка портове (> {threshold} порта/IP)   {status_tag}  {ip_info}",
        "live.zscore.no_packets": "  [Z-SCORE] Базова линия                  [dim white]✓[/]  няма пакети",
        "live.zscore.building": "  [Z-SCORE] Базова линия                  [dim white]✓[/]  изграждане на история ({current}/{needed})",
        "live.zscore.anomaly": "  [Z-SCORE] Базова линия                  [bold red]✗[/]  АНОМАЛИЯ  {severity}",
        "live.zscore.clean": "  [Z-SCORE] Базова линия                  [green]✓[/]  чисто  брой={count}",
        "live.no_anomalies": "  [green]✓ Няма открити аномалии[/]",
        "live.anomaly_fired_line": "  [bold red]✗ АНОМАЛИЯ[/]  {type} | {severity} | {description}",
        "report.title": "Отчет от базата",
        "report.anomalies.title": "Открити аномалии",
        "report.anomalies.none": "Все още няма записани аномалии",
        "report.devices.title": "Устройства",
        "report.devices.none": "Все още няма записани устройства",
        "report.yes": "да",
        "report.no": "не",
        "msg.no_packets_to_process": "Няма пакети за обработка.",
        "msg.starting_simulation": "Стартиране на симулация — {batches} партиди",
        "msg.simulation_complete": "Симулацията завърши",
        "msg.packets_processed": "Обработени пакети:",
        "msg.anomalies_detected": "Открити аномалии:",
        "msg.top_ips": "Топ IP адреси:",
        "msg.suspicious_packets": "Съмнителни пакети:",
    },
}


def set_language(lang: str) -> None:
    global _LANG
    if lang not in TRANSLATIONS:
        raise ValueError(f"Unknown language: {lang}")
    _LANG = lang


def get_language() -> str:
    return _LANG


def t(key: str, **kwargs: Any) -> str:
    text = TRANSLATIONS.get(_LANG, {}).get(key) or TRANSLATIONS["en"].get(key, key)
    try:
        return text.format(**kwargs)
    except Exception:
        return text
