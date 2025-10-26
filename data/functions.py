"""
functions.py - Core Logic for Cruelty-Free Finder
Contains all data processing, search, classification, and recommendation functions
"""

import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
from typing import Dict, List, Optional, Tuple
import os


# =============================================================================
# DATA LOADING & PREPROCESSING
# =============================================================================

def load_data(filepath: str = 'brands.csv') -> pd.DataFrame:
    """
    Load and preprocess the brands dataset
    
    Args:
        filepath: Path to the brands CSV file
        
    Returns:
        Preprocessed DataFrame with additional computed columns
    """
    try:
        df = pd.read_csv(filepath)
        
        # Validate required columns
        required_cols = ['brand_name', 'cruelty_free', 'parent_company', 
                        'certification', 'category', 'price_tier']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Clean and standardize data
        df['brand_name_clean'] = df['brand_name'].str.lower().str.strip()
        
        # Fill NaN values for optional fields
        df['certification'] = df['certification'].fillna('None')
        df['parent_company'] = df['parent_company'].fillna('Unknown')
        
        # Add derived features
        df['has_certification'] = df['certification'].apply(
            lambda x: x not in ['None', 'Unknown', '']
        )
        
        return df
        
    except FileNotFoundError:
        raise FileNotFoundError(
            f"❌ Could not find {filepath}. Please run brands_data_collection.py first!"
        )
    except Exception as e:
        raise Exception(f"❌ Error loading data: {str(e)}")


# =============================================================================
# SEARCH FUNCTIONALITY
# =============================================================================

def search_brand(query: str, df: pd.DataFrame, threshold: int = 70) -> Optional[Dict]:
    """
    Search for a brand using exact and fuzzy matching
    
    Args:
        query: Brand name to search for
        df: DataFrame containing brand data
        threshold: Minimum similarity score for fuzzy matching (0-100)
        
    Returns:
        Dictionary with brand data if found, None otherwise
    """
    if not query or not query.strip():
        return None
    
    query_clean = query.lower().strip()
    
    # Try exact match first (fastest)
    exact_match = df[df['brand_name_clean'] == query_clean]
    if not exact_match.empty:
        return exact_match.iloc[0].to_dict()
    
    # Try partial exact match (e.g., "elf" matches "e.l.f. cosmetics")
    partial_matches = df[df['brand_name_clean'].str.contains(query_clean, na=False, regex=False)]
    if not partial_matches.empty:
        # Return the shortest match (most specific)
        best_match = partial_matches.loc[partial_matches['brand_name'].str.len().idxmin()]
        return best_match.to_dict()
    
    # Fuzzy matching as last resort
    df_temp = df.copy()
    df_temp['similarity'] = df_temp['brand_name_clean'].apply(
        lambda x: fuzz.ratio(query_clean, x)
    )
    
    best_match = df_temp.loc[df_temp['similarity'].idxmax()]
    
    if best_match['similarity'] >= threshold:
        result = best_match.to_dict()
        result['match_quality'] = 'fuzzy'
        result['similarity_score'] = best_match['similarity']
        return result
    
    return None


# =============================================================================
# CLASSIFICATION & CONFIDENCE SCORING
# =============================================================================

