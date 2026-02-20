-- Performance optimization indexes for TallyPrime inventory system
-- TESTED VERSION - Safe to run in Supabase SQL editor
-- Includes table existence checks and proper error handling

-- Step 1: Check if tables exist before creating indexes
DO $$
BEGIN
    -- Only create indexes if tables exist
    
    -- ITEMS TABLE INDEXES
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'items') THEN
        -- Basic indexes for items table
        CREATE INDEX IF NOT EXISTS idx_items_item_code ON items(item_code);
        CREATE INDEX IF NOT EXISTS idx_items_item_name ON items(item_name);
        CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
        
        -- Only create updated_at index if column exists
        IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'items' AND column_name = 'updated_at') THEN
            CREATE INDEX IF NOT EXISTS idx_items_updated_at ON items(updated_at);
        END IF;
        
        -- Composite indexes for search patterns
        CREATE INDEX IF NOT EXISTS idx_items_name_category ON items(item_name, category);
        CREATE INDEX IF NOT EXISTS idx_items_code_name ON items(item_code, item_name);
        
        RAISE NOTICE 'Created indexes for items table';
    ELSE
        RAISE NOTICE 'Table "items" does not exist - skipping items indexes';
    END IF;
    
    -- STOCK_LEVELS TABLE INDEXES
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'stock_levels') THEN
        -- Basic indexes for stock_levels table
        CREATE INDEX IF NOT EXISTS idx_stock_levels_item_id ON stock_levels(item_id);
        CREATE INDEX IF NOT EXISTS idx_stock_levels_current_stock ON stock_levels(current_stock);
        
        -- Only create last_sync index if column exists
        IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'stock_levels' AND column_name = 'last_sync') THEN
            CREATE INDEX IF NOT EXISTS idx_stock_levels_last_sync ON stock_levels(last_sync DESC);
        END IF;
        
        -- Composite index for stock queries
        CREATE INDEX IF NOT EXISTS idx_stock_levels_item_stock ON stock_levels(item_id, current_stock);
        
        -- Partial indexes for common filters
        CREATE INDEX IF NOT EXISTS idx_stock_low_stock ON stock_levels(item_id, current_stock) WHERE current_stock <= 5;
        CREATE INDEX IF NOT EXISTS idx_stock_zero_stock ON stock_levels(item_id) WHERE current_stock = 0;
        CREATE INDEX IF NOT EXISTS idx_stock_negative ON stock_levels(item_id) WHERE current_stock < 0;
        
        RAISE NOTICE 'Created indexes for stock_levels table';
    ELSE
        RAISE NOTICE 'Table "stock_levels" does not exist - skipping stock_levels indexes';
    END IF;
    
    -- SYNC_LOGS TABLE INDEXES (Optional)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sync_logs') THEN
        IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'sync_logs' AND column_name = 'sync_timestamp') THEN
            CREATE INDEX IF NOT EXISTS idx_sync_logs_timestamp ON sync_logs(sync_timestamp);
        END IF;
        
        IF EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'sync_logs' AND column_name = 'status') THEN
            CREATE INDEX IF NOT EXISTS idx_sync_logs_status ON sync_logs(status);
        END IF;
        
        RAISE NOTICE 'Created indexes for sync_logs table';
    ELSE
        RAISE NOTICE 'Table "sync_logs" does not exist - skipping sync_logs indexes';
    END IF;
    
END $$;

-- Optional: Full-text search indexes (only add if you need advanced text search)
-- Uncomment these lines if you want full-text search capabilities:
-- CREATE INDEX IF NOT EXISTS idx_items_name_fulltext ON items USING gin(to_tsvector('english', item_name));
-- CREATE INDEX IF NOT EXISTS idx_items_code_fulltext ON items USING gin(to_tsvector('english', item_code));

-- Performance monitoring query
-- Run this after creating indexes to check their usage:
/*
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    idx_scan as "Times Used",
    idx_tup_read as "Tuples Read",
    idx_tup_fetch as "Tuples Fetched"
FROM pg_stat_user_indexes 
WHERE schemaname = 'public' 
ORDER BY idx_scan DESC;
*/
