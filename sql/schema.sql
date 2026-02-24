-- PostgreSQL reference schema based on docs/系统架构设计.md

CREATE TABLE IF NOT EXISTS import_batch (
  id BIGSERIAL PRIMARY KEY,
  source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('statement', 'inbound')),
  file_name TEXT NOT NULL,
  uploaded_by VARCHAR(64),
  uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
  parse_status VARCHAR(20) NOT NULL DEFAULT 'pending',
  parse_error TEXT
);

CREATE TABLE IF NOT EXISTS raw_row (
  id BIGSERIAL PRIMARY KEY,
  batch_id BIGINT NOT NULL REFERENCES import_batch(id),
  source_type VARCHAR(20) NOT NULL,
  row_no INT NOT NULL,
  raw_json JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(batch_id, row_no)
);

CREATE TABLE IF NOT EXISTS normalized_row (
  id BIGSERIAL PRIMARY KEY,
  batch_id BIGINT NOT NULL REFERENCES import_batch(id),
  raw_row_id BIGINT NOT NULL REFERENCES raw_row(id),
  source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('statement', 'inbound')),
  biz_date DATE,
  order_ref VARCHAR(100),
  item_model VARCHAR(100),
  item_name VARCHAR(255),
  qty NUMERIC(18,4),
  amount_tax_incl NUMERIC(18,2),
  counterparty_name VARCHAR(255),
  normalized_order_ref VARCHAR(100),
  normalized_item_model VARCHAR(100),
  match_key VARCHAR(220),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS purchase_item (
  id BIGSERIAL PRIMARY KEY,
  order_ref VARCHAR(100),
  item_model VARCHAR(100),
  item_name VARCHAR(255),
  qty NUMERIC(18,4),
  amount_tax_incl NUMERIC(18,2),
  reconciliation_status VARCHAR(20) NOT NULL,
  invoice_status VARCHAR(20) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_norm_source_key ON normalized_row(source_type, match_key);
