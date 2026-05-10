from rich.console import Console

console = Console()

STYLE_HEADER = "bold bright_green"
STYLE_OK = "green"
STYLE_WARN = "bold yellow"
STYLE_ANOMALY = "bold red"
STYLE_INFO = "bright_white"
STYLE_MUTED = "dim white"
STYLE_TABLE_H = "bold cyan"

SEVERITY_STYLES = {
    "Critical": "bold red",
    "High": "yellow",
    "Medium": "cyan",
    "Low": "green",
}
