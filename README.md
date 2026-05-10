# Network Anomaly Detection System

Python project for simulating network traffic and detecting anomalies such as DDoS behavior, port scanning, and unusual packet sizes.

## What It Does

- Simulates normal and attack traffic
- Detects anomalies with rule-based logic and rolling Z-score analysis
- Logs events to a file
- Stores packets, anomalies, and devices in SQLite
- Provides a rich terminal menu for simulation, manual entry, file loading, and reports

## Project Layout

- `models/` - core dataclasses
- `events/` - event publishing and subscriptions
- `services/` - detection, analysis, logging, persistence, and packet loading
- `simulation/` - traffic generation
- `ui/` - terminal interface, live feed, and reports
- `data/` - editable sample input files
- `docs/` - architecture, planning, testing, and operations guides

## Run

```bash
python main.py
```

If the terminal is interactive, the menu opens. In non-interactive runs, the app executes a default demo and exits.

## Generated Files

- `log.txt`
- `anomalies.db`

## Manual Input

Editable packet samples live in `data/`. See `docs/manual-data/` for step-by-step instructions on loading packets from the menu or from files.
