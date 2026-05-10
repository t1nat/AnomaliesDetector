# Validation Plan

## Purpose

Verify that each layer works before moving to the next one.

## What to Validate

### Models

- Fields exist and are named consistently.
- Instances can be created from real and sample data.

### Event System

- Subscribers are called when events fire.
- Anomalies reach the logger through callbacks.

### Detection

- DDoS rules trigger when packet rate exceeds the threshold.
- Port scan rules trigger when too many destination ports are used.
- Large packet rules trigger for unusual packet sizes.

### Simulation

- Normal traffic stays below attack thresholds.
- DDoS traffic is clearly distinguishable.
- Port scan traffic touches many ports.

### Analysis

- Top IP and grouping queries return correct summaries.
- Suspicious packet filters match the detection rules.

### Persistence

- Tables are created correctly.
- Save methods write data successfully.
- Query methods return mapped Python objects.

### Z-Score Detection

- Sliding window values are computed correctly.
- Higher-than-normal behavior produces a meaningful score.
- Severity mapping is consistent.

### End-to-End Run

- One command can run the full workflow.
- Output includes summary, log file entries, and database records.

## Validation Approach

- Start with manual smoke tests.
- Add focused unit-style checks for each service.
- Verify the full pipeline after each major phase.

## Exit Criteria

- Every major service has been exercised at least once.
- The final workflow completes without manual recovery steps.
- Generated output matches the documented project behavior.
