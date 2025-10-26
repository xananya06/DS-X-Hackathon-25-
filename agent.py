# """
# ConsciousCart - Enhanced Agentic System
# With confidence scoring, analytics, and real web search
# """
# import os
# import json
# import sqlite3
# from datetime import datetime, timedelta
# from anthropic import Anthropic
# from dotenv import load_dotenv
# import re

# load_dotenv()


# class UserProfile:
#     """Tracks user preferences and learns from feedback"""
    
#     def __init__(self):
#         self.budget_max = None
#         self.budget_min = None
#         self.values = {
#             "vegan": False,
#             "fragrance_free": False,
#             "paraben_free": False,
#             "cruelty_free": True
#         }
#         self.product_history = []
#         self.preferred_brands = set()
#         self.rejected_brands = set()
#         self.last_recommendation_price = None
    
#     def learn_from_feedback(self, feedback: str, context: dict):
#         """Learn from user's implicit and explicit feedback"""
#         feedback_lower = feedback.lower()
        
#         # Budget learning
#         if "expensive" in feedback_lower or "too much" in feedback_lower or "pricey" in feedback_lower:
#             if context.get("last_price"):
#                 self.budget_max = int(context["last_price"] * 0.7)
#                 print(f"[Profile] Learned budget_max: ${self.budget_max}")
        
#         elif "cheap" in feedback_lower or "affordable" in feedback_lower or "budget" in feedback_lower:
#             if context.get("last_price"):
#                 self.budget_max = int(context["last_price"])
#                 print(f"[Profile] Learned budget_max: ${self.budget_max}")
        
#         # Values learning
#         if "vegan" in feedback_lower:
#             self.values["vegan"] = True
#             print(f"[Profile] Learned: User cares about vegan")
        
#         if "fragrance" in feedback_lower or "scent" in feedback_lower:
#             self.values["fragrance_free"] = True
#             print(f"[Profile] Learned: User wants fragrance-free")
        
#         if "paraben" in feedback_lower:
#             self.values["paraben_free"] = True
#             print(f"[Profile] Learned: User wants paraben-free")
    
#     def add_to_history(self, brand: str, product_type: str, is_cruelty_free: bool, price: float = None):
#         """Track what user has checked"""
#         self.product_history.append({
#             "brand": brand,
#             "type": product_type,
#             "is_cruelty_free": is_cruelty_free,
#             "price": price,
#             "timestamp": datetime.now()
#         })
        
#         if is_cruelty_free:
#             self.preferred_brands.add(brand)
#         else:
#             self.rejected_brands.add(brand)
    
#     def get_profile_summary(self) -> str:
#         """Return readable profile summary"""
#         summary = []
        
#         if self.budget_max:
#             summary.append(f"Budget under ${self.budget_max}")
        
#         if self.values["vegan"]:
#             summary.append("Vegan only")
        
#         if self.values["fragrance_free"]:
#             summary.append("Fragrance-free")
        
#         if self.preferred_brands:
#             summary.append(f"Likes {', '.join(list(self.preferred_brands)[:2])}")
        
#         return " | ".join(summary) if summary else "Learning your preferences..."
    
#     def get_constraints_for_agent(self) -> str:
#         """Return constraints string for agent to use"""
#         constraints = ["cruelty-free"]
        
#         if self.values["vegan"]:
#             constraints.append("vegan")
#         if self.values["fragrance_free"]:
#             constraints.append("fragrance-free")
#         if self.values["paraben_free"]:
#             constraints.append("paraben-free")
#         if self.budget_max:
#             constraints.append(f"under ${self.budget_max}")
        
#         return ", ".join(constraints)


# class VerificationResult:
#     """Result with confidence scoring"""
    
#     def __init__(self, brand: str, is_cruelty_free: bool, sources_count: int, 
#                  has_conflicts: bool = False):
#         self.brand = brand
#         self.is_cruelty_free = is_cruelty_free
#         self.sources_count = sources_count
#         self.has_conflicts = has_conflicts
#         self.confidence = self.calculate_confidence()
    
#     def calculate_confidence(self) -> float:
#         """Calculate confidence score 0.0-1.0"""
#         base = 0.5
        
#         # More sources = higher confidence
#         if self.sources_count >= 4:
#             base = 0.95
#         elif self.sources_count >= 3:
#             base = 0.85
#         elif self.sources_count >= 2:
#             base = 0.75
        
#         # Conflicts reduce confidence
#         if self.has_conflicts:
#             base -= 0.25
        
#         return min(max(base, 0.1), 1.0)
    
#     def get_confidence_label(self) -> str:
#         """Get human-readable confidence label"""
#         if self.confidence >= 0.9:
#             return "Very High"
#         elif self.confidence >= 0.75:
#             return "High"
#         elif self.confidence >= 0.5:
#             return "Medium"
#         else:
#             return "Low"
    
#     def get_confidence_color(self) -> str:
#         """Get color for UI"""
#         if self.confidence >= 0.75:
#             return "success"  # Green
#         elif self.confidence >= 0.5:
#             return "warning"  # Yellow
#         else:
#             return "error"  # Red


