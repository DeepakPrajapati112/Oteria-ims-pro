-- ============================================
-- RESET ONLY TRANSACTIONS TABLE
-- This will delete all transaction history
-- ============================================

-- Delete all transactions
DELETE FROM transactions;

-- Reset the sequence counter
ALTER SEQUENCE transactions_id_seq RESTART WITH 1;

-- Verify deletion
SELECT COUNT(*) as remaining_transactions FROM transactions;

-- Success message
SELECT '✅ All transactions deleted successfully!' as status;