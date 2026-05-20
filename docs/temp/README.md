# Technical Documentation - Index

This folder contains comprehensive technical documentation for the **Network Anomaly Detection System**.

---

## Files in This Folder

### 1. **TECHNICAL_FLOW.md** - Complete System Guide

**What it covers:**
- System overview and architecture
- Layered design (UI → Services → Models → Database)
- Module structure and responsibilities
- Complete end-to-end request flow with detailed examples
- Database schema with 3 tables and relationships
- Full documentation of all 9 core classes
- Detection methods (Rule-based + Z-Score)
- AI/algorithm explanation (unsupervised statistical learning)

**Best for:** Understanding how the system works end-to-end

**Key Sections:**
- System Overview (metrics, tech stack)
- Architecture (layered design, module structure)
- Data Flow (request path with diagrams)
- Core Classes (NetworkPacket, Anomaly, Device, EventManager, AnomalyDetector, DatabaseService, LiveDetector, PacketLoader, TrafficSimulator)
- Detection Methods (Rule 1: DDoS, Rule 2: PortScan, Rule 3: UnusualSize, Z-Score statistical analysis)
- Database Schema (3 tables explained)
- AI Explanation (Z-score algorithm, unsupervised learning, limitations, ML enhancements)

---

### 2. **MERMAID_DIAGRAMS.md** - Visual Process Flows

**What it covers:**
- Complete request-to-detection flowchart (mermaid graph)
- Data flow layers (UI → Service → Events → Models → Persistence)
- Detection algorithm flow (rules → statistics → anomalies)
- Event propagation chain (pub/sub system)
- Database entity-relationship diagram (ER model)

**Best for:** Visual learners, presentations, understanding flow without reading prose

**Diagrams Included:**
1. **Request-to-Detection Flow** - Complete user interaction path
2. **Data Flow Layers** - System architecture with 6 layers
3. **Detection Algorithm Flow** - Detailed rule checks and Z-score logic
4. **Event Propagation Chain** - How anomalies trigger subscribers
5. **Database Relationships** - ER diagram with all 3 tables