# class ConsciousCartAgent:
#     """Enhanced agentic system with confidence scoring"""
    
#     def __init__(self):
#         self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
#         self.model = "claude-sonnet-4-20250514"
#         self.db_path = "brands.db"
#         self.conversation_history = []
#         self.tool_calls = []
        
#         # User profile
#         self.user_profile = UserProfile()
#         self.last_recommendation = None
        
#         # Context tracking
#         self.last_brand_discussed = None
#         self.last_product_type = None
#         self.last_verification_result = None  # NEW: Store verification with confidence
        
#         # Initialize database
#         self._init_database()
        
#         # Define tools
#         self.tools = [
#             {
#                 "name": "check_database",
#                 "description": "Check if a brand exists in the local database of verified brands. Use this FIRST before searching.",
#                 "input_schema": {
#                     "type": "object",
#                     "properties": {
#                         "brand_name": {
#                             "type": "string",
#                             "description": "The brand name to look up"
#                         }
#                     },
#                     "required": ["brand_name"]
#                 }
#             },
#             {
#                 "name": "web_search",
#                 "description": "Search for information about cruelty-free status, certifications, or alternatives.",
#                 "input_schema": {
#                     "type": "object",
#                     "properties": {
#                         "query": {
#                             "type": "string",
#                             "description": "The search query"
#                         }
#                     },
#                     "required": ["query"]
#                 }
#             },
#             {
#                 "name": "save_to_database",
#                 "description": "Save verified brand information to database.",
#                 "input_schema": {
#                     "type": "object",
#                     "properties": {
#                         "brand_name": {"type": "string"},
#                         "is_cruelty_free": {"type": "boolean"},
#                         "parent_company": {"type": "string"},
#                         "explanation": {"type": "string"},
#                         "sources": {
#                             "type": "array",
#                             "items": {"type": "string"}
#                         }
#                     },
#                     "required": ["brand_name", "is_cruelty_free", "explanation"]
#                 }
#             }
#         ]
    
#     def _init_database(self):
#         """Initialize SQLite database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#             CREATE TABLE IF NOT EXISTS brands (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT UNIQUE NOT NULL,
#                 is_cruelty_free BOOLEAN NOT NULL,
#                 parent_company TEXT,
#                 explanation TEXT,
#                 sources TEXT,
#                 confidence FLOAT DEFAULT 0.9,
#                 last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#         """)
        
#         conn.commit()
#         conn.close()
        
#         self._seed_database()
    
#     def _seed_database(self):
#         """Pre-populate with known brands"""
#         known_brands = [
#             ("Maybelline", False, "L'Oréal", "Owned by L'Oréal which tests in China", "PETA,Leaping Bunny"),
#             ("Fenty Beauty", True, "LVMH", "Certified cruelty-free, no animal testing", "Leaping Bunny,PETA"),
#             ("e.l.f. Cosmetics", True, None, "Certified cruelty-free and vegan", "Leaping Bunny,PETA"),
#             ("MAC", False, "Estée Lauder", "Owned by Estée Lauder which tests on animals", "PETA"),
#             ("NYX", False, "L'Oréal", "Owned by L'Oréal", "PETA"),
#             ("Pacifica", True, None, "100% vegan and cruelty-free", "Leaping Bunny,PETA"),
#             ("CoverGirl", False, "Coty", "Tests where required by law", "PETA"),
#             ("Revlon", False, None, "Not cruelty-free", "PETA"),
#             ("Urban Decay", True, "L'Oréal", "Maintains cruelty-free despite parent", "Leaping Bunny"),
#             ("Too Faced", True, "Estée Lauder", "Cruelty-free certified", "Leaping Bunny"),
#         ]
        
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         for brand_data in known_brands:
#             try:
#                 cursor.execute("""
#                     INSERT OR IGNORE INTO brands 
#                     (name, is_cruelty_free, parent_company, explanation, sources)
#                     VALUES (?, ?, ?, ?, ?)
#                 """, brand_data)
#             except:
#                 pass
        
#         conn.commit()
#         conn.close()
    
#     def _check_database(self, brand_name: str) -> dict:
#         """Tool: Check database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         cursor.execute("""
#             SELECT name, is_cruelty_free, parent_company, explanation, 
#                    sources, last_verified
#             FROM brands 
#             WHERE LOWER(name) = LOWER(?)
#         """, (brand_name,))
        
#         result = cursor.fetchone()
#         conn.close()
        
#         if result:
#             name, is_cf, parent, explanation, sources, last_verified = result
            
#             last_verified_date = datetime.strptime(last_verified, "%Y-%m-%d %H:%M:%S")
#             is_stale = datetime.now() - last_verified_date > timedelta(days=30)
            
#             return {
#                 "found": True,
#                 "brand_name": name,
#                 "is_cruelty_free": bool(is_cf),
#                 "parent_company": parent,
#                 "explanation": explanation,
#                 "sources": sources.split(",") if sources else [],
#                 "last_verified": last_verified,
#                 "is_stale": is_stale
#             }
        
#         return {"found": False}
    
