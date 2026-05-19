-- ============================================
-- RESET USERS (KEEP ADMIN ONLY)
-- This will delete all non-admin users
-- ============================================

-- Delete all users except admin
DELETE FROM users WHERE username != 'admin';

-- Reset sequence (start from 2 because admin is id=1)
SELECT setval('users_id_seq', 1, false);

-- Verify remaining users
SELECT id, username, role FROM users ORDER BY id;

-- Success message
SELECT '✅ All non-admin users deleted successfully! Admin preserved.' as status;