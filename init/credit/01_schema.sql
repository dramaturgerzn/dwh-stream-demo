CREATE TABLE loan(
  id SERIAL PRIMARY KEY,
  borrower_id INTEGER,
  principal NUMERIC,
  issued_at DATE
);
CREATE TABLE payment(
  id SERIAL PRIMARY KEY,
  loan_id INTEGER,
  amount NUMERIC,
  paid_at TIMESTAMP DEFAULT now()
);

CREATE PUBLICATION credit_pub FOR ALL TABLES;