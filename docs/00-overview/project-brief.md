# Project Brief

## Purpose

Build a Python-based network anomaly detection system that simulates traffic, detects suspicious behavior, logs events, and persists results to SQLite.

## Problem Statement

The project needs to identify abnormal network behavior such as DDoS patterns, port scanning, and unusually large packets without relying on external datasets.

## Success Criteria

- Simulated traffic can be generated for normal and attack scenarios.
- Rule-based detection can flag the first set of anomalies.
- Events can notify subscribers when anomalies are detected.
- Packets, anomalies, and devices can be stored in SQLite.
- The final program runs end to end from simulation to summary output.

## Scope

### In Scope

- Traffic simulation
- Packet, anomaly, and device models
- Rule-based anomaly detection
- Event handling and file logging
- SQLite persistence
- Statistical Z-score detection in the later phase

### Out of Scope

- Real packet capture from a network interface
- Third-party machine learning libraries
- External datasets
- Web UI or dashboard

## Target Deliverable

A command-line Python application that runs a complete simulation cycle and produces:

- console output
- log file entries
- SQLite records
- a summary of detected anomalies
