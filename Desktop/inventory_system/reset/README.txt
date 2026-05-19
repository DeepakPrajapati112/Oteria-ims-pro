===========================================
DATABASE RESET SCRIPTS - INSTRUCTIONS
===========================================

📁 Location: inventory_system/reset/

🔧 Available Scripts:

1. smart_reset.py (RECOMMENDED)
   - Keeps admin user (admin/admin123)
   - Deletes all products, stock, orders, transactions
   - Best for fresh start while keeping login access

2. reset_db.py
   - Deletes EVERYTHING including admin user
   - Complete fresh start
   - Admin user will be recreated when you run app.py

3. reset_with_backup.py
   - Creates backup before resetting
   - Best for safety before major changes

===========================================
HOW TO USE:
===========================================

Step 1: Stop the server (Ctrl+C in terminal)

Step 2: Navigate to reset folder:
   cd C:\Users\DELL\Desktop\inventory_system\reset

Step 3: Update connection string in the script file
   - Open the .py file
   - Replace YOUR_ACTUAL_PASSWORD with your Neon password

Step 4: Run the script:
   python smart_reset.py

Step 5: Type confirmation when prompted

Step 6: Go back to main folder:
   cd ..

Step 7: Restart the server:
   python app.py

===========================================
IMPORTANT NOTES:
===========================================

⚠️ Always stop the Flask server before resetting
⚠️ Make sure to update the connection string in each script
⚠️ Backups are saved to timestamped folders
⚠️ After reset, login with admin/admin123

===========================================