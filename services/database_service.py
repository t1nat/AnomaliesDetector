from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime

from models import Anomaly, Device, NetworkPacket


class DatabaseService:
    def __init__(self, database_path: str = "anomalies.db") -> None:
        self._path = Path(database_path)
        self._connection = sqlite3.connect(self._path)
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def close(self) -> None:
        self._connection.close()

    def save_packet(self, packet: NetworkPacket) -> int:
        cursor = self._connection.execute(
            """
            INSERT INTO packets (source_ip, dest_ip, protocol, size, port, timestamp, device_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                packet.source_ip,
                packet.dest_ip,
                packet.protocol,
                packet.size,
                packet.port,
                packet.timestamp.isoformat(),
                packet.device_id,
            ),
        )
        self._connection.commit()
        packet.id = cursor.lastrowid
        return cursor.lastrowid

    def save_anomaly(self, anomaly: Anomaly) -> int:
        cursor = self._connection.execute(
            """
            INSERT INTO anomalies (packet_id, type, severity, detected_at, description, is_resolved)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                anomaly.packet_id,
                anomaly.type,
                anomaly.severity,
                anomaly.detected_at.isoformat(),
                anomaly.description,
                int(anomaly.is_resolved),
            ),
        )
        self._connection.commit()
        anomaly.id = cursor.lastrowid
        return cursor.lastrowid

    def save_device(self, device: Device) -> int:
        cursor = self._connection.execute(
            """
            INSERT INTO devices (ip_address, device_type, is_blacklisted, first_seen, last_seen, packet_count, anomaly_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ip_address) DO UPDATE SET
                device_type = excluded.device_type,
                is_blacklisted = excluded.is_blacklisted,
                last_seen = excluded.last_seen,
                packet_count = excluded.packet_count,
                anomaly_count = excluded.anomaly_count
            """,
            (
                device.ip_address,
                device.device_type,
                int(device.is_blacklisted),
                device.first_seen.isoformat(),
                device.last_seen.isoformat(),
                device.packet_count,
                device.anomaly_count,
            ),
        )
        self._connection.commit()
        if cursor.lastrowid:
            device.id = cursor.lastrowid
        return cursor.lastrowid or self._get_device_id(device.ip_address)

    def get_all_anomalies(self) -> list[Anomaly]:
        rows = self._connection.execute("SELECT id, packet_id, type, severity, detected_at, description, is_resolved FROM anomalies ORDER BY id").fetchall()
        return [
            Anomaly(
                id=row[0],
                packet_id=row[1],
                type=row[2],
                severity=row[3],
                detected_at=datetime.fromisoformat(row[4]),
                description=row[5],
                is_resolved=bool(row[6]),
            )
            for row in rows
        ]

    def get_blacklisted_devices(self) -> list[Device]:
        rows = self._connection.execute("SELECT id, ip_address, device_type, is_blacklisted, first_seen, last_seen, packet_count, anomaly_count FROM devices WHERE is_blacklisted = 1 ORDER BY id").fetchall()
        return [self._device_from_row(row) for row in rows]

    def get_all_devices(self) -> list[Device]:
        rows = self._connection.execute(
            "SELECT id, ip_address, device_type, is_blacklisted, first_seen, last_seen, packet_count, anomaly_count FROM devices ORDER BY id"
        ).fetchall()
        return [self._device_from_row(row) for row in rows]

    def get_packets_by_ip(self, source_ip: str) -> list[NetworkPacket]:
        rows = self._connection.execute("SELECT id, source_ip, dest_ip, protocol, size, port, timestamp, device_id FROM packets WHERE source_ip = ? ORDER BY id", (source_ip,)).fetchall()
        return [
            NetworkPacket(
                id=row[0],
                source_ip=row[1],
                dest_ip=row[2],
                protocol=row[3],
                size=row[4],
                port=row[5],
                timestamp=datetime.fromisoformat(row[6]),
                device_id=row[7],
            )
            for row in rows
        ]

    def get_device_id_by_ip(self, ip_address: str) -> int:
        return self._get_device_id(ip_address)
    
    def increment_device_anomaly_count(self, packet_id: int) -> None:
        """Increment anomaly_count for the device associated with this packet"""
        # Get device_id from packet
        row = self._connection.execute(
            "SELECT device_id FROM packets WHERE id = ?",
            (packet_id,)
        ).fetchone()
        
        if row and row[0]:
            device_id = row[0]
            # Increment anomaly_count in database
            self._connection.execute(
                "UPDATE devices SET anomaly_count = anomaly_count + 1 WHERE id = ?",
                (device_id,)
            )
            self._connection.commit()

    def clear_all(self) -> None:
        self._connection.executescript(
            """
            DELETE FROM anomalies;
            DELETE FROM packets;
            DELETE FROM devices;
            """
        )
        self._connection.commit()

    def _create_tables(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                ip_address TEXT UNIQUE NOT NULL,
                device_type TEXT NOT NULL,
                is_blacklisted INTEGER NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                packet_count INTEGER NOT NULL,
                anomaly_count INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY,
                source_ip TEXT NOT NULL,
                dest_ip TEXT NOT NULL,
                protocol TEXT NOT NULL,
                size INTEGER NOT NULL,
                port INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                device_id INTEGER,
                FOREIGN KEY (device_id) REFERENCES devices(id)
            );

            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY,
                packet_id INTEGER,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                detected_at TEXT NOT NULL,
                description TEXT NOT NULL,
                is_resolved INTEGER NOT NULL,
                FOREIGN KEY (packet_id) REFERENCES packets(id)
            );
            """
        )
        self._connection.commit()
        self._migrate_add_anomaly_count()
    
    def _migrate_add_anomaly_count(self) -> None:
        """Add anomaly_count column if it doesn't exist (migration for existing DBs)"""
        try:
            cursor = self._connection.execute("PRAGMA table_info(devices)")
            columns = [row[1] for row in cursor.fetchall()]
            if "anomaly_count" not in columns:
                self._connection.execute("ALTER TABLE devices ADD COLUMN anomaly_count INTEGER NOT NULL DEFAULT 0")
                self._connection.commit()
        except Exception:
            pass  # Column likely already exists

    def _get_device_id(self, ip_address: str) -> int:
        row = self._connection.execute("SELECT id FROM devices WHERE ip_address = ?", (ip_address,)).fetchone()
        return int(row[0])

    def _device_from_row(self, row: tuple[object, ...]) -> Device:
        return Device(
            id=row[0],
            ip_address=row[1],
            device_type=row[2],
            is_blacklisted=bool(row[3]),
            first_seen=datetime.fromisoformat(row[4]),
            last_seen=datetime.fromisoformat(row[5]),
            packet_count=row[6],
            anomaly_count=row[7],
        )