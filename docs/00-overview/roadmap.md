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

### Week 1 — Project Initialization & Design ✅

**Objective:** Establish the project foundation before implementation begins. By the end of Week 1, the system scope, architecture, data model, and delivery plan should be clear enough that development can start without rework.

**Build Plan:**
1. Define the problem statement and success criteria for the network anomaly detector.
2. Confirm the core feature set: traffic simulation, anomaly detection, event notifications, logging, and SQLite persistence.
3. Map the project structure into folders, modules, and responsibilities.
4. Design the data model for packets, anomalies, and devices.
5. Document the detection strategy for the first release:
  - rule-based detection for DDoS, port scans, and unusual packet sizes
  - Z-score analysis reserved for the later statistical layer
6. Prepare example traffic scenarios that will be used to validate the first implementation.
7. Decide the initial development order so the codebase can be built in small, testable increments.

**Deliverables:**
- [x] Project idea and description
- [x] Scope and success criteria
- [x] Class list with responsibilities
- [x] Folder/file structure
- [x] Database schema (tables: packets, anomalies, devices)
- [x] AI approach (rule-based + Z-score)
- [x] Sample data examples

**Exit Criteria:**
- The project structure is approved.
- The key entities and service boundaries are defined.
- The first implementation sprint can begin without additional design work.
- The initial detection rules and sample scenarios are documented.

---

### Week 2 — OOP + Events ✅

**Objective:** Build the core domain objects and the event pipeline that the rest of the system will use.

**Build Plan:**
1. Create the main data models for packets, anomalies, and devices.
2. Define the event manager and the callbacks it must support.
3. Implement the first version of the anomaly detector with rule-based checks.
4. Add the file logger and connect it to emitted events.
5. Wire everything together in a simple entry point that processes sample packets.
6. Verify that a detected anomaly can flow through model → event → logger without manual wiring.

**Deliverables:**
- [x] `NetworkPacket`, `Anomaly`, `Device` dataclasses
- [x] `EventManager` with three events and subscriber lists
- [x] `AnomalyDetector` with rule-based checks (DDoS, port scan, unusual size)
- [x] `FileLogger` with callbacks connected to EventManager
- [x] `main.py` that creates sample packets and runs detection

**Exit Criteria:**
- The core models exist and are consistent with the planned schema.
- Events can be raised and handled through subscriber callbacks.
- The detector can flag basic anomalies from sample traffic.
- Logging works end-to-end from event emission.

**Key concepts demonstrated:**
- `@dataclass` for clean model definitions
- Publisher/subscriber pattern using lists of callbacks
- Separation of concerns across classes

---

### Week 3 — Simulation + LINQ-style Queries

**Objective:** Generate realistic traffic patterns and add query methods for exploring the packet stream.

**Build Plan:**
1. Design the traffic simulator inputs, modes, and repeatability controls.
2. Implement normal traffic generation with a configurable number of source IPs.
3. Implement attack scenarios for DDoS and port scanning.
4. Build query methods that summarize packet traffic by IP, protocol, and rate.
5. Add a suspicious-packet filter that reuses the same rules as the detector.
6. Validate the simulator by producing packet batches that clearly match each scenario.

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

**Exit Criteria:**
- The simulator can produce deterministic test traffic for each scenario.
- The analyzer can summarize traffic without manual loops in client code.
- Simulator output is useful for both testing and demonstration.

**Key concepts demonstrated:**
- List comprehensions and `collections` module as Python LINQ equivalents
- Parameterised simulation for reproducible test scenarios

---

### Week 4 — Database Integration

**Objective:** Add persistence so packets, anomalies, and devices can be stored and retrieved from SQLite.

**Build Plan:**
1. Define the database schema and foreign key relationships.
2. Implement the database service that creates and manages the tables.
3. Add methods to save packets, anomalies, and devices.
4. Add read methods that support the main reporting and inspection use cases.
5. Connect event callbacks so detected anomalies are saved automatically.
6. Confirm that database writes happen without leaking persistence logic into detection code.

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

**Exit Criteria:**
- The schema matches the planned data model.
- Save and query operations work from the service layer.
- Detection and storage remain separated concerns.

**Key concepts demonstrated:**
- `sqlite3` standard library
- FK relationships between tables
- Separation of persistence logic from detection logic

---

### Week 5 — Statistical AI Model (Z-Score)

**Objective:** Add statistical anomaly detection so the system can catch gradual or subtle attacks that the rules miss.

**Build Plan:**
1. Define the packet-count window used for each IP.
2. Implement rolling mean and standard deviation calculations.
3. Add Z-score detection to the anomaly detector.
4. Map Z-score ranges to severity levels.
5. Compare statistical detections against rule-based detections on the same sample traffic.
6. Tune thresholds so the second layer adds value rather than duplicating the first.

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

**Exit Criteria:**
- The detector can run both detection layers in one pass.
- Statistical anomalies are classified with severity.
- The team can explain what the Z-score layer adds.

**Key concepts demonstrated:**
- Statistical modelling without external ML libraries
- Sliding window aggregation
- Two-stage detection pipeline

---

### Week 6 — Final Integration & Polish

**Objective:** Connect all components into a complete working system and prepare it for use and presentation.

**Build Plan:**
1. Integrate the simulator, analyzer, detector, event manager, logger, and database service.
2. Build the main execution flow from traffic generation to summary output.
3. Add a final report that shows the most important results from a run.
4. Review the code for consistency, naming, and separation of concerns.
5. Write setup and usage instructions for the finished project.
6. Do a final end-to-end test using mixed normal and attack traffic.

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

**Exit Criteria:**
- The full pipeline runs without manual intervention.
- The output demonstrates detection, logging, and persistence together.
- The project is documented well enough for another person to run it.

**Key concepts demonstrated:**
- System integration
- End-to-end validation
- Developer documentation and cleanup

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