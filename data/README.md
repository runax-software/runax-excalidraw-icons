# Data

33 icons from database, streaming and data-pipeline logos, packaged as a Miro-style Excalidraw library:
each item is a 64px icon with an editable label below it, grouped together.

<table>
<tr><td align="center" width="120"><img src="src/PostgreSQL.svg" width="62" height="64"><br><sub>PostgreSQL</sub></td><td align="center" width="120"><img src="src/MySQL.svg" width="64" height="63"><br><sub>MySQL</sub></td><td align="center" width="120"><img src="src/SQLite.svg" width="64" height="28"><br><sub>SQLite</sub></td><td align="center" width="120"><img src="src/ClickHouse.svg" width="64" height="64"><br><sub>ClickHouse</sub></td><td align="center" width="120"><img src="src/DuckDB.svg" width="64" height="64"><br><sub>DuckDB</sub></td><td align="center" width="120"><img src="src/CockroachDB.svg" width="64" height="64"><br><sub>CockroachDB</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Snowflake.svg" width="64" height="64"><br><sub>Snowflake</sub></td><td align="center" width="120"><img src="src/MongoDB.svg" width="30" height="64"><br><sub>MongoDB</sub></td><td align="center" width="120"><img src="src/Redis.svg" width="64" height="55"><br><sub>Redis</sub></td><td align="center" width="120"><img src="src/Valkey.svg" width="56" height="64"><br><sub>Valkey</sub></td><td align="center" width="120"><img src="src/Neo4j.svg" width="64" height="64"><br><sub>Neo4j</sub></td><td align="center" width="120"><img src="src/Apache-Kafka.svg" width="40" height="64"><br><sub>Apache Kafka</sub></td></tr>
<tr><td align="center" width="120"><img src="src/RabbitMQ.svg" width="64" height="64"><br><sub>RabbitMQ</sub></td><td align="center" width="120"><img src="src/NATS.svg" width="62" height="64"><br><sub>NATS</sub></td><td align="center" width="120"><img src="src/MQTT.svg" width="64" height="55"><br><sub>MQTT</sub></td><td align="center" width="120"><img src="src/Apache-ActiveMQ.svg" width="44" height="64"><br><sub>Apache ActiveMQ</sub></td><td align="center" width="120"><img src="src/BullMQ.svg" width="64" height="22"><br><sub>BullMQ</sub></td><td align="center" width="120"><img src="src/Apache-Flink.svg" width="63" height="64"><br><sub>Apache Flink</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Apache-Spark.svg" width="64" height="33"><br><sub>Apache Spark</sub></td><td align="center" width="120"><img src="src/Apache-Airflow.svg" width="64" height="64"><br><sub>Apache Airflow</sub></td><td align="center" width="120"><img src="src/Apache-Iceberg.svg" width="64" height="64"><br><sub>Apache Iceberg</sub></td><td align="center" width="120"><img src="src/Airbyte.svg" width="61" height="64"><br><sub>Airbyte</sub></td><td align="center" width="120"><img src="src/Apache-SeaTunnel.svg" width="60" height="64"><br><sub>Apache SeaTunnel</sub></td><td align="center" width="120"><img src="src/dbt.svg" width="64" height="64"><br><sub>dbt</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Qdrant.svg" width="55" height="64"><br><sub>Qdrant</sub></td><td align="center" width="120"><img src="src/OpenSearch.svg" width="64" height="64"><br><sub>OpenSearch</sub></td></tr>
</table>

26 of 33 shown. Every icon is in [`src/`](src/). Changes are in [`CHANGELOG.md`](CHANGELOG.md).

## License

Logos come from the projects themselves, [gilbarbara/logos](https://github.com/gilbarbara/logos) (CC0-1.0) and [simple-icons](https://github.com/simple-icons/simple-icons) (CC0-1.0). Product names and logos are trademarks of their owners and are used here only to refer to their products; no endorsement is implied.

This pack forbids, and the build refuses:

- `native`: redrawing changes the logos' shape; the logos are their owners' trademarks
- `publish`: the logos are their owners' trademarks; we don't republish them as a library of their own

## Sources

Imports last fetched 2026-11-15. Paths are relative to [`src/`](src/). Imported files are refreshed by
`uv run runax-icons import data`; the rest are kept by hand.

| Files | Source | Notes |
| ----- | ------ | ----- |
| `*.svg` | https://raw.githubusercontent.com/gilbarbara/logos/main/logos/{src}.svg | CC0-1.0; 8 files |
| `ClickHouse.svg` | https://raw.githubusercontent.com/ClickHouse/ClickHouse/master/docker/server/README.src/logo.svg |  |
| `DuckDB.svg` | https://raw.githubusercontent.com/duckdb/duckdb-web/main/images/designmanual/DuckDB_icon-lightmode.svg | the icon from DuckDB's design manual |
| `Neo4j.svg` | https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/neo4j.svg | CC0-1.0; Neo4j brand color (the neo4j-browser icon is GPL-3.0); filled #4581C3 |
| `Apache-Iceberg.svg` | https://raw.githubusercontent.com/apache/iceberg/main/site/docs/assets/images/iceberg-logo-icon.png | PNG wrapped in SVG |
| `Apache-SeaTunnel.svg` | https://seatunnel.apache.org/image/logo.png | PNG wrapped in SVG |
| `Apache-ActiveMQ.svg` | https://raw.githubusercontent.com/apache/activemq-website/main/src/assets/img/activemq_logo_icon.svg | viewBox cropped |
| `Apache-NiFi.svg` | https://raw.githubusercontent.com/apache/nifi-site/main/themes/nifi/static/images/apache-nifi-drop-logo.svg | the drop mark from the NiFi website |
| `MQTT.svg` | https://raw.githubusercontent.com/mqtt/mqtt.org/master/assets/img/mqtt-ver.svg | official logo, unmodified (mqtt.org has no symbol-only version) |
| `BullMQ.svg` | https://user-images.githubusercontent.com/95200/143832033-32e868df-f3b0-4251-97fb-c64809a43d36.png | the taskforcesh/bullmq README banner, unmodified (BullMQ has no other logo file) |
| `CockroachDB.svg` | https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/cockroachlabs.svg | Cockroach Labs brand color; filled #6933FF |
| `*.svg` | https://raw.githubusercontent.com/gilbarbara/logos/main/logos/{src}.svg | CC0-1.0; 15 files |

## Use

Build with `uv run runax-icons build` from the repo root, then in Excalidraw:

1. Open `runax-data.excalidraw` (or paste icons from it into your drawing), so the images are loaded.
2. Import `runax-data.excalidrawlib` from the library panel.

Excalidraw doesn't store images in library files, so library icons render only once the
drawing contains them. See the [main README](../README.md).

<!-- Generated by runax-icons build; edit pack.yml instead. -->
