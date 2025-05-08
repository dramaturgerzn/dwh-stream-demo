"""
dwh_etl.py
Faust-сервис: читаем Debezium-топики и сохраняем «сырые» события в ClickHouse
(дополнено расширенным логированием).
"""
import json
import os
import logging          # ➊ добавили
from typing import Any, Dict, Iterable

import faust
from clickhouse_driver import Client, errors as ch_errors

# ───────────────────────────── Логирование ───────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
# Faust сам создаст app.logger, но мы хотим единый формат
logger = logging.getLogger("dwh_etl")

# ───────────────────────────── Kafka / Faust ─────────────────────────────
APP_ID: str = "dwh_etl"
KAFKA_BROKER: str = os.getenv("KAFKA_URL", "kafka://kafka:9092")

app = faust.App(
    id=APP_ID,
    broker=KAFKA_BROKER,
    store="memory://",
    topic_partitions=1,
)

# Debezium-топики ----------------------------------------------------------
TOPIC_NAMES: Iterable[str] = [
    "ecommerce.public.orders",
    "ecommerce.public.order_items",
    "insurance.public.policy",
    "insurance.public.claim",
    "credit.public.loan",
    "credit.public.payment",
]
events_topic: faust.Topic[bytes] = app.topic(*TOPIC_NAMES, value_type=bytes)

# ───────────────────────────── ClickHouse ────────────────────────────────
ch = Client(
    host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
    database=os.getenv("CLICKHOUSE_DB", "default"),
    user=os.getenv("CLICKHOUSE_USER", "default"),
    password=os.getenv("CLICKHOUSE_PASSWORD", ""),
)

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS raw_events
(
    service String,
    table   String,
    op      LowCardinality(String),
    payload String,
    ts      DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY ts
"""
INSERT_SQL = "INSERT INTO raw_events (service, table, op, payload) VALUES"

ch.execute(CREATE_SQL)

# ───────────────────────────── Faust agent ───────────────────────────────
@app.agent(events_topic)
async def sink_to_dwh(stream: faust.Stream[bytes]) -> None:
    async for event in stream:
        # 1️⃣ tombstone?
        if event is None:
            logger.debug("Tombstone message - skip")
            continue

        payload: Dict[str, Any] = event.get("payload", event)
        source = payload.get("source")
        if not source:
            logger.warning("No 'source' field, skip")
            continue

        service = source["db"]
        table   = source["table"]
        op      = payload.get("op") or "unknown"

        # 3️⃣ Детальное логирование перед вставкой
        logger.info(
            "Kafka → CH | %s.%s | op=%s | snapshot=%s | lsn=%s",
            service,
            table,
            op,
            source.get("snapshot"),
            source.get("lsn"),
        )
        logger.debug("Full payload: %s", payload)

        # 4️⃣ Пишем в ClickHouse
        try:
            ch.execute(INSERT_SQL, [(service, table, op, json.dumps(payload))])
        except ch_errors.Error as exc:
            logger.error("ClickHouse error: %s", exc)

# ───────────────────────────── Entrypoint ────────────────────────────────
if __name__ == "__main__":
    app.main()
