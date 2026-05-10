# Implementation Plan

## Goal

Build the project from zero to a working command-line system in a sequence that keeps each step testable.

## Phase 0: Repository Setup

### Tasks
- Create the project folder structure.
- Add `requirements.txt` even if the project uses only standard library modules.
- Add the docs index and planning files.
- Create the Python package layout under `models`, `services`, `events`, and `simulation`.

### Output
- A clean repository structure that matches the planned architecture.

## Phase 1: Core Models

### Tasks
- Implement `NetworkPacket`, `Anomaly`, and `Device` as dataclasses.
- Add basic validation defaults where needed.
- Confirm the fields line up with the database schema.

### Output
- Data objects that can be used across the rest of the system.

## Phase 2: Event System and Rule-Based Detection

### Tasks
- Implement `EventManager` with subscriber lists.
- Implement `AnomalyDetector` for DDoS, port scan, and unusual packet size checks.
- Add `FileLogger` callbacks.
- Create a simple `main.py` that feeds sample packets through the detector.

### Output
- A working detection pipeline with event notifications.

## Phase 3: Traffic Simulation and Analysis

### Tasks
- Implement `TrafficSimulator` with normal, DDoS, and port scan modes.
- Implement `TrafficAnalyzer` query methods for top IPs, grouped protocols, suspicious packets, and packets per second.
- Confirm that generated data can trigger the planned rules.

### Output
- Repeatable traffic scenarios and inspection methods.

## Phase 4: SQLite Persistence

### Tasks
- Implement `DatabaseService` table creation and connection handling.
- Add save methods for packets, anomalies, and devices.
- Add read methods for reporting and validation.
- Connect event callbacks to persistence actions.

### Output
- A persistent data layer with clean service boundaries.

## Phase 5: Statistical Detection

### Tasks
- Add sliding window tracking per IP.
- Compute mean and standard deviation over packet counts.
- Calculate Z-scores and map them to severity levels.
- Compare Z-score detections with rule-based detections.

### Output
- A second detection layer that catches gradual anomalies.

## Phase 6: End-to-End Integration

### Tasks
- Connect simulator, analyzer, detector, events, logger, and database.
- Add final summary reporting.
- Write setup and run instructions in the root README and docs.
- Clean up code and verify the final flow.

### Output
- A complete project that runs from traffic generation to final report.

## Recommended Execution Order

1. Models
2. Event system
3. Rule-based detector
4. Simulator
5. Analyzer
6. Database
7. Statistical detection
8. Integration and polish
