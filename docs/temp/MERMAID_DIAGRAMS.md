# System Architecture Flow Diagram

## Complete Request-to-Detection Flow

```mermaid
graph TD
    A["🔌 USER INPUT"] -->|Option 1-6| B["📋 MENU DISPATCHER"]
    
    B -->|Option 1| C1["🎲 SIMULATE TRAFFIC"]
    B -->|Option 2| C2["⌨️ MANUAL ENTRY"]
    B -->|Option 3| C3["📂 LOAD FILE"]
    B -->|Option 4| C4["📊 SHOW REPORT"]
    B -->|Option 5| C5["🗑️ CLEAR DB"]
    B -->|Option 6| C6["🚪 EXIT"]
    
    C1 --> D["🔄 PROCESS PACKETS"]
    C2 --> D
    C3 --> D
    C4 --> R1["📈 Query Database"]
    C5 --> R2["🧹 Clear All Tables"]
    C6 --> R3["⏹️ Shutdown"]
    
    D --> E["👁️ ENSURE DEVICES"]
    E -->|For each source_ip| E1["Check: Device in DB?"]
    E1 -->|YES| E2["Update last_seen, packet_count"]
    E1 -->|NO| E3["Create new Device"]
    E2 --> F
    E3 --> E4["Save Device to DB"]
    E4 --> F
    
    F["💾 SAVE PACKETS"]
    F -->|For each packet| F1["INSERT INTO packets"]
    F1 -->|Auto-increment| F2["packet.id = lastrowid"]
    F2 --> G
    
    G["🔍 RUN DETECTION"]
    G --> G1["👁️ Display Progress Bar"]
    G1 --> H["⚡ RULE-BASED CHECKS"]
    
    H --> H1["Count packets per IP"]
    H1 -->|> 100 in batch| H1A["🚨 DDoS Rule Fired"]
    H1 -->|≤ 100| H1B["✓ DDoS Clean"]
    
    H --> H2["Count unique ports per IP"]
    H2 -->|> 20| H2A["🚨 PortScan Rule Fired"]
    H2 -->|≤ 20| H2B["✓ PortScan Clean"]
    
    H --> H3["Check max packet size"]
    H3 -->|> 65000 bytes| H3A["🚨 UnusualSize Rule Fired"]
    H3 -->|≤ 65000| H3B["✓ Size Clean"]
    
    H1A --> I["⚡ STATISTICAL CHECKS"]
    H1B --> I
    H2A --> I
    H2B --> I
    H3A --> I
    H3B --> I
    
    I --> I1["📊 Z-Score Analysis"]
    I1 -->|Batch ≤ 3| I2["🏗️ Building baseline (x/3)"]
    I2 --> J
    I1 -->|Batch > 3| I3["Calculate: μ (mean), σ (stdev)"]
    I3 --> I4["For each packet: z = size - μ / σ"]
    I4 -->|abs z > 3.0| I5A["🚨 Z-Score Anomaly"]
    I4 -->|abs z ≤ 3.0| I5B["✓ Z-Score Clean"]
    I5A --> J
    I5B --> J
    
    H1A --> K["📤 EMIT EVENTS"]
    H2A --> K
    H3A --> K
    I5A --> K
    
    K -->|emit_anomaly_detected| K1["Create Anomaly object"]
    K1 --> L["🔊 PUBLISH TO SUBSCRIBERS"]
    K -->|emit_ddos_suspected| K2["Alert type: DDoS"]
    K2 --> L
    K -->|emit_unusual_traffic| K3["Alert type: PortScan"]
    K3 --> L
    
    L --> L1["📝 FileLogger"]
    L1 --> L1A["Append to log.txt"]
    
    L --> L2["💾 DatabaseService"]
    L2 --> L2A["INSERT INTO anomalies"]
    L2A --> L2B["anomaly.id = lastrowid"]
    
    L --> L3["🖥️ Console Output"]
    L3 --> L3A["Display anomaly summary"]
    
    J --> M["🎬 DISPLAY BATCH RESULTS"]
    M --> M1["Show rule status"]
    M --> M2["Show Z-score status"]
    M --> M3["Show anomalies fired"]
    
    M1 --> N{Next batch?}
    M2 --> N
    M3 --> N
    
    N -->|Yes| G
    N -->|No| O["📋 FINAL REPORT"]
    
    O --> O1["Total packets processed"]
    O --> O2["Total anomalies detected"]
    O --> O3["Top 5 IPs by activity"]
    O --> O4["Suspicious packets count"]
    
    O1 --> P["🔄 RETURN TO MENU"]
    O2 --> P
    O3 --> P
    O4 --> P
    
    P --> A
    
    R1 --> P
    R2 --> P
    R3 --> END["✅ Program Exit"]
    
    style A fill:#4CAF50,color:#fff
    style G fill:#2196F3,color:#fff
    style H fill:#FF9800,color:#fff
    style I fill:#9C27B0,color:#fff
    style K fill:#F44336,color:#fff
    style L fill:#F44336,color:#fff
    style O fill:#4CAF50,color:#fff
    style END fill:#757575,color:#fff
```