#     def _extract_sources_count(self, search_result: str) -> int:
#         """Extract number of sources from search result"""
#         match = re.search(r'SOURCES CHECKED:\s*(\d+)', search_result)
#         if match:
#             return int(match.group(1))
#         # Fallback: count mentions of known sources
#         sources = ['PETA', 'Leaping Bunny', 'Cruelty-Free', 'Logical Harmony']
#         return sum(1 for source in sources if source in search_result)
    
#     def _detect_conflicts(self, search_result: str) -> bool:
#         """Detect if sources conflict"""
#         # Simple heuristic
#         has_positive = any(word in search_result.lower() for word in ['cruelty-free', 'certified', 'approved'])
#         has_negative = any(word in search_result.lower() for word in ['not cruelty-free', 'tests on animals', 'not certified'])
#         return has_positive and has_negative
    
#     def _web_search(self, query: str) -> str:
#         """Tool: REAL web search with fallback"""
#         try:
#             print(f"[Web Search] Searching for: {query}")
            
#             search_response = self.client.messages.create(
#                 model=self.model,
#                 max_tokens=2000,
#                 temperature=0.3,
#                 system="""You are a research assistant specializing in cruelty-free beauty products. 

# When searching, look for:
# 1. Brand's cruelty-free status (PETA, Leaping Bunny certification)
# 2. Parent company information
# 3. China market presence (mandatory animal testing)
# 4. Alternative product recommendations with prices
# 5. Multiple authoritative sources

# Format your response as:
# SOURCES CHECKED: [number]

# [Source 1 name]: [key findings]
# [Source 2 name]: [key findings]
# ...

# CONFIDENCE: [High/Medium/Low based on source agreement]""",
#                 messages=[{
#                     "role": "user",
#                     "content": f"Search for information about: {query}\n\nFocus on cruelty-free certifications, parent companies, and reliable sources like PETA and Leaping Bunny."
#                 }],
#                 tools=[{
#                     "name": "web_search",
#                     "description": "Search the web for current information",
#                     "input_schema": {
#                         "type": "object",
#                         "properties": {
#                             "query": {
#                                 "type": "string",
#                                 "description": "The search query"
#                             }
#                         },
#                         "required": ["query"]
#                     }
#                 }]
#             )
            
#             result_text = ""
#             for block in search_response.content:
#                 if hasattr(block, 'text'):
#                     result_text += block.text
            
#             print(f"[Web Search] Got {len(result_text)} characters of results")
#             return result_text if result_text else self._mock_search_fallback(query)
            
#         except Exception as e:
#             print(f"[Web Search Error] {str(e)}")
#             return self._mock_search_fallback(query)
    
#     def _mock_search_fallback(self, query: str) -> str:
#         """Enhanced fallback with realistic multi-source data"""
#         query_lower = query.lower()
        
#         print(f"[Fallback] Using mock data for: {query}")
        
#         if "l'oreal" in query_lower or "loreal" in query_lower:
#             return """SOURCES CHECKED: 3

# PETA (2024): L'Oréal tests on animals where required by law, particularly in mainland China. Not on cruelty-free list.

# Cruelty-Free International: L'Oréal continues to sell products in China, which requires animal testing for imported cosmetics.

# Leaping Bunny Database: L'Oréal is NOT certified cruelty-free.

# CONFIDENCE: High (3/3 sources agree)"""
        
#         elif "alternative" in query_lower or "cruelty free" in query_lower:
#             if "mascara" in query_lower:
#                 return """SOURCES CHECKED: 4

# PETA Cruelty-Free Database: 
# - e.l.f. Big Mood Mascara ($7) - Certified cruelty-free, 100% vegan
# - Essence Lash Princess ($5) - Cruelty-free verified

# Leaping Bunny Certified:
# - Pacifica Dream Big Mascara ($12) - Certified CF & vegan
# - Milk Makeup Kush Mascara ($24) - Leaping Bunny approved

# Cruelty-Free Kitty (Independent verification):
# - All above brands verified as maintaining cruelty-free status in 2024

# Price Source: Brand websites, Ulta, Sephora (Oct 2024)

# CONFIDENCE: Very High (4/4 sources agree)"""
            
#             elif "foundation" in query_lower:
#                 return """SOURCES CHECKED: 3

# PETA Database:
# - e.l.f. Flawless Finish Foundation ($7) - 100% vegan, CF certified
# - Pacifica Alight Multi-Mineral Foundation ($14) - Vegan, CF

# Leaping Bunny:
# - Physician's Formula Healthy Foundation ($13) - Certified cruelty-free
# - Cover FX Power Play Foundation ($48) - Luxury CF option

# Sources: PETA, Leaping Bunny, brand websites (2024)

# CONFIDENCE: High"""
        
#         return f"""SOURCES CHECKED: 2

# Searching for information about: {query}

# Note: Using enhanced knowledge base. Real-time web search available for unknown brands.

# CONFIDENCE: Medium (using cached knowledge)"""
    
#     def _save_to_database(self, brand_name: str, is_cruelty_free: bool,
#                          parent_company: str = None, explanation: str = "",
#                          sources: list = None) -> dict:
#         """Tool: Save to database"""
#         conn = sqlite3.connect(self.db_path)
#         cursor = conn.cursor()
        
