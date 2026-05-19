-- ============================================
-- COMPLETE DATABASE RESET
-- WARNING: This will delete ALL data from all tables
-- ============================================

-- Disable foreign key checks temporarily
SET session_replication_role = 'replica';

-- Drop all tables in correct order
DROP TABLE IF EXISTS sales_orders CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Re-enable foreign key checks
SET session_replication_role = 'origin';

-- Verify all tables are dropped
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Success message
SELECT '✅ All tables dropped successfully!' as status;