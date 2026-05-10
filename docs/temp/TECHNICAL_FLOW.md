# Network Anomaly Detection System - Technical Documentation

**Date:** May 10, 2026  
**Project:** AnomaliesDetector  
**Language:** Python 3.13  
**Framework:** rich (TUI), SQLite3 (Persistence)

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Data Flow](#data-flow)
4. [Database Schema](#database-schema)
5. [Core Classes](#core-classes)
6. [Detection Methods](#detection-methods)
7. [Request Flow](#request-flow)
8. [AI & Algorithm Explanation](#ai--algorithm-explanation)

---

## System Overview

The **Network Anomaly Detection System** is a Python-based tool that monitors network traffic for suspicious behavior. It uses two complementary detection strategies:

1. **Rule-Based Detection** - Fast, pattern-matching anomalies
2. **Statistical Detection (Z-Score)** - Machine learning-inspired baseline deviation detection

**Key Metrics:**
- Database: 14 devices tracked, 131 packets analyzed, 2 anomalies detected
- Detection Rules: 3 (DDoS, PortScan, UnusualSize)
- Persistence Layer: SQLite3 with 3 tables (devices, packets, anomalies)

---

## Architecture

### Layered Design

```
┌─────────────────────────────────────────┐
│           UI Layer (Rich TUI)            │
│  (menu, live_feed, report, console)     │
├─────────────────────────────────────────┤
│      Service Layer (Business Logic)      │
│  anomaly_detector, database, logger      │
├─────────────────────────────────────────┤
│      Data Layer (Models & Events)        │
│  NetworkPacket, Anomaly, Device          │
│  EventManager (pub/sub)                  │
├─────────────────────────────────────────┤
│    Persistence Layer (SQLite3)           │
│  3 tables with foreign key constraints   │
└─────────────────────────────────────────┘
```

### Module Structure

```
AnomaliesDetector/
├── models/                  # Data structures
│   ├── network_packet.py    # Network traffic unit
│   ├── anomaly.py          # Detection result
│   └── device.py           # Source IP metadata
├── services/                # Business logic
│   ├── anomaly_detector.py # Detection engine
│   ├── database_service.py # SQLite layer
│   ├── file_logger.py      # Audit logging
│   ├── packet_loader.py    # JSON/CSV import
│   └── traffic_analyzer.py # LINQ-style queries
├── events/                  # Event system
│   └── event_manager.py    # Pub/sub dispatcher
├── simulation/              # Testing utilities
│   └── traffic_simulator.py # Generate test data
├── ui/                      # Terminal UI
│   ├── console.py          # Shared console + styles
│   ├── menu.py             # Interactive menu
│   ├── live_feed.py        # Real-time output
│   └── report.py           # Database tables
├── data/                    # Sample files
│   ├── sample_packets.json
│   └── sample_packets.csv
├── docs/                    # Documentation
│   ├── roadmap.md
│   ├── temp/               # Technical docs
│   │   ├── database_export.json
│   │   └── TECHNICAL_FLOW.md
│   └── ...
├── main.py                 # Entry point
└── tests/                  # Unit tests
```

---

## Data Flow

### Request Flow Diagram

```
User Input
    ↓
┌─ Menu Option ────────────────────────────────┐
│                                              │
├→ Option 1: Run Simulation                    │
│  TrafficSimulator.generate_sample_batch()    │
│  → [25, 25, 25, 120, 30, 1] packets          │
│                                              │
├→ Option 2: Add Packet Manually               │
│  User enters: source_ip, dest_ip, protocol,  │
│  size, port (console prompts with validation)│
│  → Single NetworkPacket object               │
│                                              │
├→ Option 3: Load from File                    │
│  PacketLoader.load_packets(file_path)        │
│  → Parse JSON/CSV, validate fields           │
│  → List[NetworkPacket]                       │
│                                              │
├→ Option 4: Show Report                       │
│  DatabaseService.get_all_*()                 │
│  → rich Tables with colors                   │
│                                              │
├→ Option 5: Clear Database                    │
│  DatabaseService.clear_all()                 │
│  → DELETE all rows, commit                   │
│                                              │
└→ Option 6: Exit                              │
   sys.exit(0)                                 │
    ↓
Process Packets (shared path for all inputs)
    ↓
main.process_packets(packets)
    ↓
┌─ Ensure Devices ─────────────────────────────┐
│ For each packet's source_ip:                 │
│  1. Check if device exists in DB             │
│  2. If exists: update last_seen, packet_count│
│  3. If new: create Device, save to DB        │
│                                              │
│ DatabaseService.get_all_devices() → compare  │
│ DatabaseService.save_device(device)          │
└─────────────────────────────────────────────┘
    ↓
┌─ Save Packets ───────────────────────────────┐
│ For each packet:                             │
│  DatabaseService.save_packet(packet)         │
│  → INSERT INTO packets table                 │
│  → Return packet.id (auto-increment)         │
└─────────────────────────────────────────────┘
    ↓
┌─ Run Detection ──────────────────────────────┐
│ LiveDetector.run_batch(packets, index, total)│
│  (wrapper around AnomalyDetector)            │
│    ↓                                         │
│ AnomalyDetector.analyze_packets(packets)    │
│  1. Apply rule-based checks                  │
│  2. Apply Z-score statistical analysis       │
│  3. Emit events for each anomaly             │
│    ↓                                         │
│ Event subscribers notified:                  │
│  • FileLogger: log_anomaly()                 │
│  • DatabaseService: save_anomaly()           │
│  • Console: display results (LiveDetector)   │
└─────────────────────────────────────────────┘
    ↓
┌─ Display Results ────────────────────────────┐
│ LiveDetector prints:                         │
│  • Progress bar with packet count            │
│  • ✓/⚠/✗ status for each rule check         │
│  • Z-score baseline building progress        │
│  • Summary of anomalies fired                │
│                                              │
│ Then shows final report:                     │
│  • Total packets processed                   │
│  • Anomalies detected                        │
│  • Top 5 source IPs by activity              │
│  • Suspicious packets (size > 65000)         │
└─────────────────────────────────────────────┘
    ↓
Return to Menu (loop until exit)
```

---

## Database Schema

### Table: `devices`

Tracks source IP addresses and their threat status.

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique identifier |
| ip_address | TEXT UNIQUE NOT NULL | Source IP (indexed for quick lookup) |
| device_type | TEXT | Classification (e.g., "server", "client") |
| is_blacklisted | INTEGER | Boolean flag: 1=blacklisted, 0=normal |
| first_seen | TEXT (ISO8601) | Timestamp of first packet |
| last_seen | TEXT (ISO8601) | Timestamp of most recent packet |
| packet_count | INTEGER | Total packets from this IP |

**Status:** ⚠️ Currently no `anomaly_count` field. Recommend adding to track devices with anomalies.

### Table: `packets`

Raw network traffic data captured during analysis.

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique packet identifier |
| source_ip | TEXT NOT NULL | Sender IP address |
| dest_ip | TEXT NOT NULL | Recipient IP address |
| protocol | TEXT | Communication protocol (TCP, UDP, etc.) |
| size | INTEGER | Packet payload size in bytes |
| port | INTEGER | Destination port (1-65535) |
| timestamp | TEXT (ISO8601) | When packet was captured |
| device_id | INTEGER FK | References devices(id) |

**Index:** Implicitly indexed via device_id FK for join queries.

### Table: `anomalies`

Detection results: which packets were flagged and why.

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique anomaly identifier |
| packet_id | INTEGER FK | References packets(id) |
| type | TEXT | Anomaly type (DDoS, PortScan, UnusualSize, ZScoreAnomaly) |
| severity | TEXT | Level (Critical, High, Medium, Low) |
| detected_at | TEXT (ISO8601) | Detection timestamp |
| description | TEXT | Human-readable explanation |
| is_resolved | INTEGER | Boolean: 1=resolved, 0=active |

**Relationships:**
```
anomalies.packet_id → packets.id
packets.device_id → devices.id
```

---

## Core Classes

### 1. NetworkPacket (models/network_packet.py)

**Purpose:** Immutable data structure for a single network traffic unit.

```python
@dataclass(slots=True)
class NetworkPacket:
    source_ip: str              # Sender IP
    dest_ip: str               # Receiver IP
    protocol: str              # TCP, UDP, ICMP, etc.
    size: int                  # Bytes (0-65535)
    port: int                  # Destination port
    timestamp: datetime        # UTC timezone-aware
    device_id: int | None      # Foreign key to devices table
    id: int | None = None      # Database row ID
```

**Key Methods:** None (dataclass only provides `__init__`, `__eq__`, `__repr__`)

**Used By:** AnomalyDetector, DatabaseService, TrafficSimulator, TrafficAnalyzer

---

### 2. Anomaly (models/anomaly.py)

**Purpose:** Detection result object linking a packet to a security finding.

```python
@dataclass(slots=True)
class Anomaly:
    packet_id: int
    type: str                  # DDoS, PortScan, UnusualSize, ZScoreAnomaly
    severity: str              # Critical, High, Medium, Low
    description: str           # "192.168.1.10 generated 120 packets..."
    detected_at: datetime      # When detected (UTC)
    is_resolved: bool = False  # Remediation flag
    id: int | None = None      # Database row ID
```

**Key Methods:** None (dataclass only)

**Emitted By:** AnomalyDetector when rules/stats fire

---

### 3. Device (models/device.py)

**Purpose:** Track source IP metadata for threat assessment.

```python
@dataclass(slots=True)
class Device:
    ip_address: str
    device_type: str           # "server", "client", "unknown"
    is_blacklisted: bool = False
    first_seen: datetime       # When first packet arrived
    last_seen: datetime        # When last packet arrived
    packet_count: int = 0      # Total packets from this IP
    id: int | None = None      # Database row ID
```

**Lifecycle:**
1. Created automatically when first packet from new IP is processed
2. Updated in-memory when subsequent packets arrive from same IP
3. Saved to database via `DatabaseService.save_device()`
4. Can be blacklisted via `is_blacklisted = True` flag

---

### 4. EventManager (events/event_manager.py)

**Purpose:** Publish-subscribe dispatcher for loose coupling between detection and logging/persistence.

```python
class EventManager:
    def __init__(self) -> None:
        self._anomaly_subscribers: list[Callable[[Anomaly], None]] = []
        self._ddos_subscribers: list[Callable[[str, int], None]] = []
        self._traffic_subscribers: list[Callable[[str, int], None]] = []
    
    # Registration
    def subscribe_anomaly_detected(self, callback: Callable[[Anomaly], None]) -> None
    def subscribe_ddos_suspected(self, callback: Callable[[str, int], None]) -> None
    def subscribe_unusual_traffic(self, callback: Callable[[str, int], None]) -> None
    
    # Publishing
    def emit_anomaly_detected(self, anomaly: Anomaly) -> None
    def emit_ddos_suspected(self, source_ip: str, packet_count: int) -> None
    def emit_unusual_traffic(self, source_ip: str, port_count: int) -> None
```

**Pattern:** Observer pattern with 3 event types. Each `emit_*()` calls all registered callbacks.

**Subscribers in main.py:**
- FileLogger: appends to log.txt
- DatabaseService: persists to anomalies table
- Console: displays via LiveDetector

---

### 5. AnomalyDetector (services/anomaly_detector.py)

**Purpose:** Core detection engine with dual-strategy anomaly identification.

```python
class AnomalyDetector:
    def __init__(self, event_manager: EventManager) -> None
    
    def analyze_packets(self, packets: list[NetworkPacket]) -> list[Anomaly]
        """Run both detection strategies."""
        1. Rule-based checks
        2. Statistical Z-score analysis
        3. Return combined anomalies list
```

**Detection Strategies:**

#### A. Rule-Based Detection (Deterministic)

Three independent rules checked per batch:

| Rule | Check | Threshold | Severity | Event |
|------|-------|-----------|----------|-------|
| DDoS | packets from same source_ip in one batch | > 100 | High | emit_ddos_suspected() |
| PortScan | unique dest_port per source_ip | > 20 | High | emit_unusual_traffic() |
| UnusualSize | single packet size | > 65000 bytes | Medium | emit_anomaly_detected() |

**Implementation:**
```python
def _detect_rules(self, packets: list[NetworkPacket]) -> list[Anomaly]:
    anomalies = []
    
    # 1. DDoS rule
    ip_counts = Counter(p.source_ip for p in packets)
    for ip, count in ip_counts.items():
        if count > 100:  # Threshold
            anomaly = Anomaly(
                packet_id=<first packet from this IP>.id,
                type="DDoS",
                severity="High",
                description=f"Source IP {ip} generated {count} packets..."
            )
            anomalies.append(anomaly)
            self.event_manager.emit_ddos_suspected(ip, count)
    
    # 2. PortScan rule
    for packet in packets:
        ports = len(set(p.port for p in packets if p.source_ip == packet.source_ip))
        if ports > 20:
            anomalies.append(...)
    
    # 3. UnusualSize rule
    for packet in packets:
        if packet.size > 65000:
            anomalies.append(...)
    
    return anomalies
```

#### B. Statistical Detection (Z-Score Analysis)

**Concept:** Baseline deviation detection using rolling statistics.

**Algorithm:**
1. Maintain `_packet_history[source_ip]` = list of sizes for each IP
2. After 3 batches, calculate mean (μ) and std dev (σ) for each IP
3. For new packets: `z_score = (size - μ) / σ`
4. If `z_score > 3.0`: Anomaly (99.7% confidence it's abnormal)

**Rationale:** Detects when a specific IP suddenly sends unusual-sized packets, even if within normal range for others.

**Implementation:**
```python
def _detect_z_score_anomalies(self, packets: list[NetworkPacket]) -> list[Anomaly]:
    anomalies = []
    
    for packet in packets:
        # Build history
        if packet.source_ip not in self._packet_history:
            self._packet_history[packet.source_ip] = []
        
        self._packet_history[packet.source_ip].append(packet.size)
        history = self._packet_history[packet.source_ip]
        
        # Need 3+ data points for statistics
        if len(history) < 3:
            continue
        
        # Calculate statistics
        mean = statistics.mean(history[:-1])      # Exclude current
        stdev = statistics.stdev(history[:-1])
        
        if stdev == 0:  # No variance, skip
            continue
        
        # Z-score for current packet
        z_score = (packet.size - mean) / stdev
        
        if abs(z_score) > 3.0:  # Threshold
            anomaly = Anomaly(
                packet_id=packet.id,
                type="ZScoreAnomaly",
                severity="Critical" if abs(z_score) > 5.0 else "High",
                description=f"Source IP {packet.source_ip} deviated from baseline with Z-score {z_score:.2f}."
            )
            anomalies.append(anomaly)
            self.event_manager.emit_anomaly_detected(anomaly)
    
    return anomalies
```

**Advantages:**
- Learns per-IP baseline automatically
- Detects abnormal behavior relative to that IP's history
- No manual threshold tuning per IP

**Limitations:**
- Requires 3 batches to activate
- Assumes normal traffic in first 3 batches

---

### 6. DatabaseService (services/database_service.py)

**Purpose:** SQLite persistence layer with public query API.

```python
class DatabaseService:
    def __init__(self, database_path: str = "anomalies.db") -> None
    
    # Write operations
    def save_packet(self, packet: NetworkPacket) -> int       # → packet.id
    def save_anomaly(self, anomaly: Anomaly) -> int          # → anomaly.id
    def save_device(self, device: Device) -> int             # → device.id
    
    # Read operations
    def get_all_anomalies() -> list[Anomaly]
    def get_all_devices() -> list[Device]
    def get_blacklisted_devices() -> list[Device]
    def get_packets_by_ip(source_ip: str) -> list[NetworkPacket]
    
    # Lifecycle
    def clear_all() -> None                                   # DELETE all rows
    def close() -> None                                       # Close connection
```

**Key Design:**
- Foreign key constraints enabled: `PRAGMA foreign_keys = ON`
- `save_device()` uses UPSERT (INSERT ... ON CONFLICT): idempotent updates
- All timestamps stored as ISO8601 strings
- No public `_connection` access (encapsulation)

**Subscribers to EventManager:**
- `emit_anomaly_detected()` → `save_anomaly()`
- (Other events logged by FileLogger)

---

### 7. LiveDetector (ui/live_feed.py)

**Purpose:** Wrapper around AnomalyDetector to display real-time progress without modifying core logic.

```python
class LiveDetector:
    def __init__(self, detector: AnomalyDetector, event_manager: EventManager) -> None
    
    def run_batch(
        self, 
        packets: list[NetworkPacket], 
        batch_index: int, 
        total_batches: int
    ) -> list[Anomaly]:
        """Run detection and display progress."""
```

**Output Example:**
```
Batch 4/6  ━━━━━━━━━━━━━━━━━━━━━━━━━  100%  120 packets
  [RULE] Size check (> 65 000 B)      ✓  clean
  [RULE] DDoS check (> 100 pkt/IP)    ⚠  192.168.1.10 → 120 packets
  [RULE] Port scan (> 20 ports/IP)    ✓  clean
  [Z-SCORE] Baseline                  ✗  ANOMALY FIRED  Critical
```

**Methods:**
- `_print_rule_checks()`: Check each rule, display symbol (✓/⚠/✗)
- `_print_z_score_status()`: Show baseline building or anomalies
- `_print_anomaly_summary()`: List detected anomalies with colors

---

### 8. PacketLoader (services/packet_loader.py)

**Purpose:** Import network traffic from JSON/CSV files with validation.

```python
class PacketLoader:
    @staticmethod
    def load_packets(file_path: str) -> list[NetworkPacket]:
        """Dispatch to JSON or CSV parser based on file extension."""
```

**Validation:**
- source_ip, dest_ip: valid IPv4 using `ipaddress.ip_address()`
- protocol: must exist in enum (TCP, UDP, ICMP, etc.)
- port: 1-65535
- size: > 0
- timestamp: optional, auto-filled with UTC now if missing

**Error Handling:**
- Skip invalid rows with yellow console warnings
- Continue loading remaining rows
- Returns all valid packets

---

### 9. TrafficSimulator (simulation/traffic_simulator.py)

**Purpose:** Generate synthetic network traffic for testing/demo.

```python
class TrafficSimulator:
    def __init__(self, seed: int = 42) -> None
    
    def generate_normal_traffic(self, packet_count: int) -> list[NetworkPacket]
    def generate_ddos_traffic(self, source_ip: str, packet_count: int) -> list[NetworkPacket]
    def generate_port_scan_traffic(self, source_ip: str, port_count: int) -> list[NetworkPacket]
    def generate_sample_batch(self) -> list[NetworkPacket]
```

**Batch Composition:**
```
Batch 1-3: 25 normal packets each   (baseline)
Batch 4:   120 DDoS packets         (triggers DDoS rule)
Batch 5:   30 port-scan packets     (triggers PortScan rule)
Batch 6:   1 oversized packet       (triggers UnusualSize rule)
───────────────────────────────
Total:     226 packets, 4 anomalies
```

---

## Detection Methods

### Method 1: Rule-Based Detection (Deterministic)

**When:** Every batch processed

**How:**
1. Count packets per source_ip
2. Count unique ports per source_ip
3. Check max packet size
4. Compare against hardcoded thresholds

**Pros:**
- ⚡ Fast O(n) complexity
- 🎯 High precision (no false positives if tuned correctly)
- 🔍 Explainable (clear why flagged)

**Cons:**
- 📌 Fixed thresholds (DDoS > 100, PortScan > 20, Size > 65000)
- 🚫 Can't detect subtle variations
- ⚙️ Requires manual threshold tuning per network

---

### Method 2: Statistical Detection (Unsupervised ML)

**When:** After 3 batches (baseline built per IP)

**How:**
1. For each source_ip, maintain rolling history of packet sizes
2. Calculate mean (μ) and std dev (σ) from 3-batch history
3. For each new packet: `z = (size - μ) / σ`
4. If |z| > 3.0: Flag as anomaly (99.7% confidence)

**Why Z-Score:**
- **Adaptive:** Each IP learns its own normal pattern
- **Universal:** Works across different packet size distributions
- **Statistical:** Based on probability theory (3σ rule)

**Example:**
```
IP 192.168.1.10 history: [100, 102, 101]
Mean = 101, StdDev = 1.0

New packet size 150:
Z-score = (150 - 101) / 1.0 = 49.0  → ANOMALY (extreme deviation)

Another IP 10.0.0.1 history: [50000, 52000, 51000]
Mean = 51000, StdDev = 1000

New packet size 55000:
Z-score = (55000 - 51000) / 1000 = 4.0  → ANOMALY (but different threshold)
```

---

## Request Flow

### Complete End-to-End Example

**User Request:** "Run simulation (Option 1)"

```
1. User Input
   └─→ menu.py: run_menu() displays 6 options
       User sends "1" via input()
   
2. Menu Dispatch
   └─→ run_menu() calls run_simulation callback
       callback → main.run_simulation()
   
3. Simulation Generation
   └─→ main.run_simulation() calls TrafficSimulator.generate_sample_batch()
       Returns: 226 packets across 6 batches
   
4. For each batch (1-6):
   
   4a. Ensure Devices
       └─→ main.ensure_devices_for_packets(packets)
           For each packet.source_ip:
               Check: device exists in DB?
               ├─ YES: update last_seen, packet_count
               └─ NO: create new Device, save to DB
   
   4b. Save Packets
       └─→ main.process_packets(packets)
           For each packet:
               DatabaseService.save_packet(packet)
               → INSERT INTO packets
               → packet.id = auto-increment value
   
   4c. Run Detection
       └─→ LiveDetector.run_batch(packets, batch_index, total)
           ├─→ AnomalyDetector.analyze_packets(packets)
           │   ├─ Rule checks:
           │   │  ├─ DDoS: count packets per IP, check > 100
           │   │  ├─ PortScan: count ports per IP, check > 20
           │   │  └─ UnusualSize: check max size > 65000
           │   │
           │   └─ Z-score checks:
           │      For each IP with history:
           │      ├─ calculate mean, stdev from last 3+ packets
           │      ├─ compute z = (size - mean) / stdev
           │      └─ if |z| > 3: create anomaly
           │
           ├─→ For each Anomaly detected:
           │   ├─ EventManager.emit_anomaly_detected(anomaly)
           │   │  ├─ FileLogger callback: append to log.txt
           │   │  └─ DatabaseService callback: INSERT INTO anomalies
           │   │
           │   ├─ EventManager.emit_ddos_suspected(ip, count)
           │   │  └─ FileLogger callback: log DDoS alert
           │   │
           │   └─ EventManager.emit_unusual_traffic(ip, port_count)
           │      └─ FileLogger callback: log unusual traffic
           │
           └─→ LiveDetector.run_batch() displays progress:
               ├─ Progress bar with packet count
               ├─ Rule status (✓ clean / ⚠ warning / ✗ anomaly)
               ├─ Z-score status (building baseline / clean / anomaly)
               └─ Summary of detected anomalies
   
5. Display Final Report
   └─→ Console displays:
       ├─ Total packets processed: 226
       ├─ Anomalies detected: 4
       ├─ Top IPs by activity
       └─ Suspicious packets count
   
6. Return to Menu
   └─→ Display menu again
       Wait for next user input
```

---

## AI & Algorithm Explanation

### Is There an AI?

**Technically Yes, but Limited:**

The system uses **statistical learning** (not deep learning) via the **Z-Score method**:

1. **No neural network** (no weights, layers, backprop)
2. **No labeled training data** needed
3. **Unsupervised learning**: Learns patterns from observed traffic
4. **Baseline modeling**: Each IP's "normal behavior" is its moving average

### How the "AI" Works

#### Phase 1: Learning (Batches 1-3)

```python
for each packet in batch:
    history[source_ip].append(packet.size)
    # Growing history: [100], [100, 102], [100, 102, 101]
```

After batch 3: Each IP has ~3 data points representing its typical behavior.

#### Phase 2: Detection (Batches 4+)

```python
history = [100, 102, 101]     # 3 samples from this IP
mean = 101                     # Average packet size
stdev = 1.0                    # Consistency (low = predictable)

new_packet_size = 150          # Unusual packet arrives
z_score = (150 - 101) / 1.0 = 49.0

if |z_score| > 3.0:  # 99.7% confidence this is abnormal
    trigger anomaly
```

### Why This Approach?

| Aspect | Benefit |
|--------|---------|
| **Unsupervised** | No labeled "attack" data required |
| **Adaptive** | Learns per-IP normal behavior |
| **Real-time** | O(1) computation per packet |
| **Interpretable** | Z-score tells magnitude of deviation |
| **Stateless** | No model file to load |

### Limitations

1. **Delayed activation:** First 3 batches are "blind" (learning phase)
2. **Assumes clean baseline:** If first 3 batches contain attacks, baseline is corrupted
3. **Univariate:** Only looks at packet size, not protocol, port, or time-based patterns
4. **Normal distribution assumption:** If traffic is bimodal, Z-score may fail

### Potential ML Enhancements

If this were a real production system:

1. **Multivariate analysis:** Consider [protocol, port, size, time_delta] together
2. **Isolation Forest:** Detect anomalies via tree isolation
3. **LSTM RNN:** Learn temporal patterns (sequence-based attacks)
4. **Clustering:** K-means on packet features to find attack clusters
5. **Autoencoders:** Learn compressed normal traffic representation, flag reconstructions >threshold

---

## Database Anomaly Tracking

### Current State

**Issue:** Devices table has no field marking them as "having anomalies"

**Options to Add:**

**Option A: Add anomaly_count (Conservative)**
```sql
ALTER TABLE devices ADD COLUMN anomaly_count INTEGER DEFAULT 0;
```
- Updates on each anomaly detection
- Quick query: `SELECT * FROM devices WHERE anomaly_count > 0`

**Option B: Add anomaly_flag (Binary)**
```sql
ALTER TABLE devices ADD COLUMN has_anomalies INTEGER DEFAULT 0;
```
- Boolean (0/1) set to 1 on first anomaly
- Minimal storage, fast queries

**Recommendation:** Option A (anomaly_count) provides more insights.

---

## Summary

The system implements **dual-strategy anomaly detection**:

1. **Rules** (DDoS, PortScan, Size) - deterministic, fast
2. **Statistics** (Z-Score) - adaptive, probability-based

Data flows: **User Input → Menu → Packet Generation/Loading → Device Tracking → Detection → Events → Persistence & Display → Report**

All components use **interfaces** (EventManager, DatabaseService) enabling loose coupling and testability.

The "AI" is **unsupervised statistical learning** that adapts per-source-IP, enabling anomaly detection without labeled training data.

