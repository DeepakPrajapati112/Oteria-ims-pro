-- ============================================
-- RESET WITH BACKUP - Creates backup tables before reset
-- ============================================

-- Create backup tables with timestamp
DO $$
DECLARE
    backup_suffix TEXT;
BEGIN
    backup_suffix := to_char(now(), 'YYYYMMDD_HH24MISS');
    
    -- Backup sales_orders
    EXECUTE 'CREATE TABLE sales_orders_backup_' || backup_suffix || ' AS SELECT * FROM sales_orders';
    
    -- Backup inventory
    EXECUTE 'CREATE TABLE inventory_backup_' || backup_suffix || ' AS SELECT * FROM inventory';
    
    -- Backup products
    EXECUTE 'CREATE TABLE products_backup_' || backup_suffix || ' AS SELECT * FROM products';
    
    -- Backup users
    EXECUTE 'CREATE TABLE users_backup_' || backup_suffix || ' AS SELECT * FROM users';
    
    -- Backup transactions
    EXECUTE 'CREATE TABLE transactions_backup_' || backup_suffix || ' AS SELECT * FROM transactions';
    
    RAISE NOTICE '✅ Backups created with suffix: %', backup_suffix;
END $$;

-- Now reset all tables
DELETE FROM sales_orders;
DELETE FROM inventory;
DELETE FROM products;
DELETE FROM transactions;
DELETE FROM users WHERE username != 'admin';

-- Reset sequences
ALTER SEQUENCE sales_orders_id_seq RESTART WITH 1;
ALTER SEQUENCE inventory_id_seq RESTART WITH 1;
ALTER SEQUENCE products_id_seq RESTART WITH 1;
ALTER SEQUENCE transactions_id_seq RESTART WITH 1;

-- Show backup tables list
SELECT tablename 
FROM pg_tables 
WHERE tablename LIKE '%_backup_%' 
ORDER BY tablename DESC;

-- Success message
SELECT '✅ Database reset complete! Backups created.' as status;