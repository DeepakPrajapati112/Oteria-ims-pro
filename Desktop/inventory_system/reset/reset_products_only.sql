-- ============================================
-- RESET ONLY PRODUCTS TABLE
-- WARNING: This will also delete related inventory and orders (foreign keys)
-- ============================================

-- First delete dependent records
DELETE FROM sales_orders WHERE inventory_id IN (SELECT id FROM inventory);
DELETE FROM inventory;
DELETE FROM products;

-- Reset sequences
ALTER SEQUENCE products_id_seq RESTART WITH 1;
ALTER SEQUENCE inventory_id_seq RESTART WITH 1;
ALTER SEQUENCE sales_orders_id_seq RESTART WITH 1;

-- Verify deletion
SELECT COUNT(*) as remaining_products FROM products;

-- Success message
SELECT '✅ All products deleted successfully!' as status;