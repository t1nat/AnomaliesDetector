# Refactor Plan — Network Anomaly Detector TUI v2

## What changes and why

The current system runs silently and prints 5 lines at the end.
This refactor adds:

- A **menu** to choose what to run, add data manually, or load from file
- **Both input methods** — type a packet in the menu OR drop a JSON/CSV file and load it
- **Live step-by-step output** during detection using `rich`
- A **cybersecurity dark theme** — green for clean, red/yellow for anomalies, white for info
- A `data/` folder with ready-to-edit sample files and instructions
- A `docs/manual-data/` folder explaining exactly what to put where

The existing service logic stays **untouched**. Only `main.py` changes. Everything new goes in `ui/`, `data/`, and `services/packet_loader.py`.

---

## New folder structure

```
NetworkAnomalyDetector/
├── models/                          ← no changes
├── services/
│   └── packet_loader.py             ← NEW — loads JSON/CSV from data/ folder
├── events/                          ← no changes
├── simulation/                      ← no changes
├── ui/                              ← NEW — all TUI display logic
│   ├── __init__.py
│   ├── console.py                   ← rich Console + color theme constants
│   ├── menu.py                      ← interactive main menu
│   ├── live_feed.py                 ← real-time detection output
│   └── report.py                    ← final summary tables
├── data/                            ← NEW — manual input files
│   ├── sample_packets.json          ← ready-to-edit JSON example
│   ├── sample_packets.csv           ← ready-to-edit CSV example
│   └── README.md                    ← quick reference for the data format
├── docs/
│   └── manual-data/                 ← NEW
│       ├── how-to-add-packets.md    ← step-by-step for file input
│       └── how-to-add-via-menu.md   ← step-by-step for menu input
├── main.py                          ← rewritten to use ui/ and packet_loader
├── requirements.txt                 ← add: rich
└── tests/                           ← no changes
```

---

## New dependency

```
rich>=13.0
```

Install: `pip install rich`

---

## Color theme — cybersecurity dark

All colors defined once in `ui/console.py`, imported everywhere else.

| Element | Color | Used for |
|---|---|---|
| Header / banner | `bold bright_green` | title, batch headers |
| Clean result | `green` | ✓ No anomalies |
| Rule trigger | `bold yellow` | ⚠ threshold hit |
| Anomaly confirmed | `bold red` | ✗ ANOMALY FIRED |
| Info / neutral | `bright_white` | packet counts, IPs |
| Muted | `dim white` | timestamps, descriptions |
| Progress bar | `green` on `dark_green` | batch progress |
| Table header | `bold cyan` | column names |
| Severity Critical | `bold red` | report table |
| Severity High | `yellow` | report table |
| Severity Medium | `cyan` | report table |
| Severity Low | `green` | report table |

---

## What each new file does

### `ui/console.py`

Single shared `Console()` instance + all style constants.
Every UI file imports from here — no hardcoded colors anywhere else.

```python
from rich.console import Console

console = Console()

STYLE_HEADER  = "bold bright_green"
STYLE_OK      = "green"
STYLE_WARN    = "bold yellow"
STYLE_ANOMALY = "bold red"
STYLE_INFO    = "bright_white"
STYLE_MUTED   = "dim white"
STYLE_TABLE_H = "bold cyan"

SEVERITY_STYLES = {
    "Critical": "bold red",
    "High":     "yellow",
    "Medium":   "cyan",
    "Low":      "green",
}
```

---

### `ui/menu.py`

Main menu loop in a `rich.panel.Panel` with green border.

```
╔══════════════════════════════════════════╗
║   Network Anomaly Detection System       ║
║   1  Run simulation (auto)               ║
║   2  Add packet manually (type it)       ║
║   3  Load packets from file (JSON/CSV)   ║
║   4  Show database report                ║
║   5  Clear database                      ║
║   6  Exit                                ║
╚══════════════════════════════════════════╝
```

Option 1 → calls `run_simulation()`, uses `live_feed.py`
Option 2 → prompts for each field, creates `NetworkPacket`, runs detection
Option 3 → asks for filename, loads via `packet_loader.py`, runs detection
Option 4 → calls `ui/report.py`
Option 5 → confirms then wipes DB
Option 6 → exits

Option 2 prompts:
```
Source IP            : 192.168.1.99
Dest IP              : 10.0.0.1
Protocol [TCP/UDP/ICMP]: TCP
Size (bytes)         : 512
Port                 : 80
```

Validation: IP checked with `ipaddress` stdlib, size must be int > 0, protocol must be TCP/UDP/ICMP.

---

### `ui/live_feed.py`

Shows each rule check as it runs with a `rich.progress` bar per batch.

Clean batch output:
```
  Batch 1 / 6  ━━━━━━━━━━━━━━━━━━━━━━━━━━  100%  25 packets

  [RULE] Size check (> 65 000 B)       ✓  clean
  [RULE] DDoS check (> 100 pkt/IP)     ✓  clean
  [RULE] Port scan (> 20 ports/IP)     ✓  clean
  [Z-SCORE] Baseline                   ✓  building history (1/3)
```

When a check triggers:
```
  Batch 4 / 6  ━━━━━━━━━━━━━━━━━━━━━━━━━━  100%  120 packets

  [RULE] Size check (> 65 000 B)       ✓  clean
  [RULE] DDoS check (> 100 pkt/IP)     ⚠  192.168.1.10 → 120 packets
                                       ✗  ANOMALY FIRED  DDoS | High
  [RULE] Port scan (> 20 ports/IP)     ✓  clean
  [Z-SCORE] Baseline                   ✓  clean  Z = 1.24
```

