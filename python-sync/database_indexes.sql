-- Performance optimization indexes for TallyPrime inventory system
-- Run these in your Supabase SQL editor for better query performance with 5000+ items

-- Indexes for items table
CREATE INDEX IF NOT EXISTS idx_items_item_code ON items(item_code);
CREATE INDEX IF NOT EXISTS idx_items_item_name ON items(item_name);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
CREATE INDEX IF NOT EXISTS idx_items_updated_at ON items(updated_at);

-- Composite index for common search patterns
CREATE INDEX IF NOT EXISTS idx_items_name_category ON items(item_name, category);
CREATE INDEX IF NOT EXISTS idx_items_code_name ON items(item_code, item_name);

-- Indexes for stock_levels table
CREATE INDEX IF NOT EXISTS idx_stock_levels_item_id ON stock_levels(item_id);
CREATE INDEX IF NOT EXISTS idx_stock_levels_current_stock ON stock_levels(current_stock);
CREATE INDEX IF NOT EXISTS idx_stock_levels_last_sync ON stock_levels(last_sync);

-- Composite index for stock queries
CREATE INDEX IF NOT EXISTS idx_stock_levels_item_stock ON stock_levels(item_id, current_stock);

-- Indexes for sync_logs table
CREATE INDEX IF NOT EXISTS idx_sync_logs_timestamp ON sync_logs(sync_timestamp);
CREATE INDEX IF NOT EXISTS idx_sync_logs_status ON sync_logs(status);

-- Full-text search index for item names (PostgreSQL specific)
CREATE INDEX IF NOT EXISTS idx_items_name_fulltext ON items USING gin(to_tsvector('english', item_name));
CREATE INDEX IF NOT EXISTS idx_items_code_fulltext ON items USING gin(to_tsvector('english', item_code));

-- Partial indexes for common filters
CREATE INDEX IF NOT EXISTS idx_items_low_stock ON stock_levels(item_id, current_stock) WHERE current_stock <= 5;
CREATE INDEX IF NOT EXISTS idx_items_zero_stock ON stock_levels(item_id) WHERE current_stock = 0;

-- Index for recent syncs
CREATE INDEX IF NOT EXISTS idx_stock_levels_recent_sync ON stock_levels(last_sync) WHERE last_sync >= (NOW() - INTERVAL '7 days');

-- Performance statistics
-- Run this to see index usage after deployment:
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
-- FROM pg_stat_user_indexes 
-- WHERE schemaname = 'public' 
-- ORDER BY idx_scan DESC;
