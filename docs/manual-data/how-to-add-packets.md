# How to Add Packets From Files

Follow these steps to load packets from `data/sample_packets.json` or `data/sample_packets.csv`.

## Steps

1. Open `data/sample_packets.json` or `data/sample_packets.csv` in a text editor.
2. Copy an existing packet row and edit the values.
3. Keep `source_ip` and `dest_ip` as valid IP addresses.
4. Use `TCP`, `UDP`, or `ICMP` for the protocol.
5. Use a size greater than `65000` to trigger the unusual-size rule.
6. Save the file.
7. Run `python main.py`.
8. Choose option 3 in the menu and enter the file name.

## Attack Scenarios

| Scenario | source_ip | protocol | size | port | Triggers |
|---|---|---|---|---|---|
| Normal | 192.168.1.5 | TCP | 512 | 80 | nothing |
| DDoS | 10.10.10.1 | TCP | 512 | 80 | DDoS rule when repeated 101+ times |
| Port scan | 10.10.10.2 | TCP | 128 | 1..25 | Port scan rule |
| Oversized packet | 10.10.10.3 | UDP | 66000 | 53 | Unusual size rule |
