# Data Model

## Entities

### NetworkPacket

Represents one captured or simulated packet.

Fields:
- id
- source_ip
- dest_ip
- protocol
- size
- port
- timestamp
- device_id

### Anomaly

Represents one detected suspicious event.

Fields:
- id
- packet_id
- type
- severity
- detected_at
- description
- is_resolved

### Device

Represents a known source host.

Fields:
- id
- ip_address
- device_type
- is_blacklisted
- first_seen
- last_seen
- packet_count

## SQLite Tables

### packets

- id INTEGER PRIMARY KEY
- source_ip TEXT
- dest_ip TEXT
- protocol TEXT
- size INTEGER
- port INTEGER
- timestamp DATETIME
- device_id INTEGER FK to devices.id

### anomalies

- id INTEGER PRIMARY KEY
- packet_id INTEGER FK to packets.id
- type TEXT
- severity TEXT
- detected_at DATETIME
- description TEXT
- is_resolved BOOLEAN

### devices

- id INTEGER PRIMARY KEY
- ip_address TEXT UNIQUE
- device_type TEXT
- is_blacklisted BOOLEAN
- first_seen DATETIME
- last_seen DATETIME
- packet_count INTEGER

## Relationship Rules

- One device can generate many packets.
- One packet can be linked to zero or one anomaly record.
- An anomaly always references a packet.

## Implementation Notes

- Use foreign keys consistently.
- Store timestamps in a consistent datetime format.
- Keep schema creation inside `DatabaseService`.
- Use simple object mapping methods when loading rows back into Python objects.
