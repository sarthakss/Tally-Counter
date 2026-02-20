-- TEST VERSION - Run this first to verify your database setup
-- This will show you what tables exist and help debug any issues

-- Step 1: Check what tables exist in your database
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Step 2: Check columns in items table (if it exists)
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'items' 
    AND table_schema = 'public'
ORDER BY ordinal_position;

-- Step 3: Check columns in stock_levels table (if it exists)
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'stock_levels' 
    AND table_schema = 'public'
ORDER BY ordinal_position;

-- Step 4: Check existing indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;
