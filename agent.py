"""
ConsciousCart - Personalized Agentic System
With user profiling, preference learning, and confidence scoring
"""
import os
import json
import sqlite3
from datetime import datetime, timedelta
from anthropic import Anthropic
from dotenv import load_dotenv

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
            "cruelty_free": True  # Always true for this app
        }
        self.product_history = []
        self.preferred_brands = set()
        self.rejected_brands = set()
        self.last_recommendation_price = None
    
    def learn_from_feedback(self, feedback: str, context: dict):
        """Learn from user's implicit and explicit feedback"""
        feedback_lower = feedback.lower()
        
        # Budget learning from "too expensive" or "cheap"
        if "expensive" in feedback_lower or "too much" in feedback_lower or "pricey" in feedback_lower:
            if context.get("last_price"):
                # User thinks this price is too high, set max 30% lower
                self.budget_max = int(context["last_price"] * 0.7)
                print(f"[Profile] Learned budget_max: ${self.budget_max}")
        
        elif "cheap" in feedback_lower or "affordable" in feedback_lower or "budget" in feedback_lower:
            if context.get("last_price"):
                # User wants cheap, set max at this price
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
    """Result from cruelty-free verification with confidence"""
    
    def __init__(self, brand: str, is_cruelty_free: bool, confidence: float,
                 explanation: str, sources: list, conflicts: list = None):
        self.brand = brand
        self.is_cruelty_free = is_cruelty_free
        self.confidence = confidence
        self.explanation = explanation
        self.sources = sources
        self.conflicts = conflicts or []
    
    def to_dict(self) -> dict:
        return {
            "brand": self.brand,
            "is_cruelty_free": self.is_cruelty_free,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "sources": self.sources,
            "conflicts": self.conflicts
        }


