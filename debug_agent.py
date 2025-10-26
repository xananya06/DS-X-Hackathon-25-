"""
Debug script to view agent's learned information
"""
import sqlite3
import os

print("\n" + "="*60)
print("ConsciousCart - Debug Info")
print("="*60)

# Check database
db_path = "brands.db"
if os.path.exists(db_path):
    print(f"\n✅ Database found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Show brands
    cursor.execute("SELECT COUNT(*) FROM brands")
    count = cursor.fetchone()[0]
    print(f"\n📊 Total brands in database: {count}")
    
    # Show all brands
    cursor.execute("""
        SELECT name, is_cruelty_free, parent_company, last_verified 
        FROM brands 
        ORDER BY last_verified DESC
    """)
    
    print("\n🔍 Brands in database:")
    print("-" * 60)
    for row in cursor.fetchall():
        name, is_cf, parent, verified = row
        status = "✅ Cruelty-Free" if is_cf else "❌ Not CF"
        parent_info = f" (Parent: {parent})" if parent else ""
        print(f"{status:<20} {name:<20}{parent_info}")
    
    conn.close()
else:
    print(f"\n❌ Database not found: {db_path}")
    print("Run the app first to create the database")

print("\n" + "="*60)
print("To view user preferences, they are stored in session state")
print("Check the Streamlit app's sidebar for real-time profile")
print("="*60 + "\n")