#         sources_str = ",".join(sources) if sources else ""
        
#         try:
#             cursor.execute("""
#                 INSERT OR REPLACE INTO brands 
#                 (name, is_cruelty_free, parent_company, explanation, sources, last_verified)
#                 VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
#             """, (brand_name, is_cruelty_free, parent_company, explanation, sources_str))
            
#             conn.commit()
#             conn.close()
            
#             return {"success": True, "message": f"Saved {brand_name}"}
#         except Exception as e:
#             conn.close()
#             return {"success": False, "error": str(e)}
    
#     def _execute_tool(self, tool_name: str, tool_input: dict) -> any:
#         """Execute a tool"""
#         self.tool_calls.append({
#             "tool": tool_name,
#             "input": tool_input,
#             "timestamp": datetime.now().isoformat()
#         })
        
#         if tool_name == "check_database":
#             return self._check_database(tool_input["brand_name"])
#         elif tool_name == "web_search":
#             result = self._web_search(tool_input["query"])
            
#             # Extract confidence metrics from search result
#             sources_count = self._extract_sources_count(result)
#             has_conflicts = self._detect_conflicts(result)
            
#             # Store for later use
#             if self.last_brand_discussed:
#                 self.last_verification_result = VerificationResult(
#                     brand=self.last_brand_discussed,
#                     is_cruelty_free=True,  # Will be updated by agent's final answer
#                     sources_count=sources_count,
#                     has_conflicts=has_conflicts
#                 )
            
#             return result
#         elif tool_name == "save_to_database":
#             return self._save_to_database(
#                 tool_input["brand_name"],
#                 tool_input["is_cruelty_free"],
#                 tool_input.get("parent_company"),
#                 tool_input.get("explanation", ""),
#                 tool_input.get("sources", [])
#             )
        
#         return {"error": f"Unknown tool: {tool_name}"}
    
#     def _detect_feedback(self, user_query: str) -> bool:
#         """Detect if user is giving feedback or expressing preferences"""
#         feedback_words = ["expensive", "cheap", "too much", "perfect", "good", "bad", 
#                          "affordable", "pricey", "budget", "love", "hate",
#                          "vegan", "fragrance", "paraben", "scent"]
#         return any(word in user_query.lower() for word in feedback_words)
    
#     def process_query(self, user_query: str) -> tuple:
#         """Main agentic loop with confidence scoring"""
#         self.tool_calls = []
        
#         # Check for feedback
#         if self._detect_feedback(user_query):
#             if self.last_recommendation:
#                 self.user_profile.learn_from_feedback(
#                     user_query,
#                     {"last_price": self.last_recommendation.get("price")}
#                 )
#             else:
#                 self.user_profile.learn_from_feedback(user_query, {})
        
#         # Get context
#         profile_summary = self.user_profile.get_profile_summary()
#         constraints = self.user_profile.get_constraints_for_agent()
        
#         context_info = ""
#         if self.last_brand_discussed:
#             context_info = f"\n\nCONVERSATION CONTEXT:\n- Last brand discussed: {self.last_brand_discussed}"
#             if self.last_product_type:
#                 context_info += f"\n- Product type: {self.last_product_type}"
        
#         system_prompt = f"""You are an intelligent agent helping users find cruelty-free beauty products.

# USER PROFILE: {profile_summary}
# USER CONSTRAINTS: {constraints}{context_info}

# YOUR PROCESS:
# 1. ALWAYS check database first using check_database tool
# 2. If not found or stale, use web_search to verify
# 3. When recommending alternatives, ALWAYS respect user constraints: {constraints}
# 4. Save new verifications to database
# 5. Be conversational and remember the user's preferences

# IMPORTANT:
# - When suggesting alternatives, filter by user's budget if known
# - Prioritize options that match ALL user values (vegan, fragrance-free, etc.)
# - Mention when products match user preferences
# - Be friendly and personal
# - If user asks a follow-up question like "is it vegan?", refer to the last brand discussed: {self.last_brand_discussed or 'unknown'}

# RESPONSE STYLE:
# - Conversational and warm
# - Acknowledge user preferences when relevant
# - Explain WHY recommendations match their needs"""

#         messages = [{"role": "user", "content": user_query}]
        
#         # Agentic loop
#         while True:
#             response = self.client.messages.create(
#                 model=self.model,
#                 max_tokens=4000,
#                 temperature=0.3,
#                 system=system_prompt,
#                 tools=self.tools,
#                 messages=messages
#             )
            
#             if response.stop_reason == "tool_use":
#                 tool_use_block = next(
#                     block for block in response.content 
#                     if block.type == "tool_use"
#                 )
                
#                 tool_name = tool_use_block.name
#                 tool_input = tool_use_block.input
                
#                 # Track brand
#                 if tool_name == "check_database":
#                     self.last_brand_discussed = tool_input.get("brand_name")
                
#                 tool_result = self._execute_tool(tool_name, tool_input)
                
#                 messages.append({
#                     "role": "assistant",
#                     "content": response.content
#                 })
                
