# Network Anomaly Detection System — Project Roadmap

## Project Overview

A Python-based system that simulates real network traffic and uses AI techniques to automatically detect anomalies such as DDoS attacks, port scanning, and unusual data volumes. The system classifies network packets as normal or suspicious through a combination of rule-based logic and statistical analysis.

---

## Goals

- Simulate realistic network traffic programmatically (no external datasets needed)
- Detect anomalies in real time using two-stage AI detection
- Persist packets, anomalies, and devices to a SQLite database
- Notify subscribers of events through a publisher/subscriber pattern
- Log all activity to a file for audit and review
- Demonstrate clean OOP design, LINQ-equivalent queries in Python, and event-driven architecture

---

## Project Structure

```
NetworkAnomalyDetector/
├── models/
│   ├── network_packet.py
│   ├── anomaly.py
│   └── device.py
├── services/
│   ├── traffic_analyzer.py
│   ├── anomaly_detector.py
│   ├── database_service.py
│   └── file_logger.py
├── events/
│   └── event_manager.py
├── simulation/
│   └── traffic_simulator.py
├── main.py
├── requirements.txt
└── README.md
```

---

## Week-by-Week Roadmap

---

### Week 1 — Analysis & Design ✅

**Goal:** Plan the system before writing any code.

**Deliverables:**
- [x] Project idea and description
- [x] Class list with responsibilities
- [x] Folder/file structure
- [x] Database schema (tables: packets, anomalies, devices)
- [x] AI approach (rule-based + Z-score)
- [x] Sample data examples

---

### Week 2 — OOP + Events ✅

**Goal:** Build the core classes and wire up the event system.

**Deliverables:**
- [x] `NetworkPacket`, `Anomaly`, `Device` dataclasses
- [x] `EventManager` with three events and subscriber lists
- [x] `AnomalyDetector` with rule-based checks (DDoS, port scan, unusual size)
- [x] `FileLogger` with callbacks connected to EventManager
- [x] `main.py` that creates sample packets and runs detection

**Key concepts demonstrated:**
- `@dataclass` for clean model definitions
- Publisher/subscriber pattern using lists of callbacks
- Separation of concerns across classes

---

### Week 3 — Simulation + LINQ-style Queries

**Goal:** Build the traffic simulator and implement data analysis methods.

**Deliverables:**
- [ ] `TrafficSimulator` with three modes:
  - `normal` — random traffic from 10–20 IPs
  - `ddos` — one IP sending 500+ packets per second
  - `port_scan` — one IP cycling through ports 1–1024
- [ ] `TrafficAnalyzer` with query methods:
  - `get_top_ips(n)` — top N source IPs by packet count
  - `group_by_protocol()` — packet counts per protocol
  - `get_suspicious_packets()` — packets matching threshold rules
  - `get_packets_per_second(ip)` — traffic rate for a given IP

**Key concepts demonstrated:**
- List comprehensions and `collections` module as Python LINQ equivalents
- Parameterised simulation for reproducible test scenarios

---

### Week 4 — Database Integration

**Goal:** Persist all data to SQLite using a clean service layer.

**Deliverables:**
- [ ] `DatabaseService` that creates and manages three tables:
  - `packets` — every captured packet
  - `anomalies` — every detected anomaly with FK to packet
  - `devices` — known devices/IPs with metadata
- [ ] Methods:
  - `save_packet(packet)` → returns generated ID
  - `save_anomaly(anomaly)`
  - `save_device(device)`
  - `get_all_anomalies()` → list of Anomaly objects
  - `get_blacklisted_devices()` → list of Device objects
  - `get_packets_by_ip(ip)` → list of NetworkPacket objects
- [ ] `EventManager` callbacks updated to save anomalies automatically

**Key concepts demonstrated:**
- `sqlite3` standard library
- FK relationships between tables
- Separation of persistence logic from detection logic

---

### Week 5 — Statistical AI Model (Z-Score)

**Goal:** Add the second detection layer using statistical analysis.

**Deliverables:**
- [ ] Z-score calculation per IP over a sliding time window:
  ```
  Z = (x - μ) / σ
  flag if |Z| > 3
  ```
