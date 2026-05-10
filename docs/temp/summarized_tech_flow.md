# Network Anomaly Detector — Technical Summary

## What the system does

Monitors network traffic and flags suspicious behavior using two detection strategies:
- **Rules** — fast, hardcoded thresholds
- **Z-Score** — statistical baseline per IP, adapts over time

---

## Architecture (4 layers)

```
UI Layer        →  menu, live output, report tables (rich TUI)
Service Layer   →  detection engine, database, logger, packet loader
Data Layer      →  NetworkPacket, Anomaly, Device models + EventManager
Persistence     →  SQLite3 (3 tables: packets, anomalies, devices)
```

---

## Data flow

```
User picks menu option
        ↓
Packets created (simulation / manual input / JSON file)
        ↓
Devices saved or updated in DB for each source IP
        ↓
Packets saved to DB (get auto-increment ID)
        ↓
AnomalyDetector.analyze_packets(packets)
    ├── Rule checks  (DDoS / PortScan / UnusualSize)
    └── Z-score check (after 3 batches of history)
        ↓
For each anomaly found → EventManager fires
    ├── FileLogger    → append to log.txt
    └── DatabaseService → INSERT into anomalies table
        ↓
LiveDetector prints ✓ / ⚠ / ✗ per check in real time
        ↓
Return to menu
```

---

## Detection rules

| Rule | Threshold | Severity |
|---|---|---|
| DDoS | > 100 packets from one IP in a batch | High |
| Port Scan | > 20 unique destination ports from one IP | High |
| Unusual Size | single packet > 65 000 bytes | Medium |

---

## Z-Score (statistical detection)

Needs 3 batches of history per IP before it activates.

```
history for IP = [100, 102, 101]
mean = 101, stdev = 1.0

new packet size = 150
Z = (150 - 101) / 1.0 = 49.0  → ANOMALY (|Z| > 3)
```

Severity by Z-score magnitude:

| Z-score | Severity |
|---|---|
| > 8 | Critical |
| > 5 | High |
| > 3 | Medium |

**Key limitation:** the first 3 batches are the learning phase — no detection runs yet.

---

## Events (pub/sub)

| Event | Fired when | Subscribers |
|---|---|---|
| `emit_anomaly_detected` | any anomaly confirmed | FileLogger, DatabaseService |
| `emit_ddos_suspected` | DDoS rule triggers | FileLogger |
| `emit_unusual_traffic` | size rule triggers | FileLogger |

---

## Database relationships

```
devices (id, ip_address, packet_count, is_blacklisted ...)
    ↑
packets (id, source_ip, protocol, size, port, device_id FK)
    ↑
anomalies (id, packet_id FK, type, severity, description, is_resolved)
```

---

## Key classes at a glance

| Class | Role |
|---|---|
| `AnomalyDetector` | runs both detection strategies, emits events |
| `EventManager` | pub/sub — decouples detection from logging/persistence |
| `LiveDetector` | wraps AnomalyDetector, prints real-time TUI output |
| `DatabaseService` | all SQLite reads and writes |
| `PacketLoader` | parses JSON/CSV files into NetworkPacket objects |
| `TrafficSimulator` | generates synthetic traffic for testing |
| `FileLogger` | writes audit log to log.txt |