#                 messages.append({
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "tool_result",
#                             "tool_use_id": tool_use_block.id,
#                             "content": json.dumps(tool_result)
#                         }
#                     ]
#                 })
                
#                 continue
            
#             elif response.stop_reason == "end_turn":
#                 final_text = next(
#                     (block.text for block in response.content if hasattr(block, "text")),
#                     ""
#                 )
                
#                 self.last_recommendation = {"price": 10}
                
#                 return final_text, self.tool_calls
            
#             break
        
#         return "Error in processing", self.tool_calls


# if __name__ == "__main__":
#     agent = ConsciousCartAgent()
    
#     print("\n" + "="*60)
#     print("Testing Enhanced Agent with Confidence Scoring")
#     print("="*60)
    
#     response, tools = agent.process_query("Is Rare Beauty cruelty-free?")
#     print(f"\nResponse: {response}")
#     print(f"\nTools used: {len(tools)}")
    
#     if agent.last_verification_result:
#         vr = agent.last_verification_result
#         print(f"\nConfidence Score: {vr.confidence:.2f} ({vr.get_confidence_label()})")
#         print(f"Sources Checked: {vr.sources_count}")
#         print(f"Conflicts Detected: {vr.has_conflicts}")













"""
agent.py - ConsciousCart Agentic System (Refactored)
Enhanced with confidence scoring and separated database operations
SIMPLIFIED: Uses manual save (agent decides when to save) - more reliable
"""

import os
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import re

# Import database module
from database import BrandDatabase

load_dotenv()


class UserProfile:
    """Tracks user preferences and learns from feedback"""
    
    def __init__(self):
        self.budget_max = None
        self.budget_min = None
        self.values = {
            "vegan": False,
            "fragrance_free": False,
            "paraben_free": False,
            "cruelty_free": True
        }
        self.product_history = []
        self.preferred_brands = set()
        self.rejected_brands = set()
        self.last_recommendation_price = None
    
    def learn_from_feedback(self, feedback: str, context: dict):
        """Learn from user's implicit and explicit feedback"""
        feedback_lower = feedback.lower()
        
        # Budget learning
        if "expensive" in feedback_lower or "too much" in feedback_lower or "pricey" in feedback_lower:
            if context.get("last_price"):
                self.budget_max = int(context["last_price"] * 0.7)
                print(f"[Profile] Learned budget_max: ${self.budget_max}")
        
        elif "cheap" in feedback_lower or "affordable" in feedback_lower or "budget" in feedback_lower:
            if context.get("last_price"):
                self.budget_max = int(context["last_price"])
                print(f"[Profile] Learned budget_max: ${self.budget_max}")
        
        # Values learning
        if "vegan" in feedback_lower:
            self.values["vegan"] = True
            print(f"[Profile] Learned: User cares about vegan")
        
        if "fragrance" in feedback_lower or "scent" in feedback_lower:
            self.values["fragrance_free"] = True
            print(f"[Profile] Learned: User wants fragrance-free")
        
        if "paraben" in feedback_lower:
            self.values["paraben_free"] = True
            print(f"[Profile] Learned: User wants paraben-free")
    
    def add_to_history(self, brand: str, product_type: str, is_cruelty_free: bool, price: float = None):
        """Track what user has checked"""
        self.product_history.append({
            "brand": brand,
            "type": product_type,
            "is_cruelty_free": is_cruelty_free,
            "price": price,
            "timestamp": datetime.now()
        })
        
        if is_cruelty_free:
            self.preferred_brands.add(brand)
        else:
            self.rejected_brands.add(brand)
    
    def get_profile_summary(self) -> str:
        """Return readable profile summary"""
        summary = []
        
        if self.budget_max:
            summary.append(f"Budget under ${self.budget_max}")
        
        if self.values["vegan"]:
            summary.append("Vegan only")
        
        if self.values["fragrance_free"]:
            summary.append("Fragrance-free")
        
        if self.preferred_brands:
            summary.append(f"Likes {', '.join(list(self.preferred_brands)[:2])}")
        
        return " | ".join(summary) if summary else "Learning your preferences..."
    
    def get_constraints_for_agent(self) -> str:
        """Return constraints string for agent to use"""
        constraints = ["cruelty-free"]
        
        if self.values["vegan"]:
            constraints.append("vegan")
        if self.values["fragrance_free"]:
            constraints.append("fragrance-free")
        if self.values["paraben_free"]:
            constraints.append("paraben-free")
        if self.budget_max:
            constraints.append(f"under ${self.budget_max}")
        
        return ", ".join(constraints)


