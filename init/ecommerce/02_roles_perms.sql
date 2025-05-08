DO
$$
BEGIN
   IF NOT EXISTS (
       SELECT 1 FROM pg_roles WHERE rolname = 'stream'
   ) THEN
       CREATE ROLE stream WITH LOGIN PASSWORD 'streaming';
   END IF;

   -- гарантированно существует → можно настраивать
   ALTER ROLE stream WITH REPLICATION;
END
$$;

-- права для Debezium-коннектора
GRANT CONNECT, CREATE        ON DATABASE ecommerce TO stream;   -- войти и создавать publication
GRANT USAGE                  ON SCHEMA  public   TO stream;     -- видеть объекты схемы
GRANT SELECT                 ON ALL TABLES IN SCHEMA public TO stream;         -- читать все таблицы
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO stream;                        -- и все будущие таблицы


DO
$$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_roles WHERE rolname = 'loadgen'
    ) THEN
        CREATE ROLE loadgen            -- login-роль
        WITH LOGIN
        PASSWORD 'loadgen';            -- ↔ docker-compose
    END IF;
END
$$;

-- ─── привилегии ─────────────────────────────────────────────────
GRANT CONNECT              ON DATABASE ecommerce TO loadgen;

GRANT USAGE                ON SCHEMA  public     TO loadgen;

-- писать и при необходимости читать «боевые» таблицы
GRANT INSERT, SELECT       ON TABLE orders, order_items TO loadgen;

-- доступ к последовательностям (SERIAL/IDENTITY)
GRANT USAGE, UPDATE        ON ALL SEQUENCES IN SCHEMA public TO loadgen;

-- выдавать такие же права на ВСЕ будущие таблицы/последовательности
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT INSERT, SELECT   ON TABLES       TO loadgen;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, UPDATE    ON SEQUENCES    TO loadgen;