class ConsciousCartAgent:
    """Personalized agentic system for cruelty-free verification"""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        self.db_path = "brands.db"
        self.conversation_history = []
        self.tool_calls = []
        
        # NEW: User profile for personalization
        self.user_profile = UserProfile()
        self.last_recommendation = None
        
        # Initialize database
        self._init_database()
        
        # Define available tools
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
                "description": "Save verified brand information to database.",
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
                        }
                    },
                    "required": ["brand_name", "is_cruelty_free", "explanation"]
                }
            }
        ]
    
    def _init_database(self):
        """Initialize SQLite database"""
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
                last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Seed with known brands
        self._seed_database()
    
    def _seed_database(self):
        """Pre-populate with known brands"""
        known_brands = [
            ("Maybelline", False, "L'Oréal", "Owned by L'Oréal which tests in China", "PETA,Leaping Bunny"),
            ("Fenty Beauty", True, "LVMH", "Certified cruelty-free, no animal testing", "Leaping Bunny,PETA"),
            ("e.l.f. Cosmetics", True, None, "Certified cruelty-free and vegan", "Leaping Bunny,PETA"),
            ("MAC", False, "Estée Lauder", "Owned by Estée Lauder which tests on animals", "PETA"),
            ("NYX", False, "L'Oréal", "Owned by L'Oréal", "PETA"),
            ("Pacifica", True, None, "100% vegan and cruelty-free", "Leaping Bunny,PETA"),
            ("CoverGirl", False, "Coty", "Tests where required by law", "PETA"),
            ("Revlon", False, None, "Not cruelty-free", "PETA"),
            ("Urban Decay", True, "L'Oréal", "Maintains cruelty-free despite parent", "Leaping Bunny"),
            ("Too Faced", True, "Estée Lauder", "Cruelty-free certified", "Leaping Bunny"),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for brand_data in known_brands:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO brands 
                    (name, is_cruelty_free, parent_company, explanation, sources)
                    VALUES (?, ?, ?, ?, ?)
                """, brand_data)
            except:
                pass
        
        conn.commit()
        conn.close()
    
    def _check_database(self, brand_name: str) -> dict:
        """Tool: Check database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, is_cruelty_free, parent_company, explanation, 
                   sources, last_verified
            FROM brands 
            WHERE LOWER(name) = LOWER(?)
        """, (brand_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            name, is_cf, parent, explanation, sources, last_verified = result
            
            last_verified_date = datetime.strptime(last_verified, "%Y-%m-%d %H:%M:%S")
            is_stale = datetime.now() - last_verified_date > timedelta(days=30)
            
            return {
                "found": True,
                "brand_name": name,
                "is_cruelty_free": bool(is_cf),
                "parent_company": parent,
                "explanation": explanation,
                "sources": sources.split(",") if sources else [],
                "last_verified": last_verified,
                "is_stale": is_stale
            }
        
        return {"found": False}
    
    def _web_search(self, query: str) -> str:
        """Tool: Web search using Claude (replace with real API later)"""
        # Mock search for now - you can add real Tavily/Brave API here
        query_lower = query.lower()
        
        if "l'oreal" in query_lower or "loreal" in query_lower:
            return "L'Oréal is a French cosmetics company that tests on animals where required by law, particularly in mainland China. Sources: PETA, Cruelty-Free International."
        
        elif "alternative" in query_lower or "cruelty free" in query_lower:
            if "mascara" in query_lower:
                return "Cruelty-free mascara alternatives include: e.l.f. Big Mood Mascara ($7), Pacifica Dream Big ($12), Essence Lash Princess ($5), Milk Makeup Kush ($24). Sources: Brand websites, Leaping Bunny database."
            elif "foundation" in query_lower:
                return "Cruelty-free foundations: e.l.f. Flawless Finish ($7), Pacifica Alight ($14), Physician's Formula Healthy ($13). Sources: Leaping Bunny, brand sites."
            elif "lipstick" in query_lower:
                return "Cruelty-free lipsticks: e.l.f. Satin ($3), Pacifica Color Quench ($9), Bite Beauty ($18). Sources: PETA, Leaping Bunny."
        
        return f"Search results for: {query}"
    
    def _save_to_database(self, brand_name: str, is_cruelty_free: bool,
                         parent_company: str = None, explanation: str = "",
                         sources: list = None) -> dict:
        """Tool: Save to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sources_str = ",".join(sources) if sources else ""
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO brands 
                (name, is_cruelty_free, parent_company, explanation, sources, last_verified)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (brand_name, is_cruelty_free, parent_company, explanation, sources_str))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": f"Saved {brand_name}"}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e)}
    
    def _execute_tool(self, tool_name: str, tool_input: dict) -> any:
        """Execute a tool"""
        self.tool_calls.append({
            "tool": tool_name,
            "input": tool_input,
            "timestamp": datetime.now().isoformat()
        })
        
        if tool_name == "check_database":
            return self._check_database(tool_input["brand_name"])
        elif tool_name == "web_search":
            return self._web_search(tool_input["query"])
        elif tool_name == "save_to_database":
            return self._save_to_database(
                tool_input["brand_name"],
                tool_input["is_cruelty_free"],
                tool_input.get("parent_company"),
                tool_input.get("explanation", ""),
                tool_input.get("sources", [])
            )
        
        return {"error": f"Unknown tool: {tool_name}"}
    
    def _detect_feedback(self, user_query: str) -> bool:
        """Detect if user is giving feedback on previous recommendation"""
        feedback_words = ["expensive", "cheap", "too much", "perfect", "good", "bad", 
                         "affordable", "pricey", "budget", "love", "hate"]
        return any(word in user_query.lower() for word in feedback_words)
    
    def process_query(self, user_query: str) -> tuple:
        """Main agentic loop with personalization"""
        self.tool_calls = []
        
        # Check if this is feedback on previous recommendation
        if self._detect_feedback(user_query) and self.last_recommendation:
            self.user_profile.learn_from_feedback(
                user_query,
                {"last_price": self.last_recommendation.get("price")}
            )
        
        # Get user profile context
        profile_summary = self.user_profile.get_profile_summary()
        constraints = self.user_profile.get_constraints_for_agent()
        
        # System prompt with personalization
        system_prompt = f"""You are an intelligent agent helping users find cruelty-free beauty products.

USER PROFILE: {profile_summary}
USER CONSTRAINTS: {constraints}

YOUR PROCESS:
1. ALWAYS check database first using check_database tool
2. If not found or stale, use web_search to verify
3. When recommending alternatives, ALWAYS respect user constraints: {constraints}
4. Save new verifications to database
5. Be conversational and remember the user's preferences

IMPORTANT:
- When suggesting alternatives, filter by user's budget if known
- Prioritize options that match ALL user values (vegan, fragrance-free, etc.)
- Mention when products match user preferences
- Be friendly and personal

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
                
                # Store last recommendation context
                # (simplified - in production, parse the response better)
                self.last_recommendation = {"price": 10}  # Default
                
                return final_text, self.tool_calls
            
            break
        
        return "Error in processing", self.tool_calls


if __name__ == "__main__":
    agent = ConsciousCartAgent()
    
    # Test personalization
    print("\n" + "="*60)
    print("Testing Personalization")
    print("="*60)
    
    response, tools = agent.process_query("Is Maybelline cruelty-free?")
    print(f"\nResponse: {response}")
    print(f"Profile: {agent.user_profile.get_profile_summary()}")