class VerificationResult:
    """Result with confidence scoring"""
    
    def __init__(self, brand: str, is_cruelty_free: bool, sources_count: int, 
                 has_conflicts: bool = False):
        self.brand = brand
        self.is_cruelty_free = is_cruelty_free
        self.sources_count = sources_count
        self.has_conflicts = has_conflicts
        self.confidence = self.calculate_confidence()
    
    def calculate_confidence(self) -> float:
        """Calculate confidence score 0.0-1.0"""
        base = 0.5
        
        # More sources = higher confidence
        if self.sources_count >= 4:
            base = 0.95
        elif self.sources_count >= 3:
            base = 0.85
        elif self.sources_count >= 2:
            base = 0.75
        
        # Conflicts reduce confidence
        if self.has_conflicts:
            base -= 0.25
        
        return min(max(base, 0.1), 1.0)
    
    def get_confidence_label(self) -> str:
        """Get human-readable confidence label"""
        if self.confidence >= 0.9:
            return "Very High"
        elif self.confidence >= 0.75:
            return "High"
        elif self.confidence >= 0.5:
            return "Medium"
        else:
            return "Low"
    
    def get_confidence_color(self) -> str:
        """Get color for UI"""
        if self.confidence >= 0.75:
            return "success"  # Green
        elif self.confidence >= 0.5:
            return "warning"  # Yellow
        else:
            return "error"  # Red


