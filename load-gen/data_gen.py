"""
Льём «залповый» трафик в ecommerce.orders / order_items.
По-умолчанию 30 секунд ≈ 30 000-60 000 заказов (зависит от BATCH).
Все параметры можно переопределить через env.
"""
import os, random, time
from datetime import datetime
from decimal import Decimal

import psycopg2
from faker import Faker

fake = Faker()

# ───── параметры через env ───────────────────────────────────────────────
SECONDS  = int(os.getenv("DURATION", 30))      # сколько секунд льём
BATCH    = int(os.getenv("BATCH", 1_000))      # заказов в одной транзакции
START_ID = int(os.getenv("ORDER_ID_START", 1_000_000))
DSN      = os.getenv(
    "PG_DSN",
    "dbname=ecommerce host=postgres user=app password=app",  # ↔ docker-compose
)

# ───── SQL ───────────────────────────────────────────────────────────────
ORDER_SQL = """
INSERT INTO orders(id, user_id, amount, created_at)
VALUES (%s, %s, %s, %s);
"""
ITEM_SQL = """
INSERT INTO order_items(order_id, sku, qty)
VALUES (%s, %s, %s);
"""


def main() -> None:
    conn = psycopg2.connect(DSN)
    cur  = conn.cursor()

    next_order_id = START_ID
    deadline      = time.time() + SECONDS

    while time.time() < deadline:
        for _ in range(BATCH):
            amount = round(random.uniform(10, 500), 2)
            cur.execute(
                ORDER_SQL,
                (
                    next_order_id,
                    random.randint(1, 10_000),           # user_id
                    Decimal(str(amount)),
                    datetime.utcnow(),
                ),
            )

            for _ in range(random.randint(1, 3)):         # 1-3 позиций в заказе
                cur.execute(
                    ITEM_SQL,
                    (
                        next_order_id,
                        fake.bothify("SKU-???").upper(),
                        random.randint(1, 5),
                    ),
                )
            next_order_id += 1

        conn.commit()                                     # одна «большая» транзакция

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