**How to use:**
- Copy mermaid code into [mermaid.live](https://mermaid.live) for interactive visualization
- Or use VS Code Markdown Preview with Mermaid extension

### 3. **DATABASE_RECOMMENDATIONS.md** - Schema Analysis & Field Recommendations

**What it covers:**
- Analysis: Is there a field for "devices flagged as anomalies"? (Answer: **No** → **Now Yes!**)
- Current device fields (7 fields → 8 fields after implementation)
- Problem statement (requires JOIN to find anomalous devices)
- **3 recommended solutions** with implementation status
- **✅ IMPLEMENTATION COMPLETE** - Option A deployed
- Database schema (before/after)
- Test results with real anomaly data
- Backward compatibility notes

**Best for:** Understanding database design decisions and implementation details

**Key Finding:** `anomaly_count` field is now live in production with:
- Automatic migration for existing databases
- Auto-increment on anomaly detection
- UI report showing anomalies per device
- 4 fields tracked: packets, anomalies, first_seen, last_seen

---

### 4. **IMPLEMENTATION_COMPLETE.md** - Implementation Summary ✅

**What it covers:**
- Status: ✅ **Complete and Tested** (May 10, 2026)
- All files changed (4 files modified)
- Changes to Device model, database schema, data access layer, persistence, UI
- Test results (5/5 passing, integration verified)
- Verification checklist (database integrity, anomaly attribution)
- Backward compatibility (auto-migration for existing DBs)
- Usage examples (queries, UI display)
- Performance impact (negligible)
- Optional enhancements (future improvements)

**Best for:** Developers implementing similar features, understanding deployment process

**Key Stats:**
- 25 devices tracked
- 357 packets analyzed
- 6 anomalies detected and correctly attributed
- 0 test failures

---

### 5. **database_export.json** - Human-Readable Database Copy

**What it contains:**
- Complete snapshot of current database state
- Export timestamp (ISO8601)
- **Devices table** (25 records with anomaly_count) - all IP addresses with metadata
- **Packets table** (357 records) - all network traffic captured
- **Anomalies table** (6 records) - all detections made with device attribution

**Format:** Valid JSON with 2-space indentation for readability

**Best for:**
- Backup reference
- Offline analysis
- Sharing database state without SQLite
- Loading into analysis tools (pandas, etc.)

**View the contents:**
```bash
# Pretty-print in terminal
python -c "import json; print(json.dumps(json.load(open('database_export.json')), indent=2))" | less

# Or open in VS Code with JSON viewer
```

**Data Included:**
Each device record now has:
- IP address, device type, blacklist status, first/last seen timestamps, packet count, **anomaly_count**

Each packet record has:
- Source/dest IP, protocol, size, port, timestamp, device foreign key

Each anomaly record has:
- Packet foreign key, anomaly type, severity, detected_at timestamp, description, resolved flag

---

## Quick Navigation by Question

### "How does the system work end-to-end?"
→ Read [TECHNICAL_FLOW.md](TECHNICAL_FLOW.md) sections:
- System Overview
- Architecture  
- Data Flow (Complete End-to-End Example)

### "Show me a visual diagram"
→ View [MERMAID_DIAGRAMS.md](MERMAID_DIAGRAMS.md):
- Request-to-Detection Flow
- Data Flow Layers
- Or any of the 5 diagrams

### "Is there a database field for anomalous devices?"
→ Read [DATABASE_RECOMMENDATIONS.md](DATABASE_RECOMMENDATIONS.md):
- **Answer:** ✅ **YES - IMPLEMENTED!**
- Implementation status section
- Current schema with 8 fields
- Test results showing anomaly tracking

### "What was implemented? Show me the details."
→ Read [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md):
- All code changes (4 files)
- Test results (5/5 passing)
- Verification results
- Usage examples

### "What are all the classes and how do they work?"
→ Read [TECHNICAL_FLOW.md](TECHNICAL_FLOW.md) section "Core Classes" (9 classes documented)

### "How does the AI/anomaly detection work?"
→ Read [TECHNICAL_FLOW.md](TECHNICAL_FLOW.md) sections:
- Detection Methods (Rule-based vs Statistical)
- AI & Algorithm Explanation (Z-Score analysis)
- With examples and limitations

### "What's in the database right now?"
→ View [database_export.json](database_export.json)
- 25 devices, 357 packets, 6 anomalies
- All data in human-readable JSON format
- **NEW:** anomaly_count for each device

### "How do requests flow through the system?"
→ View [MERMAID_DIAGRAMS.md](MERMAID_DIAGRAMS.md) diagram:
- "Complete Request-to-Detection Flow"
- Shows all 6 menu options, processing pipeline, event propagation

---

## Key Concepts Explained

### Detection Methods

**Rule-Based (Deterministic):**
- ✓ DDoS: > 100 packets from one IP in single batch
- ✓ PortScan: > 20 unique destination ports from one IP
- ✓ UnusualSize: Packet size > 65,000 bytes

**Statistical (Machine Learning-Inspired):**
- Z-Score: Learns per-IP baseline in first 3 batches
- Flags packets with |z-score| > 3.0 (99.7% confidence abnormal)
- Adapts to each IP's traffic pattern

### Event System

**Pattern:** Observer/Pub-Sub
- **Publisher:** AnomalyDetector
- **Subscribers:** FileLogger, DatabaseService, Console UI
- **Decoupling:** Detection logic doesn't know about persistence

### Database

**3 Tables:**
1. `devices` - Source IP metadata (14 rows)
2. `packets` - Network traffic (131 rows)
3. `anomalies` - Detection results (2 rows)

**Relationships:**
- devices ← 1:N → packets (via device_id)
- packets ← 1:N → anomalies (via packet_id)

---

## How to Use This Documentation

**For developers adding features:**
1. Read [TECHNICAL_FLOW.md](TECHNICAL_FLOW.md) - Architecture section
2. Review [MERMAID_DIAGRAMS.md](MERMAID_DIAGRAMS.md) - Data Flow Layers
3. Check relevant class documentation

**For database tuning:**
1. Start with [DATABASE_RECOMMENDATIONS.md](DATABASE_RECOMMENDATIONS.md)
2. Review [database_export.json](database_export.json) for current data
3. Check [TECHNICAL_FLOW.md](TECHNICAL_FLOW.md) - Database Schema section

**For understanding detection logic:**
1. Read [TECHNICAL_FLOW.md](TECHNICAL_FLOW.md) - Detection Methods section
2. View [MERMAID_DIAGRAMS.md](MERMAID_DIAGRAMS.md) - Detection Algorithm Flow diagram
3. Check AI & Algorithm Explanation section

**For presentations/sharing:**
1. Use mermaid diagrams from [MERMAID_DIAGRAMS.md](MERMAID_DIAGRAMS.md)
2. Reference statistics from [database_export.json](database_export.json)
3. Cite architecture from [TECHNICAL_FLOW.md](TECHNICAL_FLOW.md)

---

## Statistics

**Project Size:**
- 9 Core Classes documented
- 5 Mermaid diagrams created
- 3 Database tables analyzed + **1 column added** ✅
- 2 Detection strategies explained
- 1 Event system (pub/sub pattern)

**Current Database State:**
- 25 devices tracked (↑ from 14)
- 357 packets analyzed (↑ from 131)
- 6 anomalies detected (↑ from 2)
- 100% foreign key integrity
- **✅ anomaly_count field now live**

**Documentation Completeness:**
- ✓ Full architecture documented
- ✓ All classes explained with code examples
- ✓ Data flow traced end-to-end
- ✓ AI/ML algorithm explained
- ✓ Visual diagrams for all major processes
- ✓ Database schema with recommendations
- ✓ Migration guide provided
- ✓ **Implementation guide (NEW)**
- ✓ Test results and verification (NEW)

---

## Next Steps

### ✅ Just Completed: Anomaly Count Implementation

The `anomaly_count` field recommendation has been fully implemented:
- Device model updated with new field
- Database schema migrated with auto-add for existing DBs
- UI report displays anomalies per device
- Event system auto-increments count on anomaly detection
- All tests passing (5/5)
- Integration verified with simulation

**See:** [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) for full details

---

### Optional Future Enhancements

**For statistics:**
```python
def get_anomaly_statistics(database):
    devices = database.get_all_devices()
    return {
        'total_devices': len(devices),
        'suspicious_devices': sum(1 for d if d.anomaly_count > 0),
        'max_anomalies': max(d.anomaly_count for d in devices),
    }
```

**For querying:**
```python
# Query helper method
def get_devices_with_anomalies(database):
    return [d for d in database.get_all_devices() if d.anomaly_count > 0]
```

**For alerting:**
```python
# Flag high-anomaly devices
ALERT_THRESHOLD = 5
suspicious = [d for d in db.get_all_devices() if d.anomaly_count >= ALERT_THRESHOLD]
```

---

**Generated:** May 10, 2026  
**Format:** Markdown + Mermaid + JSON  
**Status:** Complete and ready for use
