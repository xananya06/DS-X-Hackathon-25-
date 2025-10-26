"""
database.py - Database operations for ConsciousCart
Handles all SQLite operations for brand verification storage
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class BrandDatabase:
    """Manages SQLite database for brand information"""
    
    def __init__(self, db_path: str = "brands.db"):
        self.db_path = db_path
        self.initialize_database()
        self.seed_database()
    
    def initialize_database(self):
        """Create database schema if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                is_cruelty_free BOOLEAN NOT NULL,
                parent_company TEXT,
                explanation TEXT,
                sources TEXT,
                confidence FLOAT DEFAULT 0.9,
                last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add search history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand_name TEXT NOT NULL,
                user_query TEXT,
                result_found BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"[Database] Initialized at {self.db_path}")
    
    def seed_database(self):
        """Pre-populate database - tries CSV first, then fallback data"""
        # Try to import from CSV first
        try:
            import_result = self.import_from_csv("brands.csv")
            if import_result['success']:
                print(f"[Database] Imported {import_result['imported_count']} brands from CSV")
                return
        except FileNotFoundError:
            print("[Database] brands.csv not found, using fallback data")
        except Exception as e:
            print(f"[Database] Error importing CSV: {e}, using fallback data")
        
        # Fallback: minimal seed data
        known_brands = [
            ("Maybelline", False, "L'Oréal", "Owned by L'Oréal which tests in China", "PETA,Leaping Bunny", 0.95),
            ("Fenty Beauty", True, "LVMH", "Certified cruelty-free, no animal testing", "Leaping Bunny,PETA", 0.95),
            ("e.l.f. Cosmetics", True, "Independent", "Certified cruelty-free and 100% vegan", "Leaping Bunny,PETA", 0.95),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for brand_data in known_brands:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO brands 
                    (name, is_cruelty_free, parent_company, explanation, sources, confidence)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, brand_data)
            except sqlite3.Error as e:
                print(f"[Database] Error inserting {brand_data[0]}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"[Database] Seeded with {len(known_brands)} fallback brands")
    
    def import_from_csv(self, csv_path: str = "brands.csv") -> Dict:
        """
        Import brands from CSV file
        
        CSV Format:
        brand_name, cruelty_free, parent_company, certification, category, price_tier
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            Dictionary with import results
        """
        try:
            import pandas as pd
        except ImportError:
            print("[Database] pandas not installed. Install with: pip install pandas")
            return {"success": False, "error": "pandas not installed"}
        
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            
            # Validate required columns
            required_cols = ['brand_name', 'cruelty_free', 'parent_company', 'certification']
            missing_cols = set(required_cols) - set(df.columns)
            if missing_cols:
                return {"success": False, "error": f"Missing columns: {missing_cols}"}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            skipped_count = 0
            
            for _, row in df.iterrows():
                brand_name = row['brand_name']
                is_cruelty_free = row['cruelty_free']
                parent_company = row['parent_company'] if pd.notna(row['parent_company']) else None
                certification = row['certification'] if pd.notna(row['certification']) else None
                
                # Convert boolean strings to actual booleans
                if isinstance(is_cruelty_free, str):
                    is_cruelty_free = is_cruelty_free.lower() in ['true', '1', 'yes']
                
                # Generate explanation based on data
                explanation_parts = []
                if is_cruelty_free:
                    explanation_parts.append("Certified cruelty-free")
                    if certification:
                        explanation_parts.append(f"by {certification}")
                else:
                    explanation_parts.append("Not cruelty-free")
                    if parent_company and parent_company not in ['Independent', 'Unknown', '']:
                        explanation_parts.append(f"(Parent: {parent_company})")
                
                explanation = " ".join(explanation_parts)
                
                # Sources from certification
                sources = certification if certification else ""
                
                # Calculate confidence based on certification
                confidence = 0.95 if certification in ['Leaping Bunny', 'PETA'] else 0.85
                
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO brands 
                        (name, is_cruelty_free, parent_company, explanation, sources, confidence)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (brand_name, is_cruelty_free, parent_company, explanation, sources, confidence))
                    imported_count += 1
                except sqlite3.Error as e:
                    print(f"[Database] Error importing {brand_name}: {e}")
                    skipped_count += 1
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "imported_count": imported_count,
                "skipped_count": skipped_count,
                "total_rows": len(df)
            }
            
        except FileNotFoundError:
            return {"success": False, "error": f"File not found: {csv_path}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_brand(self, brand_name: str) -> Dict:
        """
        Check if brand exists in database
        
        Args:
            brand_name: Name of the brand to look up
            
        Returns:
            Dictionary with brand information or {"found": False}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, is_cruelty_free, parent_company, explanation, 
                   sources, confidence, last_verified
            FROM brands 
            WHERE LOWER(name) = LOWER(?) OR LOWER(name) LIKE LOWER(?)
        """, (brand_name, f"%{brand_name}%"))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            name, is_cf, parent, explanation, sources, confidence, last_verified = result
            
            # Check if data is stale (>30 days old)
            try:
                last_verified_date = datetime.strptime(last_verified, "%Y-%m-%d %H:%M:%S")
                is_stale = datetime.now() - last_verified_date > timedelta(days=30)
            except:
                is_stale = False
            
            return {
                "found": True,
                "brand_name": name,
                "is_cruelty_free": bool(is_cf),
                "parent_company": parent,
                "explanation": explanation,
                "sources": sources.split(",") if sources else [],
                "confidence": confidence,
                "last_verified": last_verified,
                "is_stale": is_stale
            }
        
        return {"found": False}
    
    def save_brand(
        self, 
        brand_name: str, 
        is_cruelty_free: bool,
        parent_company: Optional[str] = None,
        explanation: str = "",
        sources: Optional[List[str]] = None,
        confidence: float = 0.9
    ) -> Dict:
        """
        Save or update brand information in database
        
        Args:
            brand_name: Name of the brand
            is_cruelty_free: Whether brand is cruelty-free
            parent_company: Parent company name (optional)
            explanation: Explanation of status
            sources: List of verification sources
            confidence: Confidence score (0.0-1.0)
            
        Returns:
            Dictionary with success status and message
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sources_str = ",".join(sources) if sources else ""
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO brands 
                (name, is_cruelty_free, parent_company, explanation, sources, confidence, last_verified)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (brand_name, is_cruelty_free, parent_company, explanation, sources_str, confidence))
            
            conn.commit()
            conn.close()
            
            print(f"[Database] Saved {brand_name} (CF: {is_cruelty_free}, Confidence: {confidence:.2f})")
            
            return {
                "success": True, 
                "message": f"Saved {brand_name} to database",
                "brand_name": brand_name
            }
            
        except sqlite3.Error as e:
            conn.close()
            print(f"[Database] Error saving {brand_name}: {e}")
            return {
                "success": False, 
                "error": str(e)
            }
    
    def get_all_brands(self, cruelty_free_only: bool = False) -> List[Dict]:
        """
        Get all brands from database
        
        Args:
            cruelty_free_only: If True, only return cruelty-free brands
            
        Returns:
            List of brand dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if cruelty_free_only:
            cursor.execute("""
                SELECT name, is_cruelty_free, parent_company, explanation, 
                       sources, confidence, last_verified
                FROM brands 
                WHERE is_cruelty_free = 1
                ORDER BY name
            """)
        else:
            cursor.execute("""
                SELECT name, is_cruelty_free, parent_company, explanation, 
                       sources, confidence, last_verified
                FROM brands 
                ORDER BY name
            """)
        
        results = cursor.fetchall()
        conn.close()
        
        brands = []
        for row in results:
            name, is_cf, parent, explanation, sources, confidence, last_verified = row
            brands.append({
                "brand_name": name,
                "is_cruelty_free": bool(is_cf),
                "parent_company": parent,
                "explanation": explanation,
                "sources": sources.split(",") if sources else [],
                "confidence": confidence,
                "last_verified": last_verified
            })
        
        return brands
    
    def search_brands(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for brands by partial name match
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching brand dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, is_cruelty_free, parent_company, explanation, 
                   sources, confidence, last_verified
            FROM brands 
            WHERE LOWER(name) LIKE LOWER(?)
            ORDER BY name
            LIMIT ?
        """, (f"%{query}%", limit))
        
        results = cursor.fetchall()
        conn.close()
        
        brands = []
        for row in results:
            name, is_cf, parent, explanation, sources, confidence, last_verified = row
            brands.append({
                "brand_name": name,
                "is_cruelty_free": bool(is_cf),
                "parent_company": parent,
                "explanation": explanation,
                "sources": sources.split(",") if sources else [],
                "confidence": confidence,
                "last_verified": last_verified
            })
        
        return brands
    
    def log_search(self, brand_name: str, user_query: str, result_found: bool):
        """
        Log a search query for analytics
        
        Args:
            brand_name: Brand that was searched
            user_query: Original user query
            result_found: Whether brand was found in database
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO search_history (brand_name, user_query, result_found)
                VALUES (?, ?, ?)
            """, (brand_name, user_query, result_found))
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"[Database] Error logging search: {e}")
        finally:
            conn.close()
    
    def get_database_stats(self) -> Dict:
        """
        Get statistics about the database
        
        Returns:
            Dictionary with database statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total brands
        cursor.execute("SELECT COUNT(*) FROM brands")
        total = cursor.fetchone()[0]
        
        # Cruelty-free count
        cursor.execute("SELECT COUNT(*) FROM brands WHERE is_cruelty_free = 1")
        cf_count = cursor.fetchone()[0]
        
        # Recent searches
        cursor.execute("""
            SELECT COUNT(*) FROM search_history 
            WHERE timestamp > datetime('now', '-7 days')
        """)
        recent_searches = cursor.fetchone()[0]
        
        # Most searched brands
        cursor.execute("""
            SELECT brand_name, COUNT(*) as count 
            FROM search_history 
            GROUP BY brand_name 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_searches = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_brands": total,
            "cruelty_free_count": cf_count,
            "not_cruelty_free_count": total - cf_count,
            "cruelty_free_percentage": round((cf_count / total * 100) if total > 0 else 0, 1),
            "recent_searches_7d": recent_searches,
            "top_searched_brands": [{"brand": b[0], "count": b[1]} for b in top_searches]
        }
    
    def delete_brand(self, brand_name: str) -> Dict:
        """
        Delete a brand from database
        
        Args:
            brand_name: Name of brand to delete
            
        Returns:
            Dictionary with success status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM brands WHERE LOWER(name) = LOWER(?)", (brand_name,))
            conn.commit()
            
            if cursor.rowcount > 0:
                conn.close()
                return {"success": True, "message": f"Deleted {brand_name}"}
            else:
                conn.close()
                return {"success": False, "message": f"Brand {brand_name} not found"}
                
        except sqlite3.Error as e:
            conn.close()
            return {"success": False, "error": str(e)}
    
    def update_confidence(self, brand_name: str, new_confidence: float) -> Dict:
        """
        Update confidence score for a brand
        
        Args:
            brand_name: Name of the brand
            new_confidence: New confidence score (0.0-1.0)
            
        Returns:
            Dictionary with success status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE brands 
                SET confidence = ?, last_verified = CURRENT_TIMESTAMP
                WHERE LOWER(name) = LOWER(?)
            """, (new_confidence, brand_name))
            
            conn.commit()
            conn.close()
            
            if cursor.rowcount > 0:
                return {"success": True, "message": f"Updated confidence for {brand_name}"}
            else:
                return {"success": False, "message": f"Brand {brand_name} not found"}
                
        except sqlite3.Error as e:
            conn.close()
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Cleanup method (if needed for connection pooling in future)"""
        pass
    
    def export_to_csv(self, csv_path: str = "brands_export.csv") -> Dict:
        """
        Export database to CSV file
        
        Args:
            csv_path: Path where CSV should be saved
            
        Returns:
            Dictionary with export results
        """
        try:
            import pandas as pd
        except ImportError:
            return {"success": False, "error": "pandas not installed"}
        
        try:
            brands = self.get_all_brands()
            
            # Convert to DataFrame
            df_data = []
            for brand in brands:
                df_data.append({
                    'brand_name': brand['brand_name'],
                    'cruelty_free': brand['is_cruelty_free'],
                    'parent_company': brand['parent_company'] or 'Unknown',
                    'certification': brand['sources'][0] if brand['sources'] else None,
                    'category': 'Unknown',  # Not stored in DB currently
                    'price_tier': 'Unknown'  # Not stored in DB currently
                })
            
            df = pd.DataFrame(df_data)
            df.to_csv(csv_path, index=False)
            
            return {
                "success": True,
                "exported_count": len(df),
                "file_path": csv_path
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing BrandDatabase")
    print("="*60 + "\n")
    
    # Initialize database
    db = BrandDatabase("test_brands.db")
    
    # Test 1: Check existing brand
    print("Test 1: Check existing brand")
    result = db.check_brand("Fenty Beauty")
    print(f"Found: {result.get('found')}")
    if result.get('found'):
        print(f"  Brand: {result['brand_name']}")
        print(f"  Cruelty-Free: {result['is_cruelty_free']}")
        print(f"  Confidence: {result['confidence']:.2f}")
    print()
    
    # Test 2: Check non-existent brand
    print("Test 2: Check non-existent brand")
    result = db.check_brand("Unknown Brand XYZ")
    print(f"Found: {result.get('found')}")
    print()
    
    # Test 3: Save new brand
    print("Test 3: Save new brand")
    result = db.save_brand(
        brand_name="Test Brand",
        is_cruelty_free=True,
        parent_company="Test Corp",
        explanation="Test explanation",
        sources=["Test Source 1", "Test Source 2"],
        confidence=0.85
    )
    print(f"Success: {result['success']}")
    print()
    
    # Test 4: Get database stats
    print("Test 4: Database statistics")
    stats = db.get_database_stats()
    print(f"Total brands: {stats['total_brands']}")
    print(f"Cruelty-free: {stats['cruelty_free_count']} ({stats['cruelty_free_percentage']}%)")
    print()
    
    # Test 5: Search brands
    print("Test 5: Search for brands with 'e.l.f'")
    results = db.search_brands("elf")
    print(f"Found {len(results)} results")
    for brand in results:
        print(f"  - {brand['brand_name']}")
    print()
    
    print("✅ All database tests completed!")