- [ ] `AnomalyDetector` updated to run both rule-based and Z-score checks
- [ ] New severity levels based on Z-score magnitude:
  - `|Z| > 3` → Medium
  - `|Z| > 5` → High
  - `|Z| > 8` → Critical
- [ ] Results compared: what does Z-score catch that rules miss?

**Key concepts demonstrated:**
- Statistical modelling without external ML libraries
- Sliding window aggregation
- Two-stage detection pipeline

---

### Week 6 — Final Integration & Polish

**Goal:** Connect all components into a working end-to-end system.

**Deliverables:**
- [ ] `main.py` runs a full simulation cycle:
  1. Simulator generates traffic (mix of normal + attack scenarios)
  2. Analyzer queries the stream
  3. Detector runs both rule-based and Z-score checks
  4. EventManager fires callbacks
  5. Logger writes to file
  6. DatabaseService persists everything
- [ ] Summary report printed at the end:
  - Total packets processed
  - Anomalies detected by type
  - Top 5 suspicious IPs
  - Detection method breakdown (rules vs Z-score)
- [ ] `README.md` with setup and run instructions
- [ ] Code cleaned up, comments added

---

## Database Schema

```
packets
-------
id          INTEGER  PK
source_ip   TEXT
dest_ip     TEXT
protocol    TEXT     (TCP / UDP / ICMP)
size        INTEGER  (bytes)
port        INTEGER
timestamp   DATETIME
device_id   INTEGER  FK → devices.id

anomalies
---------
id          INTEGER  PK
packet_id   INTEGER  FK → packets.id
type        TEXT     (DDoS / PortScan / UnusualSize)
severity    TEXT     (Low / Medium / High / Critical)
detected_at DATETIME
description TEXT
is_resolved BOOLEAN

devices
-------
id              INTEGER  PK
ip_address      TEXT     UNIQUE
device_type     TEXT
is_blacklisted  BOOLEAN
first_seen      DATETIME
last_seen       DATETIME
packet_count    INTEGER
```

---

## AI Detection Approach

### Stage 1 — Rule-Based (Week 2)

Hard-coded thresholds applied to every packet batch:

| Rule | Threshold | Anomaly Type |
|---|---|---|
| Packets from one IP per second | > 100 | DDoS |
| Unique destination ports per IP | > 20 | Port Scan |
| Packet size | > 65,000 bytes | Unusual Size |

### Stage 2 — Statistical / Z-Score (Week 5)

For each IP, maintain a rolling window of packet counts. Compute mean (μ) and standard deviation (σ). Flag IPs where the current count deviates by more than 3 standard deviations.

```
Z = (current_count - μ) / σ
if |Z| > 3 → anomaly
```

This catches gradual build-up attacks that stay under the hard thresholds in Stage 1.

---

## Events

| Event | Fired when | Payload |
|---|---|---|
| `on_anomaly_detected` | Any anomaly is confirmed | `Anomaly` object |
| `on_ddos_suspected` | DDoS threshold exceeded | source IP string |
| `on_unusual_traffic` | Packet size > 65,000B | `NetworkPacket` object |

---

## Sample Data

```
192.168.1.10 → 10.0.0.1  | TCP  | 512B   | port 80  | NORMAL
192.168.1.10 → 10.0.0.1  | TCP  | 512B   | port 80  | NORMAL (×500 in 1s → DDoS)
192.168.1.55 → 10.0.0.1  | TCP  | 128B   | port 1   | PORT SCAN
192.168.1.55 → 10.0.0.1  | TCP  | 128B   | port 2   | PORT SCAN
203.0.113.77 → 10.0.0.1  | UDP  | 66000B | port 53  | UNUSUAL SIZE
```

---

## Dependencies

```
# requirements.txt
# No third-party libraries required.
# Standard library only: sqlite3, dataclasses, collections, datetime, random, statistics
```

---

## How to Run (Week 6 target)

```bash
git clone <repo>
cd NetworkAnomalyDetector
python main.py
```

Output:
- Console summary of detected anomalies
- `log.txt` with timestamped entries
- `anomalies.db` SQLite file with full data