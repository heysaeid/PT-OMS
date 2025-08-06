# Order Repository Service
**Order Repository Service** is a specialized microservice designed to provide efficient and structured access to **Order Management System (OMS)** data. It acts as a centralized read layer for all order-related data, serving both **Operational** and **Analytical** needs through two distinct access paths:

## Operational Path

Provides real-time, transactional views of order data optimized for operational use cases. This includes up-to-date details about orders, statuses, line items, fulfillment, and other data critical for day-to-day workflows.

## Analytical Path

Delivers denormalized, business-oriented views of order data tailored for analytical, reporting, and decision-making processes. This path is optimized for querying patterns related to KPIs, business metrics, and aggregations.

## Key Features

- Unified access to OMS order data  
- Separation of concerns between real-time operations and analytical needs  
- Flexible APIs for both granular and high-level order insights  
- Scalable architecture suitable for enterprise-grade systems  

## Use Cases

- Customer service applications needing real-time order tracking  
- BI tools generating sales reports and operational dashboards  
- Backend services that require clean, query-optimized access to order data  

## High-Level Architecture

```mermaid
graph TD
    %% Input Sources & Channels
    subgraph "Input Sources & Channels"
        direction LR
        A["FulfillmentOrder Service"] -- "Real-time Events" --> KAFKA
        B["Digital Service"] -- "Real-time Events" --> KAFKA
        DB1["Legacy Databases ?"] -- "CDC Events" --> DEBEZIUM[Debezium] --> KAFKA
    end

    %% Real-time Ingestion & Storage
    subgraph "Real-time Ingestion & Storage"
        KAFKA["<b>Apache Kafka</b><br/>Central Event Bus"] --> KC["Kafka Connect (S3 Sink)"] --> S3["<b>S3 (MinIO)</b><br/>Data Lake<br/>Permanent Raw Archive (Parquet)"]
    end

    %% Operational Path
    subgraph "Operational Path (Real-time Serving)"
        direction LR
        KAFKA -- "Live Order Events" --> KFSQK_SPARK_STREAM["<b>ksqlDB | Spark Streaming</b><br/>Processes & Denormalizes"] --> ES["<b>Elasticsearch</b><br/>Fast Search Layer<br/>(Recent Data)"]
    end

    %% Analytical Path (Phased)
    subgraph "Analytical Path (Phased Approach)"
        direction TB

        subgraph "Phase 1: General Analytics (Lakehouse Model)"
            PRESTO["<b>Presto / Trino</b><br/>Interactive SQL Engine on Data Lake"]
            S3 -- "Full Historical Data" --> PRESTO
        end

        subgraph "Phase 2 (Future Optimization): High-Speed Dashboards"
            INGEST_OLAP["Data Ingestion<br/>(ksqlDB | Spark Batch)"]
            CLICKHOUSE["<b>ClickHouse</b><br/>High-Performance OLAP DB"]
            S3 -- "Loads Curated Data" --> INGEST_OLAP --> CLICKHOUSE
        end
    end

    %% API & Consumers
    subgraph "API & Consumers"
        API["<b>Order Repository API</b><br/>(Python/FastAPI)"]
        API -- "Hot Queries (last 2 years)" --> ES
        API -- "Cold Queries (> 2 years)" --> PRESTO
    end

    %% End Users
    subgraph "End Users"
        direction TB
        CRM["CRM"] --> API
        OMS["OMS"] --> API
        SERVICES["Outher Services"] --> API
        ANALYSTS["BI Developer"] --> PRESTO
        ANALYSTS["BI Developer"] --> CLICKHOUSE
    end
```