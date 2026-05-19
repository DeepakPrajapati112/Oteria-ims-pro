"""
COMPLETE DATABASE RESET - Deletes all data including admin
Location: inventory_system/reset/reset_db.py
"""

import psycopg2
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================
# REPLACE WITH YOUR ACTUAL NEON CONNECTION STRING
# ============================================================
DATABASE_URL = "postgresql://neondb_owner:npg_F1kgVCxvAK2o@ep-quiet-river-aoi8ja0k-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def complete_reset():
    print("\n" + "=" * 60)
    print("⚠️  COMPLETE DATABASE RESET")
    print("=" * 60)
    print("This will DELETE EVERYTHING including:")
    print("  ✗ All Products")
    print("  ✗ All Inventory")
    print("  ✗ All Orders")
    print("  ✗ All Transactions")
    print("  ✗ All Users (including admin)")
    print("=" * 60)
    
    confirm = input("\n⚠️  Type 'DELETE ALL' to confirm: ")
    
    if confirm != 'DELETE ALL':
        print("❌ Reset cancelled.")
        return
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("\n🔄 Dropping all tables...")
        
        tables = ['sales_orders', 'inventory', 'products', 'transactions', 'users']
        for table in tables:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS {table} CASCADE;')
                print(f"  ✓ Dropped: {table}")
            except Exception as e:
                print(f"  ✗ Error dropping {table}: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ COMPLETE RESET DONE!")
        print("=" * 60)
        print("\n💡 Now run 'python app.py' to recreate all tables and admin user.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    complete_reset()