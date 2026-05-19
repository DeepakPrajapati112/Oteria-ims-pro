-- ============================================
-- RESET ONLY INVENTORY TABLE
-- This will delete all stock records but keep products
-- ============================================

-- Delete all inventory records
DELETE FROM inventory;

-- Reset the sequence counter
ALTER SEQUENCE inventory_id_seq RESTART WITH 1;

-- Verify deletion
SELECT COUNT(*) as remaining_stock FROM inventory;

-- Success message
SELECT '✅ All inventory records deleted successfully!' as status;