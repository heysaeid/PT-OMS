# OM-Demo
```mermaid
graph TD
    %% Input Sources & Channels
    subgraph "Input Sources & Channels"
        direction LR
        A["Mobile & Web Apps"] -- "Real-time Events" --> KAFKA
        DB1["Legacy Databases (e.g., CRM)"] -- "CDC Events" --> DEBEZIUM[Debezium] --> KAFKA
    end

    %% Real-time Ingestion & Storage
    subgraph "Real-time Ingestion & Storage"
        KAFKA["<b>Apache Kafka</b><br/>Central Event Bus"] --> KC["Kafka Connect (S3 Sink)"] --> S3["<b>AWS S3</b><br/>🌊 Data Lake<br/>Permanent Raw Archive (Parquet)"]
    end

    %% Operational Path
    subgraph "Operational Path (Real-time Serving)"
        direction LR
        KAFKA -- "Live Order Events" --> SPARK_STREAM["<b>Spark Streaming</b><br/>Processes & Denormalizes"] --> ES["<b>Elasticsearch</b><br/>Fast Search Layer<br/>(Recent Data)"]
    end

    %% Analytical Path (Phased)
    subgraph "Analytical Path (Phased Approach)"
        direction TB

        subgraph "Phase 1: General Analytics (Lakehouse Model)"
            PRESTO["<b>Presto / Trino</b><br/>Interactive SQL Engine on Data Lake"]
            S3 -- "Full Historical Data" --> PRESTO
        end

        subgraph "Phase 2 (Future Optimization): High-Speed Dashboards"
            INGEST_OLAP["Data Ingestion<br/>(Spark Batch)"]
            CLICKHOUSE["<b>ClickHouse / StarRocks</b><br/>High-Performance OLAP DB"]
            S3 -- "Loads Curated Data" --> INGEST_OLAP --> CLICKHOUSE
        end
    end

    %% API & Consumers
    subgraph "API & Consumers"
        API["<b>Order Repository API</b><br/>(Python/FastAPI)"]
        API -- "Hot Queries (e.g., last 2 years)" --> ES
        API -- "Cold Queries (e.g., > 2 years)" --> PRESTO
    end

    %% End Users
    subgraph "End Users"
        direction TB
        SERVICES["Other Turkcell Services"] --> API
        ANALYSTS["Data Analysts & Scientists"] --> PRESTO
        MANAGERS["Business Managers"] --> CLICKHOUSE
    end
```# PT-OMS
