-- MINIMAL INDEXES - Guaranteed to work
-- Run this version if you want just the essential indexes

-- Basic indexes that will work on any table structure
-- Only creates indexes if tables and columns exist

-- Items table - basic indexes
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'items') THEN
        CREATE INDEX IF NOT EXISTS idx_items_item_code ON items(item_code);
        CREATE INDEX IF NOT EXISTS idx_items_item_name ON items(item_name);
        RAISE NOTICE 'Created basic indexes for items table';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Could not create items indexes: %', SQLERRM;
END $$;

-- Stock levels table - basic indexes  
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'stock_levels') THEN
        CREATE INDEX IF NOT EXISTS idx_stock_levels_item_id ON stock_levels(item_id);
        CREATE INDEX IF NOT EXISTS idx_stock_levels_current_stock ON stock_levels(current_stock);
        RAISE NOTICE 'Created basic indexes for stock_levels table';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Could not create stock_levels indexes: %', SQLERRM;
END $$;