---

## Data Flow Layers

```mermaid
graph LR
    subgraph UI["🖥️ UI LAYER"]
        MENU["menu.py<br/>Interactive Menu"]
        FEED["live_feed.py<br/>Real-time Progress"]
        REPORT["report.py<br/>Rich Tables"]
        CONSOLE["console.py<br/>Styling"]
    end
    
    subgraph SERVICE["⚙️ SERVICE LAYER"]
        DET["anomaly_detector.py<br/>Detection Engine"]
        DB["database_service.py<br/>SQLite Layer"]
        LOG["file_logger.py<br/>Audit Logging"]
        LOAD["packet_loader.py<br/>File Import"]
        ANALYZE["traffic_analyzer.py<br/>LINQ Queries"]
    end
    
    subgraph EVENTS["📤 EVENT BUS"]
        EM["event_manager.py<br/>Pub/Sub Dispatcher"]
    end
    
    subgraph MODELS["📦 DATA MODELS"]
        PKT["NetworkPacket"]
        ANM["Anomaly"]
        DEV["Device"]
    end
    
    subgraph SIM["🎲 SIMULATION"]
        SIMULATOR["traffic_simulator.py"]
    end
    
    subgraph PERSIST["💾 PERSISTENCE"]
        SQLITE["SQLite3<br/>anomalies.db"]
    end
    
    MENU -->|Calls| DET
    MENU -->|Calls| LOAD
    MENU -->|Displays| REPORT
    FEED -->|Wraps| DET
    DET -->|Creates| ANM
    DET -->|Publishes| EM
    SIMULATOR -->|Generates| PKT
    LOAD -->|Parses| PKT
    DB -->|CRUD| ANM
    DB -->|CRUD| PKT
    DB -->|CRUD| DEV
    EM -->|Notifies| LOG
    EM -->|Notifies| DB
    REPORT -->|Queries| DB
    ANALYZE -->|Analyzes| PKT
    DB -->|Read/Write| SQLITE
    
    style UI fill:#BBDEFB
    style SERVICE fill:#C8E6C9
    style EVENTS fill:#FFCCBC
    style MODELS fill:#F8BBD0
    style SIM fill:#FFF9C4
    style PERSIST fill:#D1C4E9
```

---

## Detection Algorithm Flow

