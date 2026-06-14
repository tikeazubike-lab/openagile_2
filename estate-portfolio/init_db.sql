---
-- Estate Portfolio Database Schema

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Registrars Table
CREATE TABLE IF NOT EXISTS registrars (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    website VARCHAR(255),
    response_rating INTEGER CHECK (response_rating >= 1 AND response_rating <= 5),
    status VARCHAR(20) DEFAULT 'active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Companies Table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    sector VARCHAR(100),
    isin VARCHAR(12),
    status VARCHAR(20) NOT NULL DEFAULT 'listed',
    market_cap DECIMAL(20, 2),
    outstanding_shares BIGINT,
    date_listed DATE,
    date_delisted DATE,
    registrar_id INTEGER REFERENCES registrars(id),
    current_price DECIMAL(10, 2),
    last_price_update TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    CONSTRAINT chk_status CHECK (status IN ('listed', 'merged', 'defunct', 'delisted'))
);

CREATE INDEX idx_companies_ticker ON companies(ticker);
CREATE INDEX idx_companies_status ON companies(status);
CREATE INDEX idx_companies_registrar ON companies(registrar_id);

-- Holdings Table
CREATE TABLE IF NOT EXISTS holdings (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    num_shares DECIMAL(15, 4) NOT NULL,
    average_cost_basis DECIMAL(10, 2) NOT NULL,
    total_cost DECIMAL(20, 2) NOT NULL,
    current_value DECIMAL(20, 2),
    unrealized_gain_loss DECIMAL(20, 2),
    certificate_number VARCHAR(100),
    allocation_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

CREATE INDEX idx_holdings_company ON holdings(company_id);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    holding_id INTEGER REFERENCES holdings(id),
    company_id INTEGER NOT NULL REFERENCES companies(id),
    transaction_type VARCHAR(20) NOT NULL,
    transaction_date DATE NOT NULL,
    settlement_date DATE,
    num_shares DECIMAL(15, 4),
    price_per_share DECIMAL(10, 2),
    gross_amount DECIMAL(20, 2),
    fees DECIMAL(10, 2) DEFAULT 0,
    net_amount DECIMAL(20, 2),
    broker VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    CONSTRAINT chk_transaction_type CHECK (transaction_type IN ('buy', 'sell', 'dividend', 'stock_split', 'bonus_issue', 'rights_issue'))
);

CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_company ON transactions(company_id);

-- Dividends Table
CREATE TABLE IF NOT EXISTS dividends (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    transaction_id INTEGER REFERENCES transactions(id),
    declaration_date DATE,
    ex_dividend_date DATE,
    payment_date DATE,
    amount_per_share DECIMAL(10, 4) NOT NULL,
    shares_held DECIMAL(15, 4),
    gross_amount DECIMAL(20, 2),
    tax_withheld DECIMAL(20, 2),
    net_amount DECIMAL(20, 2),
    payment_method VARCHAR(50),
    status VARCHAR(20) DEFAULT 'declared',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    CONSTRAINT chk_dividend_status CHECK (status IN ('declared', 'pending', 'paid', 'cancelled'))
);

CREATE INDEX idx_dividends_company ON dividends(company_id);
CREATE INDEX idx_dividends_payment_date ON dividends(payment_date);

-- Price History Table
CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    price_date DATE NOT NULL,
    open_price DECIMAL(10, 2),
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    close_price DECIMAL(10, 2) NOT NULL,
    volume BIGINT,
    source VARCHAR(50) DEFAULT 'ngx_scraper',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, price_date)
);

CREATE INDEX idx_price_history_company_date ON price_history(company_id, price_date DESC);

-- Communication Logs Table
CREATE TABLE IF NOT EXISTS communication_logs (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20) NOT NULL,
    entity_id INTEGER,
    communication_type VARCHAR(20) NOT NULL,
    contact_person VARCHAR(255),
    communication_date DATE NOT NULL,
    summary TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(10) DEFAULT 'medium',
    follow_up_date DATE,
    next_action TEXT,
    tags TEXT[],
    attachments JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    CONSTRAINT chk_entity_type CHECK (entity_type IN ('registrar', 'company', 'sec', 'ngx', 'other')),
    CONSTRAINT chk_comm_type CHECK (communication_type IN ('email', 'phone', 'in_person', 'letter')),
    CONSTRAINT chk_comm_status CHECK (status IN ('open', 'pending', 'resolved', 'escalated')),
    CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high'))
);

CREATE INDEX idx_comms_entity ON communication_logs(entity_type, entity_id);
CREATE INDEX idx_comms_date ON communication_logs(communication_date);
CREATE INDEX idx_comms_status ON communication_logs(status);

-- Audit Log Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id INTEGER NOT NULL,
    action VARCHAR(10) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(50) DEFAULT 'admin'
);

CREATE INDEX idx_audit_table_record ON audit_logs(table_name, record_id);

-- Views for Reporting
CREATE VIEW portfolio_summary AS
SELECT 
    c.ticker,
    c.name,
    c.sector,
    c.status,
    h.num_shares,
    h.average_cost_basis,
    h.total_cost,
    c.current_price,
    (h.num_shares * COALESCE(c.current_price, 0)) AS current_value,
    ((h.num_shares * COALESCE(c.current_price, 0)) - h.total_cost) AS unrealized_gain_loss,
    (((h.num_shares * COALESCE(c.current_price, 0)) - h.total_cost) / NULLIF(h.total_cost, 0) * 100) AS return_pct
FROM holdings h
JOIN companies c ON h.company_id = c.id
WHERE h.deleted_at IS NULL AND c.deleted_at IS NULL;

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_holdings_updated_at BEFORE UPDATE ON holdings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_registrars_updated_at BEFORE UPDATE ON registrars
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample registrars
INSERT INTO registrars (name, email, phone, status) VALUES
('Unity Registrars', 'info@unityregistrars.com', '+234-1-234-5678', 'active'),
('Meristem Registrars', 'registrar@meristem.com.ng', '+234-1-345-6789', 'active'),
('GTI Registrars', 'info@gtiregistrars.com', '+234-1-456-7890', 'active');
