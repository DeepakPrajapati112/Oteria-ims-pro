-- ============================================
-- CHECK DATABASE STATUS
-- Shows record counts for all tables
-- ============================================

-- Count records in each table
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'inventory', COUNT(*) FROM inventory
UNION ALL
SELECT 'sales_orders', COUNT(*) FROM sales_orders
UNION ALL
SELECT 'transactions', COUNT(*) FROM transactions
ORDER BY table_name;

-- Show table sizes
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size('"' || table_name || '"')) as table_size
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Success message
SELECT '✅ Database status check complete!' as status;