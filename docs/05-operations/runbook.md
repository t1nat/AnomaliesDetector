# Operations Runbook

## Purpose

Describe how to run, inspect, and troubleshoot the finished project.

## Prerequisites

- Python installed
- Access to the project root
- Permission to create a log file and SQLite database file

## Run Steps

1. Open a terminal in the project root.
2. Run the application entry point.
3. Review console output for the summary report.
4. Check the log file for anomaly events.
5. Inspect the SQLite database for stored packets and anomalies.

## Expected Outputs

- Console summary of packets processed and anomalies detected
- A log file with timestamped event entries
- A SQLite database containing packets, anomalies, and devices

## Troubleshooting

### No anomalies are detected

- Confirm the simulation mode includes attack traffic.
- Check that the detection thresholds are not too high.

### Database file is not created

- Confirm the application has write permission in the working directory.
- Confirm the database service is being initialized in `main.py`.

### Log file is empty

- Confirm the event subscribers are connected.
- Confirm anomaly events are being emitted.

## Maintenance Notes

- Update this file when run commands or file locations change.
- Keep the summary output aligned with the implementation plan.
