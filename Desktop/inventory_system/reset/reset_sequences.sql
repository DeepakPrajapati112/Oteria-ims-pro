-- ============================================
-- RESET ALL SEQUENCES
-- Use this if IDs are not starting from 1
-- ============================================

-- Reset all sequences to start from 1
ALTER SEQUENCE users_id_seq RESTART WITH 1;
ALTER SEQUENCE products_id_seq RESTART WITH 1;
ALTER SEQUENCE inventory_id_seq RESTART WITH 1;
ALTER SEQUENCE sales_orders_id_seq RESTART WITH 1;
ALTER SEQUENCE transactions_id_seq RESTART WITH 1;

-- Show current sequence values
SELECT 
    'users' as table_name, currval('users_id_seq') as current_value
UNION ALL
SELECT 'products', currval('products_id_seq')
UNION ALL
SELECT 'inventory', currval('inventory_id_seq')
UNION ALL
SELECT 'sales_orders', currval('sales_orders_id_seq')
UNION ALL
SELECT 'transactions', currval('transactions_id_seq');

-- Success message
SELECT '✅ All sequences reset to start from 1!' as status;