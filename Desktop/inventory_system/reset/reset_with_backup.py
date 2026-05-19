"""
RESET WITH BACKUP - Creates backup before resetting
Location: inventory_system/reset/reset_with_backup.py
"""

import psycopg2
import csv
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================
# REPLACE WITH YOUR ACTUAL NEON CONNECTION STRING
# ============================================================
DATABASE_URL = "postgresql://neondb_owner:npg_F1kgVCxvAK2o@ep-quiet-river-aoi8ja0k-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def backup_table(cursor, table_name, backup_dir):
    """Backup a table to CSV file"""
    try:
        cursor.execute(f'SELECT * FROM {table_name}')
        rows = cursor.fetchall()
        
        if rows:
            # Get column names
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = [col[0] for col in cursor.fetchall()]
            
            # Write to CSV
            filename = os.path.join(backup_dir, f'{table_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(rows)
            
            print(f"  ✓ Backed up {len(rows)} rows from {table_name}")
            return True
        else:
            print(f"  - No data in {table_name}")
            return True
    except Exception as e:
        print(f"  ✗ Error backing up {table_name}: {e}")
        return False

def reset_with_backup():
    print("\n" + "=" * 60)
    print("📦 RESET WITH BACKUP")
    print("=" * 60)
    
    # Create backup directory
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"\n📁 Backup will be saved to: {backup_dir}/")
    
    confirm = input("\n⚠️  Type 'BACKUP' to confirm: ")
    
    if confirm != 'BACKUP':
        print("❌ Cancelled.")
        return
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("\n📦 Creating backups...")
        tables = ['products', 'inventory', 'sales_orders', 'transactions', 'users']
        for table in tables:
            backup_table(cursor, table, backup_dir)
        
        print("\n🔄 Dropping all tables...")
        for table in tables:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS {table} CASCADE;')
                print(f"  ✓ Dropped: {table}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ RESET WITH BACKUP COMPLETE!")
        print("=" * 60)
        print(f"\n📁 Backup saved to: {backup_dir}/")
        print("\n💡 Now run 'python app.py' to recreate tables.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    reset_with_backup()