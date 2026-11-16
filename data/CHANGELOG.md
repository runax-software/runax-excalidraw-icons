# Changelog

All notable changes to the Data pack (`runax-data.excalidrawlib`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
This pack is released on its own, tagged `data/vX.Y.Z`.

## [Unreleased]

## [0.1.0] - 2026-11-16

### Added

- 43 icons: databases (PostgreSQL, MySQL, MariaDB, Oracle, SQLite, MongoDB, Redis, Valkey, Cassandra, CouchDB, ClickHouse, DuckDB, CockroachDB, Snowflake, Neo4j), messaging and streaming (Kafka, Pulsar, RabbitMQ, NATS, MQTT, ActiveMQ, BullMQ, Flink, Spark), search (Elasticsearch, OpenSearch, Kibana, Qdrant), query engines and formats (DataFusion, Arrow, Parquet, Trino, Polars), lakehouse and pipelines (Iceberg, Delta Lake, Polaris, Airbyte, SeaTunnel, NiFi, dbt, Airflow, Temporal) and Firebase.
- Logos from openly licensed sources: gilbarbara/logos and simple-icons (CC0) where the project doesn't publish its own. Microsoft's Cosmos DB and SQL Server are in the azure pack.
- Logos as their projects publish them: NiFi's drop mark, DuckDB's design-manual icon, the official MQTT and BullMQ logos, and the simple-icons marks of CockroachDB and Neo4j in their brand colors.
- Captions follow vendor naming: at most two lines, small words lowercase.
- `runax-data-native.excalidrawlib`: the icons drawn with Excalidraw shapes, which work in Excalidraw's library panel on their own (it drops a library's images on import) and take arrows like any shape; Apache Iceberg, Apache SeaTunnel and BullMQ are images, so they're left out.
