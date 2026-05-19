-- ============================================
-- RESET ONLY ORDERS TABLE
-- This will delete all sales orders but keep products and inventory
-- ============================================

-- Delete all orders
DELETE FROM sales_orders;

-- Reset the sequence counter
ALTER SEQUENCE sales_orders_id_seq RESTART WITH 1;

-- Verify deletion
SELECT COUNT(*) as remaining_orders FROM sales_orders;

-- Success message
SELECT '✅ All orders deleted successfully!' as status;