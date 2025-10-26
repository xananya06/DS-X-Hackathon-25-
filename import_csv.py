"""
import_csv.py - Import brands from CSV to SQLite database
Run this to convert your brands.csv to the database format

Usage:
    python import_csv.py
    python import_csv.py --csv path/to/brands.csv
    python import_csv.py --csv brands.csv --db my_brands.db
"""

import argparse
from database import BrandDatabase


def main():
    parser = argparse.ArgumentParser(description='Import brands from CSV to database')
    parser.add_argument('--csv', type=str, default='brands.csv', 
                       help='Path to CSV file (default: brands.csv)')
    parser.add_argument('--db', type=str, default='brands.db',
                       help='Path to database file (default: brands.db)')
    parser.add_argument('--force', action='store_true',
                       help='Force re-import even if database exists')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("CSV to Database Import Tool")
    print("="*60 + "\n")
    
    print(f"📁 CSV File: {args.csv}")
    print(f"💾 Database: {args.db}")
    
    if args.force:
        print("⚠️  Force mode: Will overwrite existing database")
        import os
        if os.path.exists(args.db):
            os.remove(args.db)
            print(f"   Deleted existing {args.db}")
    
    print("\n🔄 Initializing database...")
    db = BrandDatabase(args.db)
    
    print(f"\n📥 Importing from {args.csv}...")
    result = db.import_from_csv(args.csv)
    
    if result['success']:
        print("\n✅ Import Successful!")
        print(f"   Imported: {result['imported_count']} brands")
        if result.get('skipped_count', 0) > 0:
            print(f"   Skipped: {result['skipped_count']} brands (errors)")
        print(f"   Total in CSV: {result['total_rows']}")
        
        # Show stats
        print("\n📊 Database Statistics:")
        stats = db.get_database_stats()
        print(f"   Total brands: {stats['total_brands']}")
        print(f"   Cruelty-free: {stats['cruelty_free_count']} ({stats['cruelty_free_percentage']}%)")
        print(f"   Not cruelty-free: {stats['not_cruelty_free_count']}")
        
        # Show sample brands
        print("\n🔍 Sample Brands (first 10):")
        brands = db.get_all_brands()[:10]
        for brand in brands:
            status = "✓" if brand['is_cruelty_free'] else "✗"
            conf = f"{brand['confidence']:.0%}"
            print(f"   {status} {brand['brand_name']} (Confidence: {conf})")
        
        print("\n" + "="*60)
        print("✅ Ready to use! Your database is set up.")
        print("="*60)
        
        # Test a query
        print("\n🧪 Testing database query...")
        test_brand = brands[0]['brand_name'] if brands else None
        if test_brand:
            result = db.check_brand(test_brand)
            print(f"   Queried: {test_brand}")
            print(f"   Found: {result['found']}")
            print(f"   Cruelty-Free: {result.get('is_cruelty_free', 'N/A')}")
        
    else:
        print("\n❌ Import Failed!")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        print("\n💡 Tips:")
        print("   - Make sure CSV file exists")
        print("   - Check CSV has required columns: brand_name, cruelty_free, parent_company, certification")
        print("   - Install pandas: pip install pandas")
        print("   - Run with --force to overwrite existing database")


if __name__ == "__main__":
    main()