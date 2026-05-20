# Sample Data

Use these files with menu option 3.

## Required Fields

- `source_ip` - valid IP address
- `dest_ip` - valid IP address
- `protocol` - `TCP`, `UDP`, or `ICMP`
- `size` - packet size in bytes, integer greater than 0
- `port` - destination port, integer from 1 to 65535

## Behavior

- Packets larger than 65,000 bytes trigger the unusual-size rule.
- Repeated entries from the same source IP can trigger DDoS or port-scan rules.
- The loader fills in `timestamp` automatically if it is omitted.

## Files

- `sample_packets.json` - JSON list of packet objects
- `sample_packets.csv` - CSV version of the same packet list
