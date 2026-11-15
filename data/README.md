# Data

34 icons from database, streaming and data-pipeline logos, packaged as a Miro-style Excalidraw library:
each item is a 64px icon with an editable label below it, grouped together.

<table>
<tr><td align="center" width="120"><img src="src/PostgreSQL.svg" width="64" height="64"><br><sub>PostgreSQL</sub></td><td align="center" width="120"><img src="src/MySQL.svg" width="64" height="64"><br><sub>MySQL</sub></td><td align="center" width="120"><img src="src/Microsoft-SQL-Server.svg" width="64" height="64"><br><sub>Microsoft SQL Server</sub></td><td align="center" width="120"><img src="src/SQLite.svg" width="64" height="64"><br><sub>SQLite</sub></td><td align="center" width="120"><img src="src/ClickHouse.svg" width="64" height="64"><br><sub>ClickHouse</sub></td><td align="center" width="120"><img src="src/DuckDB.svg" width="64" height="64"><br><sub>DuckDB</sub></td></tr>
<tr><td align="center" width="120"><img src="src/CockroachDB.svg" width="64" height="64"><br><sub>CockroachDB</sub></td><td align="center" width="120"><img src="src/Snowflake.svg" width="64" height="64"><br><sub>Snowflake</sub></td><td align="center" width="120"><img src="src/MongoDB.svg" width="64" height="64"><br><sub>MongoDB</sub></td><td align="center" width="120"><img src="src/Redis.svg" width="64" height="64"><br><sub>Redis</sub></td><td align="center" width="120"><img src="src/Valkey.svg" width="64" height="64"><br><sub>Valkey</sub></td><td align="center" width="120"><img src="src/Neo4j.svg" width="64" height="64"><br><sub>Neo4j</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Apache-Kafka.svg" width="64" height="64"><br><sub>Apache Kafka</sub></td><td align="center" width="120"><img src="src/RabbitMQ.svg" width="64" height="64"><br><sub>RabbitMQ</sub></td><td align="center" width="120"><img src="src/NATS.svg" width="64" height="64"><br><sub>NATS</sub></td><td align="center" width="120"><img src="src/MQTT.svg" width="64" height="64"><br><sub>MQTT</sub></td><td align="center" width="120"><img src="src/Apache-ActiveMQ.svg" width="64" height="64"><br><sub>Apache ActiveMQ</sub></td><td align="center" width="120"><img src="src/BullMQ.svg" width="64" height="64"><br><sub>BullMQ</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Apache-Flink.svg" width="64" height="64"><br><sub>Apache Flink</sub></td><td align="center" width="120"><img src="src/Apache-Spark.svg" width="64" height="64"><br><sub>Apache Spark</sub></td><td align="center" width="120"><img src="src/Apache-Airflow.svg" width="64" height="64"><br><sub>Apache Airflow</sub></td><td align="center" width="120"><img src="src/Apache-Iceberg.svg" width="64" height="64"><br><sub>Apache Iceberg</sub></td><td align="center" width="120"><img src="src/Airbyte.svg" width="64" height="64"><br><sub>Airbyte</sub></td><td align="center" width="120"><img src="src/Apache-SeaTunnel.svg" width="64" height="64"><br><sub>Apache SeaTunnel</sub></td></tr>
<tr><td align="center" width="120"><img src="src/dbt.svg" width="64" height="64"><br><sub>dbt</sub></td><td align="center" width="120"><img src="src/Qdrant.svg" width="64" height="64"><br><sub>Qdrant</sub></td><td align="center" width="120"><img src="src/OpenSearch.svg" width="64" height="64"><br><sub>OpenSearch</sub></td></tr>
</table>

27 of 34 shown. Every icon is in [`src/`](src/). Changes are in [`CHANGELOG.md`](CHANGELOG.md).

## License

Logos come from the projects themselves, [gilbarbara/logos](https://github.com/gilbarbara/logos) (CC0-1.0) and [simple-icons](https://github.com/simple-icons/simple-icons) (CC0-1.0). Product names and logos are trademarks of their owners and are used here only to refer to their products; no endorsement is implied.

## Sources

Imports last fetched 2026-11-15. Paths are relative to [`src/`](src/). Imported files are refreshed by
`uv run runax-icons import data`; the rest are kept by hand.

| Files | Source | Notes |
| ----- | ------ | ----- |
| `*.svg` | https://raw.githubusercontent.com/gilbarbara/logos/main/logos/{src}.svg | CC0-1.0; 8 files |
| `ClickHouse.svg` | https://raw.githubusercontent.com/ClickHouse/ClickHouse/master/docker/server/README.src/logo.svg |  |
| `DuckDB.svg` | https://raw.githubusercontent.com/duckdb/duckdb/main/logo/DuckDB_Logo-stacked.svg | mark only; viewBox cropped |
| `Neo4j.svg` | https://raw.githubusercontent.com/neo4j/neo4j-browser/master/src/browser/components/icons/svgs/neo4j-icon.svg |  |
| `Apache-Iceberg.svg` | https://raw.githubusercontent.com/apache/iceberg/main/site/docs/assets/images/iceberg-logo-icon.png | PNG wrapped in SVG |
| `Apache-SeaTunnel.svg` | https://seatunnel.apache.org/image/logo.png | PNG wrapped in SVG |
| `Apache-ActiveMQ.svg` | https://raw.githubusercontent.com/apache/activemq-website/main/src/assets/img/activemq_logo_icon.svg | viewBox cropped |
| `MQTT.svg` | https://raw.githubusercontent.com/mqtt/mqtt.org/master/assets/img/mqtt-ver.svg | mark only; viewBox cropped |
| `CockroachDB.svg` | https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/cockroachlabs.svg | Cockroach Labs brand color; filled #6933FF |
| `BullMQ.svg` | https://user-images.githubusercontent.com/95200/143832033-32e868df-f3b0-4251-97fb-c64809a43d36.png | the bull from the taskforcesh/bullmq README banner, as a 512px PNG on a rounded #00ADEF tile |
| `*` |  | moved from the techno pack (originally from techno's svg.zip); Cosmos-DB, Elasticsearch and PostgreSQL renamed to fix typos |

## Use

Build with `uv run runax-icons build` from the repo root, then in Excalidraw:

1. Open `runax-data.excalidraw` (or paste icons from it into your drawing), so the images are loaded.
2. Import `runax-data.excalidrawlib` from the library panel.

Excalidraw doesn't store images in library files, so library icons render only once the
drawing contains them. See the [main README](../README.md).

<!-- Generated by runax-icons build; edit pack.yml instead. -->
