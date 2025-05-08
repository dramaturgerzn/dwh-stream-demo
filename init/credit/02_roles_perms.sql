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
GRANT CONNECT, CREATE        ON DATABASE credit TO stream;   -- войти и создавать publication
GRANT USAGE                  ON SCHEMA  public   TO stream;     -- видеть объекты схемы
GRANT SELECT                 ON ALL TABLES IN SCHEMA public TO stream;         -- читать все таблицы
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO stream;                        -- и все будущие таблицы