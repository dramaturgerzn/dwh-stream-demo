"""
Генерирует «залповый» поток заказов + позиций.
Идентификаторы берутся из штатных секвенсов → дубликатов не будет,
даже при повторных запусках генератора.
"""

import os, random, time
from datetime import datetime
from decimal import Decimal

import psycopg2
from faker import Faker

fake = Faker()

# ─────────────── параметры ───────────────────────────────────────────────
SECONDS  = int(os.getenv("DURATION", 30))        # сколько секунд льём
BATCH    = int(os.getenv("BATCH", 1_000))        # заказов в одной транзакции
DSN      = os.getenv(                             # см. docker-compose.yml
    "PG_DSN",
    "dbname=ecommerce host=ecommerce-db port=5432 "
    "user=loadgen password=loadgen",
)

# ─────────────── SQL ─────────────────────────────────────────────────────
ORDER_SQL = """
INSERT INTO orders (user_id, amount, created_at)
VALUES      (%s     , %s    , %s)
RETURNING id;                       -- ← получаем id, который сгенерировал sequence
"""
ITEM_SQL = """
INSERT INTO order_items (order_id, sku, qty)
VALUES                   (%s      , %s , %s);
"""

# ─────────────── генерация ───────────────────────────────────────────────
def main() -> None:
    conn = psycopg2.connect(DSN)
    cur  = conn.cursor()
    deadline = time.time() + SECONDS

    while time.time() < deadline:
        for _ in range(BATCH):
            # 1. заказ ----------------------------------------------------
            amount   = round(random.uniform(10, 500), 2)
            cur.execute(
                ORDER_SQL,
                (
                    random.randint(1, 10_000),         # user_id
                    Decimal(str(amount)),
                    datetime.utcnow(),
                ),
            )
            order_id: int = cur.fetchone()[0]          # id из секвенса

            # 2. 1-3 позиций заказа ---------------------------------------
            for _ in range(random.randint(1, 3)):
                cur.execute(
                    ITEM_SQL,
                    (
                        order_id,
                        fake.bothify("SKU-???").upper(),
                        random.randint(1, 5),
                    ),
                )

        conn.commit()                                  # одна «большая» транзакция

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
