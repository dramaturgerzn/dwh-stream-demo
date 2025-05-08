CREATE TABLE orders(
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  amount NUMERIC,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE order_items(
  id SERIAL PRIMARY KEY,
  order_id INTEGER,
  sku TEXT,
  qty INTEGER
);

CREATE PUBLICATION ecommerce_pub FOR ALL TABLES;

INSERT INTO orders(user_id,amount) VALUES
 (1, 100.50),(2,55.30);

INSERT INTO order_items(order_id,sku,qty) VALUES
 (1,'SKU-AAA',2),(1,'SKU-BBB',1),(2,'SKU-CCC',4);
