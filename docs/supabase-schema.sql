-- TallyPrime Clean Slate Inventory System
-- Supabase PostgreSQL Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Items master table
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_code VARCHAR(100) UNIQUE NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) DEFAULT 'General',
    unit VARCHAR(50) DEFAULT 'Nos',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Current stock truth table
CREATE TABLE stock_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID REFERENCES items(id) ON DELETE CASCADE,
    current_stock DECIMAL(15,3) DEFAULT 0,
    physical_baseline DECIMAL(15,3) DEFAULT 0,
    tally_delta DECIMAL(15,3) DEFAULT 0,
    last_sync TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sync_source VARCHAR(50) DEFAULT 'manual',
    UNIQUE(item_id)
);

-- Sync operation logs
CREATE TABLE sync_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sync_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    items_processed INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL CHECK (status IN ('SUCCESS', 'FAILED', 'ERROR')),
    error_message TEXT,
    duration_seconds INTEGER
);

-- Indexes for performance
CREATE INDEX idx_items_item_code ON items(item_code);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_stock_levels_item_id ON stock_levels(item_id);
CREATE INDEX idx_stock_levels_last_sync ON stock_levels(last_sync);
CREATE INDEX idx_sync_logs_timestamp ON sync_logs(sync_timestamp);
CREATE INDEX idx_sync_logs_status ON sync_logs(status);

-- Row Level Security (RLS) policies
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_levels ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_logs ENABLE ROW LEVEL SECURITY;

-- Policy to allow read access for authenticated users
CREATE POLICY "Allow read access for authenticated users" ON items
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow read access for authenticated users" ON stock_levels
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Allow read access for authenticated users" ON sync_logs
    FOR SELECT USING (auth.role() = 'authenticated');

-- Policy to allow insert/update for service role (Python script)
CREATE POLICY "Allow full access for service role" ON items
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow full access for service role" ON stock_levels
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Allow full access for service role" ON sync_logs
    FOR ALL USING (auth.role() = 'service_role');

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_items_updated_at 
    BEFORE UPDATE ON items 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- View for mobile app consumption
CREATE VIEW inventory_view AS
SELECT 
    i.id,
    i.item_code,
    i.item_name,
    i.category,
    i.unit,
    COALESCE(sl.current_stock, 0) as current_stock,
    COALESCE(sl.physical_baseline, 0) as physical_baseline,
    COALESCE(sl.tally_delta, 0) as tally_delta,
    COALESCE(sl.last_sync, i.created_at) as last_sync,
    COALESCE(sl.sync_source, 'manual') as sync_source
FROM items i
LEFT JOIN stock_levels sl ON i.id = sl.item_id
ORDER BY i.item_name;

-- Grant permissions on the view
GRANT SELECT ON inventory_view TO authenticated;
GRANT SELECT ON inventory_view TO anon;

-- Function to get latest sync timestamp
CREATE OR REPLACE FUNCTION get_latest_sync_timestamp()
RETURNS TIMESTAMP WITH TIME ZONE AS $$
BEGIN
    RETURN (
        SELECT MAX(last_sync) 
        FROM stock_levels 
        WHERE sync_source = 'tally_sync'
    );
END;
$$ LANGUAGE plpgsql;

-- Sample data for testing (remove in production)
INSERT INTO items (item_code, item_name, category, unit) VALUES
    ('BRAKE001', 'Brake Pads Front', 'Brakes', 'Set'),
    ('BRAKE002', 'Brake Pads Rear', 'Brakes', 'Set'),
    ('OIL001', 'Engine Oil 5W30', 'Lubricants', 'Liter'),
    ('FILTER001', 'Air Filter', 'Filters', 'Piece'),
    ('SPARK001', 'Spark Plugs', 'Ignition', 'Set');

INSERT INTO stock_levels (item_id, current_stock, physical_baseline, tally_delta, sync_source)
SELECT 
    i.id,
    CASE 
        WHEN i.item_code = 'BRAKE001' THEN 25
        WHEN i.item_code = 'BRAKE002' THEN 18
        WHEN i.item_code = 'OIL001' THEN 42
        WHEN i.item_code = 'FILTER001' THEN 15
        WHEN i.item_code = 'SPARK001' THEN 30
    END,
    CASE 
        WHEN i.item_code = 'BRAKE001' THEN 25
        WHEN i.item_code = 'BRAKE002' THEN 18
        WHEN i.item_code = 'OIL001' THEN 42
        WHEN i.item_code = 'FILTER001' THEN 15
        WHEN i.item_code = 'SPARK001' THEN 30
    END,
    0,
    'manual'
FROM items i;
