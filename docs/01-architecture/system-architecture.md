# System Architecture

## Architecture Style

Use a small layered architecture with clear separation of responsibilities:

- `models` for data structures
- `simulation` for traffic generation
- `services` for detection, persistence, and analysis
- `events` for notification flow
- `main.py` as the orchestration entry point

## Core Components

### Models

- `NetworkPacket` stores packet fields and timestamps.
- `Anomaly` stores detection metadata and severity.
- `Device` stores source host metadata and blacklist state.

### Simulation

- `TrafficSimulator` generates reproducible traffic batches.
- It should support normal traffic, DDoS traffic, and port scan traffic.

### Detection

- `AnomalyDetector` evaluates packets using rule-based thresholds first.
- Later, it also applies Z-score analysis over sliding windows.

### Analysis

- `TrafficAnalyzer` provides query-style summary methods over packet collections.
- Keep it read-only and separate from detection logic.

### Events

- `EventManager` publishes anomaly and traffic events.
- Subscribers receive callbacks for logging and persistence.

### Persistence

- `DatabaseService` owns SQLite schema creation and all database access.
- Detection code should not talk to SQLite directly.

### Logging

- `FileLogger` writes timestamped entries for audits and review.

## Data Flow

1. `TrafficSimulator` creates packets.
2. `TrafficAnalyzer` summarizes the packet stream when needed.
3. `AnomalyDetector` checks packets against detection rules.
4. `EventManager` notifies subscribers about confirmed anomalies.
5. `FileLogger` records activity.
6. `DatabaseService` persists packets, anomalies, and devices.

## Design Rules

- Keep each class focused on one responsibility.
- Prefer simple function boundaries over deep inheritance.
- Pass data between components using plain objects.
- Keep `main.py` thin and orchestration-only.
