CREATE TABLE policy(
  id SERIAL PRIMARY KEY,
  customer_id INTEGER,
  premium NUMERIC,
  started_at DATE
);
CREATE TABLE claim(
  id SERIAL PRIMARY KEY,
  policy_id INTEGER,
  payout NUMERIC,
  created_at TIMESTAMP DEFAULT now()
);

CREATE PUBLICATION insurance_pub FOR ALL TABLES;