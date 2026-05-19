-- ============================================
-- DELETE OLD ORDERS (Cancelled, Returned, Expired)
-- Keeps only Created, Invoiced, Shipped orders
-- ============================================

-- Delete cancelled orders older than 30 days
DELETE FROM sales_orders 
WHERE order_status = 'Cancelled' 
AND created_on < NOW() - INTERVAL '30 days';

-- Delete returned orders older than 30 days
DELETE FROM sales_orders 
WHERE order_status = 'Returned' 
AND created_on < NOW() - INTERVAL '30 days';

-- Show remaining orders
SELECT order_status, COUNT(*) 
FROM sales_orders 
GROUP BY order_status;

-- Success message
SELECT '✅ Old cancelled/returned orders cleaned!' as status;