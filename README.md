# Network Anomaly Detection System

Python project for simulating network traffic and detecting anomalies such as DDoS behavior, port scanning, and unusual packet sizes.

## What It Does

- Simulates normal and attack traffic
- Detects anomalies with rule-based logic and rolling Z-score analysis
- Logs events to a file
- Stores packets, anomalies, and devices in SQLite
- Prints a summary report at the end of a run

## Project Layout

- `models/` - core dataclasses
- `events/` - event publishing and subscriptions
- `services/` - detection, analysis, logging, and persistence
- `simulation/` - traffic generation
- `docs/` - architecture, planning, testing, and operations guides

## Run

```bash
python main.py
```

## Generated Files

- `log.txt`
- `anomalies.db`