```mermaid
graph TD
    START["📥 Batch of Packets Arrives"] --> SPLIT["Split per source_ip"]
    
    SPLIT --> IP["For each source_ip"]
    
    IP --> RULE1["🔍 RULE 1: DDoS Check"]
    RULE1 --> RULE1A["Count: packets from this IP"]
    RULE1A -->|count > 100| RULE1B["⚠️ DDoS Threshold Hit"]
    RULE1A -->|count ≤ 100| RULE1C["✓ DDoS Clean"]
    
    RULE1B --> RULE1D["Create Anomaly<br/>type=DDoS, severity=High"]
    RULE1D --> EVENT1["emit_ddos_suspected()"]
    RULE1C --> RULE2
    EVENT1 --> RULE2
    
    RULE2["🔍 RULE 2: PortScan Check"]
    RULE2 --> RULE2A["Count: unique dest_port"]
    RULE2A -->|count > 20| RULE2B["⚠️ PortScan Threshold Hit"]
    RULE2A -->|count ≤ 20| RULE2C["✓ PortScan Clean"]
    
    RULE2B --> RULE2D["Create Anomaly<br/>type=PortScan, severity=High"]
    RULE2D --> EVENT2["emit_unusual_traffic()"]
    RULE2C --> RULE3
    EVENT2 --> RULE3
    
    RULE3["🔍 RULE 3: Unusual Size Check"]
    RULE3 --> RULE3A["Check: max packet size"]
    RULE3A -->|size > 65000| RULE3B["⚠️ Size Threshold Hit"]
    RULE3A -->|size ≤ 65000| RULE3C["✓ Size Clean"]
    
    RULE3B --> RULE3D["Create Anomaly<br/>type=UnusualSize, severity=Medium"]
    RULE3D --> EVENT3["emit_anomaly_detected()"]
    RULE3C --> ZSCORE
    EVENT3 --> ZSCORE
    
    ZSCORE["📊 STATISTICAL: Z-Score Analysis"] --> ZCHECK["Check batch number"]
    ZCHECK -->|batch ≤ 3| ZLEARN["🏗️ Learning Phase"]
    ZLEARN --> ZLEARN1["Append packet sizes to history[source_ip]"]
    ZLEARN1 --> ZLEARN2["Status: building baseline (batch/3)"]
    ZLEARN2 --> END
    
    ZCHECK -->|batch > 3| ZCALC["📐 Calculate Statistics"]
    ZCALC --> ZCALC1["μ = mean(history[:-1])"]
    ZCALC --> ZCALC2["σ = stdev(history[:-1])"]
    
    ZCALC1 --> ZCHECK2{σ = 0?}
    ZCALC2 --> ZCHECK2
    ZCHECK2 -->|YES| ZFLAT["⏭️ Skip (flat baseline)"]
    ZCHECK2 -->|NO| ZSCORE_CALC
    
    ZFLAT --> END
    
    ZSCORE_CALC["z = (size - μ) / σ"] --> ZTHRESH{abs z > 3.0?}
    ZTHRESH -->|YES| ZANOM["🚨 Z-Score Anomaly"]
    ZTHRESH -->|NO| ZCLEAN["✓ Z-Score Clean"]
    
    ZANOM --> ZANOM1["Create Anomaly<br/>type=ZScoreAnomaly<br/>severity=Critical or High"]
    ZANOM1 --> EVENT4["emit_anomaly_detected()"]
    ZCLEAN --> END
    EVENT4 --> END
    
    END["✅ Detection Complete<br/>Return anomalies list"] --> COLLECTOR["Collect all anomalies<br/>from all rules"]
    COLLECTOR --> RETURN["Return list to caller"]
    
    style START fill:#4CAF50,color:#fff
    style IP fill:#2196F3,color:#fff
    style RULE1 fill:#FF9800,color:#fff
    style RULE2 fill:#FF9800,color:#fff
    style RULE3 fill:#FF9800,color:#fff
    style ZSCORE fill:#9C27B0,color:#fff
    style ZANOM fill:#F44336,color:#fff
    style END fill:#4CAF50,color:#fff
```

---

## Event Propagation Chain

```mermaid
graph LR
    DET["AnomalyDetector<br/>analyze_packets()"]
    
    DET -->|emit_anomaly_detected| EM["EventManager<br/>publish"]
    DET -->|emit_ddos_suspected| EM
    DET -->|emit_unusual_traffic| EM
    
    EM --> SUB1["FileLogger<br/>Subscriber"]
    EM --> SUB2["DatabaseService<br/>Subscriber"]
    EM --> SUB3["Console Output<br/>Subscriber"]
    
    SUB1 -->|Callback| LOG1["log_anomaly()"]
    SUB1 -->|Callback| LOG2["log_ddos_suspected()"]
    SUB1 -->|Callback| LOG3["log_unusual_traffic()"]
    
    LOG1 --> LOGFILE["📝 Append to log.txt"]
    LOG2 --> LOGFILE
    LOG3 --> LOGFILE
    
    SUB2 -->|Callback| DB1["save_anomaly()"]
    DB1 --> DBWRITE["💾 INSERT INTO anomalies"]
    
    SUB3 -->|Callback| CONS1["Display in LiveDetector"]
    CONS1 --> DISPLAY["🖥️ Print anomaly summary"]
    
    LOGFILE --> END["✅ Event fully propagated"]
    DBWRITE --> END
    DISPLAY --> END
    
    style DET fill:#2196F3,color:#fff
    style EM fill:#FF9800,color:#fff
    style SUB1 fill:#4CAF50,color:#fff
    style SUB2 fill:#4CAF50,color:#fff
    style SUB3 fill:#4CAF50,color:#fff
    style END fill:#9C27B0,color:#fff
```

---

## Database Relationships

```mermaid
erDiagram
    DEVICES ||--o{ PACKETS : "has"
    PACKETS ||--o{ ANOMALIES : "flagged_in"
    
    DEVICES {
        int id PK
        string ip_address UK
        string device_type
        boolean is_blacklisted
        datetime first_seen
        datetime last_seen
        int packet_count
    }
    
    PACKETS {
        int id PK
        string source_ip
        string dest_ip
        string protocol
        int size
        int port
        datetime timestamp
        int device_id FK
    }
    
    ANOMALIES {
        int id PK
        int packet_id FK
        string type
        string severity
        datetime detected_at
        string description
        boolean is_resolved
    }
```

