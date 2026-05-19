from werkzeug.security import generate_password_hash
import psycopg2
import os

# Database connection (Render ka DATABASE_URL)
DATABASE_URL = "postgresql://neondb_owner:npg_F1kgVCxvAK2o@ep-quiet-river-aoi8ja0k-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

def reset_admin_password():
    # Generate hash for 'admin123'
    new_password = 'admin123'
    hashed_password = generate_password_hash(new_password)
    
    print(f"Generated hash for password '{new_password}':")
    print(hashed_password)
    print("\n" + "="*50)
    
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # First, delete existing admin if any
        cur.execute("DELETE FROM users WHERE username = 'admin'")
        print("✓ Removed existing admin user (if any)")
        
        # Create new admin
        cur.execute("""
            INSERT INTO users (username, password, role, full_name, email, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, ('admin', hashed_password, 'admin', 'Administrator', 'admin@imspro.com'))
        
        conn.commit()
        print("✓ New admin user created successfully!")
        
        # Verify
        cur.execute("SELECT id, username, role FROM users WHERE username = 'admin'")
        user = cur.fetchone()
        if user:
            print(f"✓ Verified: ID={user[0]}, Username={user[1]}, Role={user[2]}")
        
        cur.close()
        conn.close()
        
        print("\n" + "="*50)
        print("✅ SUCCESS! You can now login with:")
        print("   Username: admin")
        print("   Password: admin123")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reset_admin_password()