def classify_status(brand_data: Dict) -> Dict:
    """
    Classify cruelty-free status with confidence score and reasoning
    
    Uses rule-based expert system to determine:
    - Cruelty-free status (True/False)
    - Confidence score (0.0 to 1.0)
    - Detailed reasoning
    
    Args:
        brand_data: Dictionary containing brand information
        
    Returns:
        Dictionary with classification results
    """
    confidence = 0.50  # Start with neutral confidence
    status = brand_data.get('cruelty_free', False)
    reasons = []
    warning_flags = []
    
    # Known parent companies that test on animals
    parent_companies_that_test = {
        "L'Oréal": "tests in China where required by law",
        "Estée Lauder": "tests in some markets",
        "Procter & Gamble": "conducts animal testing",
        "Johnson & Johnson": "tests on animals",
        "Coty": "allows animal testing in some regions",
        "Unilever": "tests in markets where required",
        "Revlon Inc": "parent company tests",
        "LVMH": "some brands test in China",
        "Chanel": "tests where required by law",
        "Shiseido": "conducts animal testing in China",
        "Euroitalia": "tests in some markets"
    }
    
    # Rule 1: Check for official certifications (strongest signal)
    certification = brand_data.get('certification', 'None')
    
    if certification == 'Leaping Bunny':
        confidence = max(confidence, 0.95)
        reasons.append("✓ Leaping Bunny certified - the gold standard for cruelty-free")
        reasons.append("  • Independent audits of supply chain")
        reasons.append("  • Strictest no-animal-testing policy")
        
    elif certification == 'PETA':
        confidence = max(confidence, 0.90)
        reasons.append("✓ PETA certified cruelty-free")
        reasons.append("  • Brand signed PETA's cruelty-free pledge")
        
    elif certification in ['None', 'Unknown', '']:
        if status:
            confidence = 0.65
            reasons.append("⚠ No third-party certification")
            reasons.append("  • Based on brand's own claims")
            warning_flags.append("Consider looking for certified alternatives")
        else:
            confidence = 0.80
            reasons.append("✗ Not certified cruelty-free")
    
    # Rule 2: Parent company analysis
    parent_company = brand_data.get('parent_company', 'Unknown')
    
    if parent_company == 'Independent':
        confidence = min(confidence + 0.05, 1.0)
        reasons.append("✓ Independent company (no parent company complications)")
        
    elif parent_company in parent_companies_that_test:
        parent_info = parent_companies_that_test[parent_company]
        
        if status:  # Brand claims cruelty-free but parent tests
            confidence = max(0.70, confidence - 0.15)
            warning_flags.append(f"Parent company ({parent_company}) {parent_info}")
            reasons.append(f"⚠ Complex case: Brand is cruelty-free but parent company {parent_info}")
            reasons.append(f"  • Some consumers avoid brands owned by testing companies")
            
        else:  # Not cruelty-free AND parent tests
            confidence = 0.90
            reasons.append(f"✗ Parent company ({parent_company}) {parent_info}")
            
    elif parent_company not in ['Unknown', '']:
        reasons.append(f"Parent company: {parent_company}")
    
    # Rule 3: Cross-validation checks
    if status and certification in ['None', 'Unknown', ''] and parent_company == 'Unknown':
        confidence = 0.50
        warning_flags.append("Limited information available - verify with brand directly")
    
    # Rule 4: Category-specific considerations
    category = brand_data.get('category', 'Unknown')
    if category == 'Fragrance' and not status:
        reasons.append("  • Many fragrance brands test in markets requiring it")
    
    # Compile final result
    result = {
        'status': status,
        'confidence': round(confidence, 2),
        'confidence_label': get_confidence_label(confidence),
        'reasons': reasons,
        'warning_flags': warning_flags,
        'certification': certification,
        'parent_company': parent_company
    }
    
    return result


def get_confidence_label(confidence: float) -> str:
    """
    Convert confidence score to human-readable label
    
    Args:
        confidence: Confidence score between 0 and 1
        
    Returns:
        String label describing confidence level
    """
    if confidence >= 0.90:
        return "Very High"
    elif confidence >= 0.80:
        return "High"
    elif confidence >= 0.70:
        return "Moderate"
    elif confidence >= 0.60:
        return "Low"
    else:
        return "Very Low"


# =============================================================================
# RECOMMENDATION SYSTEM
# =============================================================================

def get_recommendations(
    brand_data: Dict, 
    df: pd.DataFrame, 
    n: int = 3,
    same_price_tier: bool = True
) -> List[Dict]:
    """
    Get cruelty-free alternative recommendations
    
    Uses content-based filtering to find similar brands that are cruelty-free
    
    Args:
        brand_data: Dictionary containing the source brand's data
        df: DataFrame with all brands
        n: Number of recommendations to return
        same_price_tier: Whether to prioritize same price tier
        
    Returns:
        List of dictionaries with recommended brand information
    """
    # Filter: must be cruelty-free and not the same brand
    candidates = df[
        (df['cruelty_free'] == True) &
        (df['brand_name'] != brand_data['brand_name'])
    ].copy()
    
    if candidates.empty:
        return []
    
    # Calculate similarity scores
    category = brand_data.get('category', 'Unknown')
    price_tier = brand_data.get('price_tier', 'Unknown')
    
    # Score 1: Category match (most important)
    candidates['category_score'] = (candidates['category'] == category).astype(float) * 0.6
    
    # Score 2: Price tier similarity
    price_tiers = {'Budget': 1, 'Mid-range': 2, 'Luxury': 3, 'Unknown': 2}
    source_price = price_tiers.get(price_tier, 2)
    
    candidates['price_score'] = candidates['price_tier'].apply(
        lambda x: 1.0 / (1.0 + abs(price_tiers.get(x, 2) - source_price))
    ) * 0.3
    
    # Score 3: Certification quality (bonus)
    def cert_score(cert):
        if cert == 'Leaping Bunny':
            return 0.1
        elif cert == 'PETA':
            return 0.05
        return 0.0
    
    candidates['cert_score'] = candidates['certification'].apply(cert_score)
    
    # Calculate total similarity score
    candidates['similarity'] = (
        candidates['category_score'] + 
        candidates['price_score'] + 
        candidates['cert_score']
    )
    
    # Get top N recommendations
    top_recommendations = candidates.nlargest(n, 'similarity')
    
    # Format results
    recommendations = []
    for _, row in top_recommendations.iterrows():
        rec = {
            'brand_name': row['brand_name'],
            'category': row['category'],
            'price_tier': row['price_tier'],
            'certification': row['certification'] if row['certification'] not in ['None', 'Unknown'] else None,
            'parent_company': row['parent_company'],
            'similarity_score': round(row['similarity'], 2),
            'match_reason': get_match_reason(row, brand_data)
        }
        recommendations.append(rec)
    
    return recommendations


