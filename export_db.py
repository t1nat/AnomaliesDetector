#!/usr/bin/env python3
"""Export database to human-readable JSON format."""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

db_path = 'anomalies.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Export all data
data = {
    'exported_at': datetime.now().isoformat(),
    'devices': [],
    'packets': [],
    'anomalies': []
}

# Get devices
cursor.execute('SELECT * FROM devices ORDER BY id')
for row in cursor.fetchall():
    data['devices'].append(dict(row))

# Get packets
cursor.execute('SELECT * FROM packets ORDER BY id')
for row in cursor.fetchall():
    data['packets'].append(dict(row))

# Get anomalies
cursor.execute('SELECT * FROM anomalies ORDER BY id')
for row in cursor.fetchall():
    data['anomalies'].append(dict(row))

conn.close()

# Write to JSON
Path('docs/temp/database_export.json').write_text(json.dumps(data, indent=2))
print(f"✓ Exported {len(data['devices'])} devices, {len(data['packets'])} packets, {len(data['anomalies'])} anomalies")
print(f"✓ Saved to docs/temp/database_export.json")
