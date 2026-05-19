import psycopg2

# Replace with your Neon connection string
conn_string = "postgresql://neondb_owner:npg_IgYH4serGx6y@ep-young-wind-a1ncwxcu-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Drop dependent views first
    cursor.execute("DROP VIEW IF EXISTS batch_shelf_life CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS batches CASCADE;")
    
    # Drop all our tables
    cursor.execute("DROP TABLE IF EXISTS sales_orders CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS inventory CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS products CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS transactions CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
    
    print("✓ Database cleaned successfully!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    print("\nIf you see errors, just create a new database in Neon instead.")