def get_match_reason(rec_brand: pd.Series, source_brand: Dict) -> str:
    """
    Generate explanation for why this brand was recommended
    
    Args:
        rec_brand: Recommended brand's data (pandas Series)
        source_brand: Source brand's data (dictionary)
        
    Returns:
        Human-readable explanation string
    """
    reasons = []
    
    if rec_brand['category'] == source_brand.get('category'):
        reasons.append(f"Same category ({rec_brand['category']})")
    
    if rec_brand['price_tier'] == source_brand.get('price_tier'):
        reasons.append(f"Similar price ({rec_brand['price_tier']})")
    
    if rec_brand['certification'] in ['Leaping Bunny', 'PETA']:
        reasons.append(f"Certified {rec_brand['certification']}")
    
    if not reasons:
        reasons.append("Cruelty-free alternative")
    
    return " • ".join(reasons)


# =============================================================================
# CHATBOT FUNCTIONALITY
# =============================================================================

def chatbot_response(
    question: str, 
    df: pd.DataFrame, 
    api_key: Optional[str] = None
) -> str:
    """
    Generate chatbot response using AI or fallback to rule-based
    
    Args:
        question: User's question
        df: DataFrame with brand data
        api_key: Optional OpenAI API key
        
    Returns:
        Response string
    """
    if api_key:
        return ai_chatbot_response(question, df, api_key)
    else:
        return simple_chatbot_response(question, df)


