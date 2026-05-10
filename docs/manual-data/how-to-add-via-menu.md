# How to Add Packets From the Menu

Follow these steps to create a packet directly in the terminal menu.

## Steps

1. Run `python main.py`.
2. Choose option 2.
3. Enter each packet field when prompted.
4. The packet is processed immediately.
5. Any anomaly is logged and stored in the database.
6. Choose option 4 to view the report.

## Manual Entry Example

- Source IP: `192.168.1.99`
- Dest IP: `10.0.0.1`
- Protocol: `TCP`
- Size: `512`
- Port: `80`

## Attack Scenarios

| Scenario | source_ip | protocol | size | port | Triggers |
|---|---|---|---|---|---|
| Normal | 192.168.1.5 | TCP | 512 | 80 | nothing |
| DDoS | 10.10.10.1 | TCP | 512 | 80 | DDoS rule when repeated 101+ times |
| Port scan | 10.10.10.2 | TCP | 128 | 1..25 | Port scan rule |
| Oversized packet | 10.10.10.3 | UDP | 66000 | 53 | Unusual size rule |