Implementation: `LiveDetector` wrapper — calls the real `AnomalyDetector`
but prints before/after each check using the shared console styles.

---

### `ui/report.py`

Pulls anomalies and devices from `DatabaseService`, renders two `rich.table.Table` objects.

Anomaly table — Severity cell colored by `SEVERITY_STYLES`.
Devices table — Packet count + blacklist status per IP.

---

### `services/packet_loader.py` — NEW

Loads `NetworkPacket` objects from a JSON or CSV file.

JSON format:
```json
[
  {
    "source_ip": "192.168.1.99",
    "dest_ip": "10.0.0.1",
    "protocol": "TCP",
    "size": 512,
    "port": 80
  }
]
```

CSV format:
```
source_ip,dest_ip,protocol,size,port
192.168.1.99,10.0.0.1,TCP,512,80
```

`timestamp` auto-set to `datetime.now(UTC)` if not in the file.
Invalid rows are skipped with a yellow warning.

---

### `data/README.md` — NEW

Quick reference next to the sample files:
- required fields and types
- valid protocol values (TCP / UDP / ICMP)
- which size triggers UnusualSize (> 65 000)
- how to load from menu option 3

---

### `docs/manual-data/how-to-add-packets.md` — NEW

Step-by-step for file input:

1. Open `data/sample_packets.json` or `.csv` in any text editor
2. Copy an entry and edit the values
3. Valid protocols: `TCP`, `UDP`, `ICMP`
4. Size > 65 000 bytes triggers UnusualSize
5. Port is destination port (1–65535)
6. Save the file
7. Run program → option 3 → enter filename

Attack scenario table:

| Scenario | source_ip | protocol | size | port | Triggers |
|---|---|---|---|---|---|
| Normal | 192.168.1.5 | TCP | 512 | 80 | nothing |
| DDoS (101+ entries) | 10.10.10.1 | TCP | 512 | 80 | DDoS rule |
| Port scan (ports 1–25) | 10.10.10.2 | TCP | 128 | 1..25 | PortScan rule |
| Oversized packet | 10.10.10.3 | UDP | 66000 | 53 | UnusualSize rule |

---

### `docs/manual-data/how-to-add-via-menu.md` — NEW

Step-by-step for typing a packet in the menu:

1. Run `python main.py`
2. Choose option 2
3. Enter each field when prompted
4. Packet is immediately processed through all detection checks
5. Anomalies shown live and saved to DB
6. Choose option 4 to see the updated report

Includes the same attack scenario table so you know what values to type.

---

### `main.py` — rewritten

1. Print banner (rich Panel, bright_green border)
2. Initialize DatabaseService, EventManager, FileLogger, AnomalyDetector
3. Wire event callbacks
4. Launch `ui/menu.py` main loop

Simulation batch logic moves into `run_simulation()` called by menu option 1.

---

## Implementation order

| Step | File | What you build |
|---|---|---|
| 1 | `requirements.txt` | Add `rich>=13.0` |
| 2 | `ui/console.py` | Console singleton + style constants |
| 3 | `ui/live_feed.py` | LiveDetector + progress bar output |
| 4 | `ui/report.py` | Two rich tables from DB |
| 5 | `services/packet_loader.py` | JSON + CSV loader |
| 6 | `data/sample_packets.json` | Example JSON (normal + attack mix) |
| 7 | `data/sample_packets.csv` | Same data in CSV |
| 8 | `data/README.md` | Quick field reference |
| 9 | `docs/manual-data/how-to-add-packets.md` | File input guide |
| 10 | `docs/manual-data/how-to-add-via-menu.md` | Menu input guide |
| 11 | `ui/menu.py` | Full menu loop with validation |
| 12 | `main.py` | Boot banner + wire services + call menu |

---

## What does NOT change

| File | Status |
|---|---|
| `models/network_packet.py` | unchanged |
| `models/anomaly.py` | unchanged |
| `models/device.py` | unchanged |
| `services/anomaly_detector.py` | unchanged |
| `services/traffic_analyzer.py` | unchanged |
| `services/database_service.py` | unchanged |
| `events/event_manager.py` | unchanged |
| `simulation/traffic_simulator.py` | unchanged |
| `tests/test_core.py` | unchanged |

---

## End result

```
╔══════════════════════════════════════════════╗
║   Network Anomaly Detection System  v2.0    ║
╚══════════════════════════════════════════════╝

  1  Run simulation (auto)
  2  Add packet manually (type it)
  3  Load packets from file (JSON/CSV)
  4  Show database report
  5  Clear database
  6  Exit

> 1

  Starting simulation — 6 batches

  Batch 1/6  ━━━━━━━━━━━━━━━━━━━━━━━━━━  100%  25 packets
  [RULE] Size check       ✓  clean
  [RULE] DDoS check       ✓  clean
  [RULE] Port scan check  ✓  clean
  [Z-SCORE]               ✓  building baseline (1/3)

  Batch 4/6  ━━━━━━━━━━━━━━━━━━━━━━━━━━  100%  120 packets
  [RULE] Size check       ✓  clean
  [RULE] DDoS check       ⚠  192.168.1.10 → 120 packets
                          ✗  ANOMALY FIRED  DDoS | High
  [RULE] Port scan check  ✓  clean
  [Z-SCORE]               ✓  clean  Z = 2.11

  ──────────────────────────────────────────────
  Done.  6 batches  ·  226 packets  ·  4 anomalies
```