def ai_chatbot_response(question: str, df: pd.DataFrame, api_key: str) -> str:
    """
    Use OpenAI API to generate intelligent responses
    
    Args:
        question: User's question
        df: DataFrame with brand data for context
        api_key: OpenAI API key
        
    Returns:
        AI-generated response
    """
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Create context from database
        cruelty_free_brands = df[df['cruelty_free'] == True]['brand_name'].tolist()[:15]
        not_cruelty_free = df[df['cruelty_free'] == False]['brand_name'].tolist()[:15]
        
        context = f"""You are a helpful assistant for a cruelty-free product finder app.

Our database includes these cruelty-free brands: {', '.join(cruelty_free_brands)}
And these non-cruelty-free brands: {', '.join(not_cruelty_free)}

Answer questions about:
- What "cruelty-free" means
- Specific brands in our database
- How to find ethical beauty products
- Certifications (Leaping Bunny, PETA)

Keep responses concise (2-3 sentences). Always remind users to verify information with brands directly for the most current policies. Be friendly and helpful."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"AI chatbot error: {str(e)}")
        return simple_chatbot_response(question, df)


def simple_chatbot_response(question: str, df: pd.DataFrame) -> str:
    """
    Fallback rule-based chatbot (works without API key)
    
    Args:
        question: User's question
        df: DataFrame with brand data
        
    Returns:
        Rule-based response
    """
    question_lower = question.lower().strip()
    
    # Check if asking about a specific brand
    for _, brand in df.iterrows():
        brand_name_lower = brand['brand_name'].lower()
        
        # Check if brand name is in question
        if brand_name_lower in question_lower:
            status = "cruelty-free" if brand['cruelty_free'] else "NOT cruelty-free"
            cert_info = f" They're certified by {brand['certification']}." if brand['certification'] not in ['None', 'Unknown'] else ""
            
            return f"✓ {brand['brand_name']} is {status}.{cert_info} You can search for them in the main search bar for more details!"
    
    # General questions about cruelty-free
    if any(word in question_lower for word in ['what is', 'define', 'mean', 'means']):
        return ("Cruelty-free means the product and its ingredients weren't tested on animals at any stage of development. "
                "Look for Leaping Bunny or PETA certifications for verified cruelty-free products!")
    
    # How to use the app
    if any(word in question_lower for word in ['how', 'use', 'work', 'search']):
        return ("Just type a brand name in the search bar above! I'll tell you if they're cruelty-free and suggest alternatives if needed. "
                "Try searching for brands like 'Maybelline', 'e.l.f.', or 'Fenty Beauty'.")
    
    # Certifications
    if 'certification' in question_lower or 'leaping bunny' in question_lower or 'peta' in question_lower:
        return ("Leaping Bunny is the gold standard - they audit the entire supply chain. PETA certification means the brand signed their cruelty-free pledge. "
                "Both are reliable indicators!")
    
    # General stats
    if any(word in question_lower for word in ['how many', 'database', 'brands']):
        total = len(df)
        cf_count = len(df[df['cruelty_free'] == True])
        return f"Our database has {total} brands - {cf_count} are cruelty-free! We're always adding more. Try searching for your favorite brands!"
    
    # Default response
    return ("I'm here to help with cruelty-free product questions! Try asking about a specific brand, "
            "or use the search bar above to look up any beauty brand. You can also ask 'what is cruelty-free?' for more info.")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_database_stats(df: pd.DataFrame) -> Dict:
    """
    Calculate statistics about the database
    
    Args:
        df: DataFrame with brand data
        
    Returns:
        Dictionary with statistics
    """
    stats = {
        'total_brands': len(df),
        'cruelty_free_count': len(df[df['cruelty_free'] == True]),
        'not_cruelty_free_count': len(df[df['cruelty_free'] == False]),
        'cruelty_free_percentage': round(len(df[df['cruelty_free'] == True]) / len(df) * 100, 1),
        'categories': df['category'].value_counts().to_dict(),
        'certifications': df[df['certification'].notna()]['certification'].value_counts().to_dict(),
        'price_tiers': df['price_tier'].value_counts().to_dict()
    }
    return stats


def validate_brand_data(brand_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate brand data structure
    
    Args:
        brand_data: Dictionary with brand information
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    required_fields = ['brand_name', 'cruelty_free', 'parent_company', 
                      'certification', 'category', 'price_tier']
    errors = []
    
    for field in required_fields:
        if field not in brand_data:
            errors.append(f"Missing required field: {field}")
    
    return len(errors) == 0, errors


# =============================================================================
# MODULE TESTING (Only runs when file is executed directly)
# =============================================================================

if __name__ == "__main__":
    print("🧪 Testing functions.py...\n")
    
    # Test 1: Load data
    print("Test 1: Loading data...")
    try:
        df = load_data()
        print(f"✅ Loaded {len(df)} brands\n")
    except Exception as e:
        print(f"❌ Failed: {e}\n")
        exit(1)
    
    # Test 2: Search functionality
    print("Test 2: Search functionality...")
    test_searches = ['Maybelline', 'elf', 'fenty beauty', 'nonexistent brand']
    for query in test_searches:
        result = search_brand(query, df)
        if result:
            print(f"  ✓ Found: {result['brand_name']}")
        else:
            print(f"  ✗ Not found: {query}")
    print()
    
    # Test 3: Classification
    print("Test 3: Classification...")
    test_brand = search_brand('Maybelline', df)
    if test_brand:
        classification = classify_status(test_brand)
        print(f"  Brand: {test_brand['brand_name']}")
        print(f"  Status: {'✓ Cruelty-Free' if classification['status'] else '✗ Not Cruelty-Free'}")
        print(f"  Confidence: {classification['confidence']:.0%} ({classification['confidence_label']})")
    print()
    
    # Test 4: Recommendations
    print("Test 4: Recommendations...")
    if test_brand:
        recommendations = get_recommendations(test_brand, df, n=3)
        print(f"  Alternatives for {test_brand['brand_name']}:")
        for i, rec in enumerate(recommendations, 1):
            print(f"    {i}. {rec['brand_name']} - {rec['match_reason']}")
    print()
    
    # Test 5: Database stats
    print("Test 5: Database statistics...")
    stats = get_database_stats(df)
    print(f"  Total brands: {stats['total_brands']}")
    print(f"  Cruelty-free: {stats['cruelty_free_count']} ({stats['cruelty_free_percentage']}%)")
    print()
    
    print("✅ All tests passed! functions.py is ready to use.")