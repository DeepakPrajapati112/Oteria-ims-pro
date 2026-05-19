"""
SMART RESET - Keeps admin user but deletes all other data
Location: inventory_system/reset/smart_reset.py
"""

import psycopg2
import sys
import os

# Add parent directory to path to access app configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================
# REPLACE WITH YOUR ACTUAL NEON CONNECTION STRING
# ============================================================
DATABASE_URL = "postgresql://neondb_owner:npg_F1kgVCxvAK2o@ep-quiet-river-aoi8ja0k-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def smart_reset():
    print("\n" + "=" * 60)
    print("🔧 SMART RESET - Keep Admin User")
    print("=" * 60)
    print("This will delete:")
    print("  ✗ All Products")
    print("  ✗ All Inventory/Stock")
    print("  ✗ All Orders")
    print("  ✗ All Transactions")
    print("  ✗ All Non-Admin Users")
    print("  ✓ Admin user will be preserved")
    print("=" * 60)
    
    confirm = input("\n⚠️  Type 'SMART' to confirm reset: ")
    
    if confirm != 'SMART':
        print("❌ Reset cancelled.")
        return
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("\n🔄 Processing...")
        
        # Delete non-admin users
        cursor.execute("DELETE FROM users WHERE username != 'admin';")
        print(f"  ✓ Deleted {cursor.rowcount} non-admin users")
        
        # Delete transactions
        cursor.execute("DELETE FROM transactions;")
        print(f"  ✓ Deleted {cursor.rowcount} transactions")
        
        # Delete sales orders
        cursor.execute("DELETE FROM sales_orders;")
        print(f"  ✓ Deleted {cursor.rowcount} orders")
        
        # Delete inventory
        cursor.execute("DELETE FROM inventory;")
        print(f"  ✓ Deleted {cursor.rowcount} inventory records")
        
        # Delete products
        cursor.execute("DELETE FROM products;")
        print(f"  ✓ Deleted {cursor.rowcount} products")
        
        # Reset sequences
        print("\n🔄 Resetting ID sequences...")
        cursor.execute("ALTER SEQUENCE products_id_seq RESTART WITH 1;")
        cursor.execute("ALTER SEQUENCE inventory_id_seq RESTART WITH 1;")
        cursor.execute("ALTER SEQUENCE sales_orders_id_seq RESTART WITH 1;")
        cursor.execute("ALTER SEQUENCE transactions_id_seq RESTART WITH 1;")
        cursor.execute("ALTER SEQUENCE users_id_seq RESTART WITH 1;")
        print("  ✓ All sequences reset")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ SMART RESET COMPLETE!")
        print("=" * 60)
        print("\n✓ Admin user preserved:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\n✓ All other data deleted successfully!")
        print("\n💡 Now run 'python app.py' to start fresh.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure:")
        print("  1. Your database connection string is correct")
        print("  2. You have replaced YOUR_ACTUAL_PASSWORD")
        print("  3. Your internet connection is working")

if __name__ == '__main__':
    smart_reset()