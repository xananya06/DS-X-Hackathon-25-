"""
Cruelty-Free Brands Data Collection Script
Creates brands.csv with comprehensive beauty brand data

Run this first: python brands_data_collection.py
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def create_comprehensive_dataset():
    """
    Create a comprehensive starter dataset with 100+ popular brands
    Covers makeup, skincare, haircare, fragrance
    """
    
    brands = [
        # ==================== MAKEUP - CRUELTY-FREE ====================
        {'brand_name': 'e.l.f. Cosmetics', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'NYX Professional Makeup', 'cruelty_free': True, 'parent_company': "L'Oréal", 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'Wet n Wild', 'cruelty_free': True, 'parent_company': 'Markwins Beauty', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'ColourPop', 'cruelty_free': True, 'parent_company': 'Seed Beauty', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'Milani', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'Essence', 'cruelty_free': True, 'parent_company': 'Cosnova', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'Catrice', 'cruelty_free': True, 'parent_company': 'Cosnova', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'Makeup Revolution', 'cruelty_free': True, 'parent_company': 'Revolution Beauty', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'Physicians Formula', 'cruelty_free': True, 'parent_company': 'Markwins Beauty', 
         'certification': 'Leaping Bunny', 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'Pacifica', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Makeup', 'price_tier': 'Budget'},
        
        {'brand_name': 'Anastasia Beverly Hills', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Too Faced', 'cruelty_free': True, 'parent_company': 'Estée Lauder', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Urban Decay', 'cruelty_free': True, 'parent_company': "L'Oréal", 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Tarte Cosmetics', 'cruelty_free': True, 'parent_company': 'Kose', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Fenty Beauty', 'cruelty_free': True, 'parent_company': 'LVMH', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'KVD Beauty', 'cruelty_free': True, 'parent_company': 'Kendo', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Morphe', 'cruelty_free': True, 'parent_company': 'Forma Brands', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'BH Cosmetics', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Becca', 'cruelty_free': True, 'parent_company': 'Estée Lauder', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Smashbox', 'cruelty_free': True, 'parent_company': 'Estée Lauder', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Cover FX', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Bare Minerals', 'cruelty_free': True, 'parent_company': 'Shiseido', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Mid-range'},
        
        {'brand_name': 'Hourglass Cosmetics', 'cruelty_free': True, 'parent_company': 'Unilever', 
         'certification': 'PETA', 'category': 'Makeup', 'price_tier': 'Luxury'},
        {'brand_name': 'Ilia Beauty', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Makeup', 'price_tier': 'Luxury'},
        {'brand_name': 'RMS Beauty', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Makeup', 'price_tier': 'Luxury'},
        
        # ==================== MAKEUP - NOT CRUELTY-FREE ====================
        {'brand_name': 'Maybelline', 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'Revlon', 'cruelty_free': False, 'parent_company': 'Revlon Inc', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'CoverGirl', 'cruelty_free': False, 'parent_company': 'Coty', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': "L'Oréal Paris", 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'Rimmel London', 'cruelty_free': False, 'parent_company': 'Coty', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Budget'},
        {'brand_name': 'Almay', 'cruelty_free': False, 'parent_company': 'Revlon Inc', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Budget'},
        
        {'brand_name': 'MAC Cosmetics', 'cruelty_free': False, 'parent_company': 'Estée Lauder', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Clinique', 'cruelty_free': False, 'parent_company': 'Estée Lauder', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Benefit Cosmetics', 'cruelty_free': False, 'parent_company': 'LVMH', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'Bobbi Brown', 'cruelty_free': False, 'parent_company': 'Estée Lauder', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Mid-range'},
        {'brand_name': 'NARS', 'cruelty_free': False, 'parent_company': 'Shiseido', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Mid-range'},
        
        {'brand_name': 'Estée Lauder', 'cruelty_free': False, 'parent_company': 'Estée Lauder', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Luxury'},
        {'brand_name': 'Lancôme', 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Luxury'},
        {'brand_name': 'Chanel', 'cruelty_free': False, 'parent_company': 'Chanel', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Luxury'},
        {'brand_name': 'Dior', 'cruelty_free': False, 'parent_company': 'LVMH', 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Luxury'},
        {'brand_name': 'Giorgio Armani Beauty', 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Luxury'},
        {'brand_name': 'Yves Saint Laurent', 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Makeup', 'price_tier': 'Luxury'},
        
        # ==================== SKINCARE - CRUELTY-FREE ====================
        {'brand_name': 'The Ordinary', 'cruelty_free': True, 'parent_company': 'Deciem', 
         'certification': 'PETA', 'category': 'Skincare', 'price_tier': 'Budget'},
        {'brand_name': 'CeraVe', 'cruelty_free': True, 'parent_company': "L'Oréal", 
         'certification': 'PETA', 'category': 'Skincare', 'price_tier': 'Budget'},
        {'brand_name': 'Pacifica', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Skincare', 'price_tier': 'Budget'},
        {'brand_name': 'Derma E', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Skincare', 'price_tier': 'Budget'},
        {'brand_name': 'Acure', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Skincare', 'price_tier': 'Budget'},
        {'brand_name': 'Alba Botanica', 'cruelty_free': True, 'parent_company': 'Hain Celestial', 
         'certification': 'Leaping Bunny', 'category': 'Skincare', 'price_tier': 'Budget'},
        {'brand_name': 'Bliss', 'cruelty_free': True, 'parent_company': 'Steward Corporation', 
         'certification': 'PETA', 'category': 'Skincare', 'price_tier': 'Budget'},
        
        {'brand_name': "Paula's Choice", 'cruelty_free': True, 'parent_company': 'Unilever', 
         'certification': 'PETA', 'category': 'Skincare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Youth to the People', 'cruelty_free': True, 'parent_company': "L'Oréal", 
         'certification': 'PETA', 'category': 'Skincare', 'price_tier': 'Mid-range'},
        {'brand_name': 'First Aid Beauty', 'cruelty_free': True, 'parent_company': 'Procter & Gamble', 
         'certification': 'PETA', 'category': 'Skincare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Glow Recipe', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Skincare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Herbivore Botanicals', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Skincare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Tata Harper', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Skincare', 'price_tier': 'Luxury'},
        {'brand_name': 'Drunk Elephant', 'cruelty_free': True, 'parent_company': 'Shiseido', 
         'certification': 'PETA', 'category': 'Skincare', 'price_tier': 'Luxury'},
        {'brand_name': 'Sunday Riley', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Skincare', 'price_tier': 'Luxury'},
        
        # ==================== SKINCARE - NOT CRUELTY-FREE ====================
        {'brand_name': 'Neutrogena', 'cruelty_free': False, 'parent_company': 'Johnson & Johnson', 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Budget'},
        {'brand_name': 'Olay', 'cruelty_free': False, 'parent_company': 'Procter & Gamble', 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Budget'},
        {'brand_name': 'Aveeno', 'cruelty_free': False, 'parent_company': 'Johnson & Johnson', 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Budget'},
        {'brand_name': 'Clean & Clear', 'cruelty_free': False, 'parent_company': 'Johnson & Johnson', 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Budget'},
        {'brand_name': 'Pond\'s', 'cruelty_free': False, 'parent_company': 'Unilever', 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Budget'},
        
        {'brand_name': 'La Roche-Posay', 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Vichy', 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Mid-range'},
        {'brand_name': "Kiehl's", 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Clinique', 'cruelty_free': False, 'parent_company': 'Estée Lauder', 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Origins', 'cruelty_free': False, 'parent_company': 'Estée Lauder', 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Mid-range'},
        
        {'brand_name': 'La Mer', 'cruelty_free': False, 'parent_company': 'Estée Lauder', 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Luxury'},
        {'brand_name': 'SK-II', 'cruelty_free': False, 'parent_company': 'Procter & Gamble', 
         'certification': None, 'category': 'Skincare', 'price_tier': 'Luxury'},
        
        # ==================== HAIRCARE - CRUELTY-FREE ====================
        {'brand_name': "Not Your Mother's", 'cruelty_free': True, 'parent_company': 'Revlon', 
         'certification': 'PETA', 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'OGX', 'cruelty_free': True, 'parent_company': 'Johnson & Johnson', 
         'certification': 'PETA', 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'Giovanni', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'Kristen Ess', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'Shea Moisture', 'cruelty_free': True, 'parent_company': 'Unilever', 
         'certification': 'PETA', 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'Love Beauty and Planet', 'cruelty_free': True, 'parent_company': 'Unilever', 
         'certification': 'PETA', 'category': 'Haircare', 'price_tier': 'Budget'},
        
        {'brand_name': 'Briogeo', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Haircare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Amika', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Haircare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Ouai', 'cruelty_free': True, 'parent_company': 'Procter & Gamble', 
         'certification': 'PETA', 'category': 'Haircare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Function of Beauty', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Haircare', 'price_tier': 'Mid-range'},
        
        {'brand_name': 'Olaplex', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Haircare', 'price_tier': 'Luxury'},
        
        # ==================== HAIRCARE - NOT CRUELTY-FREE ====================
        {'brand_name': 'Pantene', 'cruelty_free': False, 'parent_company': 'Procter & Gamble', 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'Head & Shoulders', 'cruelty_free': False, 'parent_company': 'Procter & Gamble', 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'Herbal Essences', 'cruelty_free': False, 'parent_company': 'Procter & Gamble', 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'TRESemmé', 'cruelty_free': False, 'parent_company': 'Unilever', 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'Garnier', 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'Aussie', 'cruelty_free': False, 'parent_company': 'Procter & Gamble', 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Budget'},
        {'brand_name': 'Dove', 'cruelty_free': False, 'parent_company': 'Unilever', 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Budget'},
        
        {'brand_name': 'Redken', 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Matrix', 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Mid-range'},
        {'brand_name': 'Bed Head', 'cruelty_free': False, 'parent_company': 'Unilever', 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Mid-range'},
        
        {'brand_name': 'Kérastase', 'cruelty_free': False, 'parent_company': "L'Oréal", 
         'certification': None, 'category': 'Haircare', 'price_tier': 'Luxury'},
        
        # ==================== FRAGRANCE - CRUELTY-FREE ====================
        {'brand_name': 'Pacifica', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'Leaping Bunny', 'category': 'Fragrance', 'price_tier': 'Budget'},
        {'brand_name': 'Lush', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Fragrance', 'price_tier': 'Mid-range'},
        {'brand_name': 'Skylar', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Fragrance', 'price_tier': 'Mid-range'},
        {'brand_name': 'Phlur', 'cruelty_free': True, 'parent_company': 'Independent', 
         'certification': 'PETA', 'category': 'Fragrance', 'price_tier': 'Mid-range'},
        
        # ==================== FRAGRANCE - NOT CRUELTY-FREE ====================
        {'brand_name': 'Calvin Klein', 'cruelty_free': False, 'parent_company': 'Coty', 
         'certification': None, 'category': 'Fragrance', 'price_tier': 'Mid-range'},
        {'brand_name': 'Marc Jacobs Fragrances', 'cruelty_free': False, 'parent_company': 'Coty', 
         'certification': None, 'category': 'Fragrance', 'price_tier': 'Luxury'},
        {'brand_name': 'Versace', 'cruelty_free': False, 'parent_company': 'Euroitalia', 
         'certification': None, 'category': 'Fragrance', 'price_tier': 'Luxury'},
        {'brand_name': 'Dolce & Gabbana', 'cruelty_free': False, 'parent_company': 'Shiseido', 
         'certification': None, 'category': 'Fragrance', 'price_tier': 'Luxury'},
    ]
    
    df = pd.DataFrame(brands)
    df.to_csv('brands.csv', index=False)
    
    print("=" * 70)
    print("✅ SUCCESS! Created brands.csv")
    print("=" * 70)
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total brands: {len(df)}")
    print(f"   ✓ Cruelty-free: {len(df[df['cruelty_free'] == True])} ({len(df[df['cruelty_free'] == True])/len(df)*100:.1f}%)")
    print(f"   ✗ Not cruelty-free: {len(df[df['cruelty_free'] == False])} ({len(df[df['cruelty_free'] == False])/len(df)*100:.1f}%)")
    
    print(f"\n📦 Breakdown by Category:")
    for category in df['category'].unique():
        count = len(df[df['category'] == category])
        cf_count = len(df[(df['category'] == category) & (df['cruelty_free'] == True)])
        print(f"   {category}: {count} brands ({cf_count} cruelty-free)")
    
    print(f"\n💰 Breakdown by Price:")
    for price in ['Budget', 'Mid-range', 'Luxury']:
        count = len(df[df['price_tier'] == price])
        print(f"   {price}: {count} brands")
    
    print(f"\n🏆 Certifications:")
    print(f"   Leaping Bunny: {len(df[df['certification'] == 'Leaping Bunny'])}")
    print(f"   PETA: {len(df[df['certification'] == 'PETA'])}")
    print(f"   None: {len(df[df['certification'].isna()])}")
    
    print("\n" + "=" * 70)
    print("🎯 Next Steps:")
    print("   1. Review brands.csv and add more if needed")
    print("   2. Test search: python -c \"import pandas as pd; print(pd.read_csv('brands.csv').head())\"")
    print("   3. Run your app: streamlit run app.py")
    print("=" * 70)
    
    return df


def add_more_brands(additional_brands_list):
    """
    Add more brands to existing CSV
    Usage: add_more_brands([{'brand_name': 'X', ...}, {...}])
    """
    try:
        existing_df = pd.read_csv('brands.csv')
        new_df = pd.DataFrame(additional_brands_list)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Remove duplicates
        combined_df.drop_duplicates(subset=['brand_name'], keep='first', inplace=True)
        
        combined_df.to_csv('brands.csv', index=False)
        print(f"✅ Added {len(new_df)} brands. Total now: {len(combined_df)}")
        
    except FileNotFoundError:
        print("❌ brands.csv not found. Run create_comprehensive_dataset() first!")


def validate_dataset():
    """Check for common data quality issues"""
    try:
        df = pd.read_csv('brands.csv')
        
        print("\n🔍 Data Quality Check:")
        print("=" * 50)
        
        # Check for missing values
        missing = df.isnull().sum()
        if missing.any():
            print("\n⚠️  Missing values found:")
            print(missing[missing > 0])
        else:
            print("✓ No missing values")
        
        # Check for duplicates
        dupes = df.duplicated(subset=['brand_name']).sum()
        if dupes > 0:
            print(f"\n⚠️  {dupes} duplicate brand names found!")
            print(df[df.duplicated(subset=['brand_name'], keep=False)]['brand_name'].tolist())
        else:
            print("✓ No duplicate brands")
        
        # Check categories
        valid_categories = ['Makeup', 'Skincare', 'Haircare', 'Fragrance']
        invalid_cats = df[~df['category'].isin(valid_categories)]
        if not invalid_cats.empty:
            print(f"\n⚠️  Invalid categories found:")
            print(invalid_cats[['brand_name', 'category']])
        else:
            print("✓ All categories valid")
        
        # Check price tiers
        valid_prices = ['Budget', 'Mid-range', 'Luxury', 'Unknown']
        invalid_prices = df[~df['price_tier'].isin(valid_prices)]
        if not invalid_prices.empty:
            print(f"\n⚠️  Invalid price tiers found:")
            print(invalid_prices[['brand_name', 'price_tier']])
        else:
            print("✓ All price tiers valid")
        
        # Check for suspicious patterns
        print("\n📈 Data Distribution:")
        print(f"   Average brand name length: {df['brand_name'].str.len().mean():.1f} chars")
        print(f"   Shortest: '{df.loc[df['brand_name'].str.len().idxmin(), 'brand_name']}'")
        print(f"   Longest: '{df.loc[df['brand_name'].str.len().idxmax(), 'brand_name']}'")
        
        print("\n✅ Validation complete!")
        
    except FileNotFoundError:
        print("❌ brands.csv not found!")


def export_demo_brands():
    """Export a small list of brands that demo well"""
    try:
        df = pd.read_csv('brands.csv')
        
        # Pick brands that demonstrate key scenarios
        demo_brands = [
            'Maybelline',  # NOT cruelty-free, popular
            'e.l.f. Cosmetics',  # Cruelty-free, budget
            'Fenty Beauty',  # Cruelty-free, trendy
            'MAC Cosmetics',  # NOT cruelty-free, popular
            'Urban Decay',  # Cruelty-free but owned by L'Oreal
            'The Ordinary',  # Cruelty-free skincare, popular
            'Neutrogena',  # NOT cruelty-free skincare
            'OGX',  # Cruelty-free haircare
        ]
        
        demo_df = df[df['brand_name'].isin(demo_brands)]
        demo_df.to_csv('demo_brands.csv', index=False)
        
        print("✅ Created demo_brands.csv with these brands:")
        for brand in demo_brands:
            if brand in df['brand_name'].values:
                status = "✓" if df[df['brand_name'] == brand]['cruelty_free'].iloc[0] else "✗"
                print(f"   {status} {brand}")
        
        print("\n💡 Use these for your 3-minute demo!")
        
    except FileNotFoundError:
        print("❌ brands.csv not found!")


def scrape_leaping_bunny_brands():
    """
    Optional: Try to scrape additional brands from Leaping Bunny
    NOTE: This may not work depending on website structure
    Only use if you have extra time and want more brands
    """
    print("🔍 Attempting to scrape Leaping Bunny website...")
    print("⚠️  This is experimental and may not work")
    
    try:
        url = "https://www.leapingbunny.org/guide/brands"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Hackathon Educational Project)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch page (Status: {response.status_code})")
            return pd.DataFrame()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # This selector may need adjustment based on actual website structure
        # Inspect the website in your browser to find correct selectors
        brand_elements = soup.find_all('div', class_='brand-card')  # Example selector
        
        if not brand_elements:
            print("⚠️  No brands found with current selector")
            print("   Try inspecting the Leaping Bunny website to find correct CSS selector")
            return pd.DataFrame()
        
        brands = []
        for element in brand_elements:
            try:
                name = element.find('h3').text.strip()  # Adjust selector
                brands.append({
                    'brand_name': name,
                    'cruelty_free': True,
                    'certification': 'Leaping Bunny',
                    'parent_company': 'Unknown',
                    'category': 'Unknown',
                    'price_tier': 'Unknown'
                })
            except:
                continue
        
        if brands:
            print(f"✅ Successfully scraped {len(brands)} brands!")
            scraped_df = pd.DataFrame(brands)
            scraped_df.to_csv('scraped_brands.csv', index=False)
            print("   Saved to scraped_brands.csv")
            print("   Review and merge with main dataset manually")
            return scraped_df
        else:
            print("❌ No brands extracted")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Scraping failed: {str(e)}")
        print("   Don't worry - the manual dataset is sufficient for the hackathon!")
        return pd.DataFrame()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🐰 CRUELTY-FREE BRANDS DATA COLLECTION")
    print("=" * 70 + "\n")
    
    # Step 1: Create comprehensive dataset
    print("📦 Step 1: Creating comprehensive dataset...\n")
    df = create_comprehensive_dataset()
    
    # Step 2: Validate data quality
    print("\n📋 Step 2: Validating data quality...\n")
    validate_dataset()
    
    # Step 3: Export demo brands
    print("\n🎯 Step 3: Creating demo subset...\n")
    export_demo_brands()
    
    # Step 4: Optional scraping (only if you want more brands)
    print("\n🌐 Step 4: Optional web scraping...")
    user_input = input("\nWant to try scraping additional brands? (y/n): ").lower()
    
    if user_input == 'y':
        scraped_df = scrape_leaping_bunny_brands()
        if not scraped_df.empty:
            print("\n💡 Tip: Review scraped_brands.csv and manually add good ones to brands.csv")
    else:
        print("⏭️  Skipping web scraping (smart choice for time constraints!)")
    
    print("\n" + "=" * 70)
    print("✅ DATA COLLECTION COMPLETE!")
    print("=" * 70)
    print("\n🎉 You now have:")
    print("   ✓ brands.csv - Your main database")
    print("   ✓ demo_brands.csv - Curated list for demos")
    print("\n🚀 Ready to build your app!")
    print("   Run: streamlit run app.py")
    print("=" * 70 + "\n")