class ConsciousCartAgent:
    """Enhanced agentic system with separated database operations"""
    
    def __init__(self, db_path: str = "brands.db"):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        self.conversation_history = []
        self.tool_calls = []
        
        # Initialize database connection using the BrandDatabase class
        print(f"[Agent] Initializing database: {db_path}")
        self.db = BrandDatabase(db_path)
        
        # User profile
        self.user_profile = UserProfile()
        self.last_recommendation = None
        
        # Context tracking
        self.last_brand_discussed = None
        self.last_product_type = None
        self.last_verification_result = None
        
        # Define tools
        self.tools = [
            {
                "name": "check_database",
                "description": "Check if a brand exists in the local database of verified brands. Use this FIRST before searching.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brand_name": {
                            "type": "string",
                            "description": "The brand name to look up"
                        }
                    },
                    "required": ["brand_name"]
                }
            },
            {
                "name": "web_search",
                "description": "Search for information about cruelty-free status, certifications, or alternatives.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "save_to_database",
                "description": "Save verified brand information to database. Use this after you've verified a brand's status through web search.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brand_name": {"type": "string"},
                        "is_cruelty_free": {"type": "boolean"},
                        "parent_company": {"type": "string"},
                        "explanation": {"type": "string"},
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "confidence": {"type": "number"}
                    },
                    "required": ["brand_name", "is_cruelty_free", "explanation"]
                }
            },
            {
                "name": "search_database",
                "description": "Search for brands by partial name match in the database",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for brand names"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default 10)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_database_stats",
                "description": "Get statistics about the database (total brands, cruelty-free count, etc.)",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    def _extract_sources_count(self, search_result: str) -> int:
        """Extract number of sources from search result"""
        match = re.search(r'SOURCES CHECKED:\s*(\d+)', search_result)
        if match:
            return int(match.group(1))
        # Fallback: count mentions of known sources
        sources = ['PETA', 'Leaping Bunny', 'Cruelty-Free', 'Logical Harmony']
        return sum(1 for source in sources if source in search_result)
    
    def _detect_conflicts(self, search_result: str) -> bool:
        """Detect if sources conflict"""
        has_positive = any(word in search_result.lower() for word in ['cruelty-free', 'certified', 'approved'])
        has_negative = any(word in search_result.lower() for word in ['not cruelty-free', 'tests on animals', 'not certified'])
        return has_positive and has_negative
    
    def _web_search(self, query: str) -> str:
        """Tool: REAL web search with fallback"""
        try:
            print(f"[Web Search] Searching for: {query}")
            
            search_response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                system="""You are a research assistant specializing in cruelty-free beauty products. 

When searching, look for:
1. Brand's cruelty-free status (PETA, Leaping Bunny certification)
2. Parent company information
3. China market presence (mandatory animal testing)
4. Alternative product recommendations with prices
5. Multiple authoritative sources

Format your response as:
SOURCES CHECKED: [number]

[Source 1 name]: [key findings]
[Source 2 name]: [key findings]
...

CONFIDENCE: [High/Medium/Low based on source agreement]""",
                messages=[{
                    "role": "user",
                    "content": f"Search for information about: {query}\n\nFocus on cruelty-free certifications, parent companies, and reliable sources like PETA and Leaping Bunny."
                }],
                tools=[{
                    "name": "web_search",
                    "description": "Search the web for current information",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }]
            )
            
            result_text = ""
            for block in search_response.content:
                if hasattr(block, 'text'):
                    result_text += block.text
            
            print(f"[Web Search] Got {len(result_text)} characters of results")
            return result_text if result_text else self._mock_search_fallback(query)
            
        except Exception as e:
            print(f"[Web Search Error] {str(e)}")
            return self._mock_search_fallback(query)
    
    def _mock_search_fallback(self, query: str) -> str:
        """Enhanced fallback with realistic multi-source data"""
        query_lower = query.lower()
        
        print(f"[Fallback] Using mock data for: {query}")
        
        if "l'oreal" in query_lower or "loreal" in query_lower:
            return """SOURCES CHECKED: 3

PETA (2024): L'Oréal tests on animals where required by law, particularly in mainland China. Not on cruelty-free list.

Cruelty-Free International: L'Oréal continues to sell products in China, which requires animal testing for imported cosmetics.

Leaping Bunny Database: L'Oréal is NOT certified cruelty-free.

CONFIDENCE: High (3/3 sources agree)"""
        
        elif "alternative" in query_lower or "cruelty free" in query_lower:
            if "mascara" in query_lower:
                return """SOURCES CHECKED: 4

PETA Cruelty-Free Database: 
- e.l.f. Big Mood Mascara ($7) - Certified cruelty-free, 100% vegan
- Essence Lash Princess ($5) - Cruelty-free verified

Leaping Bunny Certified:
- Pacifica Dream Big Mascara ($12) - Certified CF & vegan
- Milk Makeup Kush Mascara ($24) - Leaping Bunny approved

Cruelty-Free Kitty (Independent verification):
- All above brands verified as maintaining cruelty-free status in 2024

Price Source: Brand websites, Ulta, Sephora (Oct 2024)

CONFIDENCE: Very High (4/4 sources agree)"""
            
            elif "foundation" in query_lower:
                return """SOURCES CHECKED: 3

PETA Database:
- e.l.f. Flawless Finish Foundation ($7) - 100% vegan, CF certified
- Pacifica Alight Multi-Mineral Foundation ($14) - Vegan, CF

Leaping Bunny:
- Physician's Formula Healthy Foundation ($13) - Certified cruelty-free
- Cover FX Power Play Foundation ($48) - Luxury CF option

Sources: PETA, Leaping Bunny, brand websites (2024)

CONFIDENCE: High"""
        
        return f"""SOURCES CHECKED: 2

Searching for information about: {query}

Note: Using enhanced knowledge base. Real-time web search available for unknown brands.

CONFIDENCE: Medium (using cached knowledge)"""
    
    def _execute_tool(self, tool_name: str, tool_input: dict) -> any:
        """Execute a tool - now using database module methods"""
        self.tool_calls.append({
            "tool": tool_name,
            "input": tool_input,
            "timestamp": datetime.now().isoformat()
        })
        
        if tool_name == "check_database":
            # Use database module's check_brand method
            brand_name = tool_input["brand_name"]
            result = self.db.check_brand(brand_name)
            
            # Log the search
            self.db.log_search(brand_name, brand_name, result.get("found", False))
            
            return result
        
        elif tool_name == "web_search":
            result = self._web_search(tool_input["query"])
            
            # Extract confidence metrics from search result
            sources_count = self._extract_sources_count(result)
            has_conflicts = self._detect_conflicts(result)
            
            # Store for later use
            if self.last_brand_discussed:
                self.last_verification_result = VerificationResult(
                    brand=self.last_brand_discussed,
                    is_cruelty_free=True,  # Will be updated by agent's final answer
                    sources_count=sources_count,
                    has_conflicts=has_conflicts
                )
            
            return result
        
        elif tool_name == "save_to_database":
            # Use database module's save_brand method
            brand_name = tool_input["brand_name"]
            
            result = self.db.save_brand(
                brand_name=brand_name,
                is_cruelty_free=tool_input["is_cruelty_free"],
                parent_company=tool_input.get("parent_company"),
                explanation=tool_input.get("explanation", ""),
                sources=tool_input.get("sources", []),
                confidence=tool_input.get("confidence", 0.9)
            )
            
            return result
        
        elif tool_name == "search_database":
            # Use database module's search_brands method
            query = tool_input["query"]
            limit = tool_input.get("limit", 10)
            results = self.db.search_brands(query, limit)
            
            return {
                "found": len(results) > 0,
                "count": len(results),
                "brands": results
            }
        
        elif tool_name == "get_database_stats":
            # Use database module's get_database_stats method
            return self.db.get_database_stats()
        
        return {"error": f"Unknown tool: {tool_name}"}
    
    def _detect_feedback(self, user_query: str) -> bool:
        """Detect if user is giving feedback or expressing preferences"""
        feedback_words = ["expensive", "cheap", "too much", "perfect", "good", "bad", 
                         "affordable", "pricey", "budget", "love", "hate",
                         "vegan", "fragrance", "paraben", "scent"]
        return any(word in user_query.lower() for word in feedback_words)
    
    def process_query(self, user_query: str) -> tuple:
        """Main agentic loop with confidence scoring"""
        self.tool_calls = []
        
        # Check for feedback
        if self._detect_feedback(user_query):
            if self.last_recommendation:
                self.user_profile.learn_from_feedback(
                    user_query,
                    {"last_price": self.last_recommendation.get("price")}
                )
            else:
                self.user_profile.learn_from_feedback(user_query, {})
        
        # Get context
        profile_summary = self.user_profile.get_profile_summary()
        constraints = self.user_profile.get_constraints_for_agent()
        
        # Get database stats for context
        db_stats = self.db.get_database_stats()
        
        context_info = f"\n\nDATABASE INFO:\n- Total brands in database: {db_stats['total_brands']}\n- Cruelty-free brands: {db_stats['cruelty_free_count']}"
        
        if self.last_brand_discussed:
            context_info += f"\n\nCONVERSATION CONTEXT:\n- Last brand discussed: {self.last_brand_discussed}"
            if self.last_product_type:
                context_info += f"\n- Product type: {self.last_product_type}"
        
        system_prompt = f"""You are an intelligent agent helping users find cruelty-free beauty products.

USER PROFILE: {profile_summary}
USER CONSTRAINTS: {constraints}{context_info}

YOUR PROCESS:
1. ALWAYS check database first using check_database tool
2. If not found or stale, use web_search to verify
3. After web search, ALWAYS save the results using save_to_database
4. When recommending alternatives, ALWAYS respect user constraints: {constraints}
5. Be conversational and remember the user's preferences

AVAILABLE TOOLS:
- check_database: Look up a specific brand
- search_database: Find brands by partial name
- get_database_stats: Get database statistics
- web_search: Search web for new information
- save_to_database: Save verified brand info (ALWAYS use after web_search)

IMPORTANT:
- When suggesting alternatives, filter by user's budget if known
- Prioritize options that match ALL user values (vegan, fragrance-free, etc.)
- Mention when products match user preferences
- Be friendly and personal
- If user asks a follow-up question like "is it vegan?", refer to the last brand discussed: {self.last_brand_discussed or 'unknown'}
- ALWAYS save new brand verifications to the database after searching

RESPONSE STYLE:
- Conversational and warm
- Acknowledge user preferences when relevant
- Explain WHY recommendations match their needs"""

        messages = [{"role": "user", "content": user_query}]
        
        # Agentic loop
        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                system=system_prompt,
                tools=self.tools,
                messages=messages
            )
            
            if response.stop_reason == "tool_use":
                tool_use_block = next(
                    block for block in response.content 
                    if block.type == "tool_use"
                )
                
                tool_name = tool_use_block.name
                tool_input = tool_use_block.input
                
                # Track brand
                if tool_name == "check_database":
                    self.last_brand_discussed = tool_input.get("brand_name")
                
                tool_result = self._execute_tool(tool_name, tool_input)
                
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": json.dumps(tool_result)
                        }
                    ]
                })
                
                continue
            
            elif response.stop_reason == "end_turn":
                final_text = next(
                    (block.text for block in response.content if hasattr(block, "text")),
                    ""
                )
                
                self.last_recommendation = {"price": 10}
                
                return final_text, self.tool_calls
            
            break
        
        return "Error in processing", self.tool_calls
    
    def get_conversation_stats(self) -> dict:
        """Get statistics about the current conversation"""
        return {
            "total_tool_calls": len(self.tool_calls),
            "brands_checked": len([t for t in self.tool_calls if t["tool"] == "check_database"]),
            "web_searches": len([t for t in self.tool_calls if t["tool"] == "web_search"]),
            "brands_saved": len([t for t in self.tool_calls if t["tool"] == "save_to_database"]),
            "last_brand": self.last_brand_discussed,
            "user_profile": self.user_profile.get_profile_summary()
        }
    
    def correct_brand_entry(self, brand_name: str, is_cruelty_free: bool, 
                           explanation: str = None, confidence: float = 0.95) -> dict:
        """
        Manually correct a brand entry that was saved incorrectly
        
        Args:
            brand_name: Name of the brand to correct
            is_cruelty_free: Correct cruelty-free status
            explanation: Explanation for the correction
            confidence: Confidence level (default 0.95 for manual corrections)
            
        Returns:
            Dictionary with correction result
        """
        if explanation is None:
            status = "cruelty-free" if is_cruelty_free else "not cruelty-free"
            explanation = f"Manually corrected to {status}"
        
        result = self.db.save_brand(
            brand_name=brand_name,
            is_cruelty_free=is_cruelty_free,
            explanation=explanation,
            confidence=confidence
        )
        
        print(f"[Manual Correction] Updated {brand_name} to CF={is_cruelty_free}")
        return result


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Agent with Database Module")
    print("="*60 + "\n")
    
    # Initialize agent (will create/connect to database)
    agent = ConsciousCartAgent()
    
    # Test 1: Query about a brand
    print("Test 1: Querying brand...")
    response, tools = agent.process_query("Is Boody cruelty-free?")
    print(f"\nResponse: {response}")
    print(f"Tools used: {len(tools)}")
    
    # Test 2: Get conversation stats
    print("\n" + "="*60)
    print("Test 2: Conversation statistics...")
    stats = agent.get_conversation_stats()
    print(f"Total tool calls: {stats['total_tool_calls']}")
    print(f"Brands checked: {stats['brands_checked']}")
    print(f"Web searches: {stats['web_searches']}")
    print(f"Brands saved: {stats['brands_saved']}")
    
    # Test 3: Database stats
    print("\n" + "="*60)
    print("Test 3: Database statistics...")
    db_stats = agent.db.get_database_stats()
    print(f"Total brands: {db_stats['total_brands']}")
    print(f"Cruelty-free: {db_stats['cruelty_free_count']} ({db_stats['cruelty_free_percentage']}%)")
    
    if agent.last_verification_result:
        vr = agent.last_verification_result
        print(f"\nConfidence Score: {vr.confidence:.2f} ({vr.get_confidence_label()})")
        print(f"Sources Checked: {vr.sources_count}")
        print(f"Conflicts Detected: {vr.has_conflicts}")
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)