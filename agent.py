"""
ConsciousCart - True Agentic System
Single agent with autonomous tool use and decision making
"""
import os
import json
import sqlite3
from datetime import datetime, timedelta
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class ConsciousCartAgent:
    """
    Agentic system for cruelty-free product verification
    Agent autonomously decides which tools to use and when
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"
        self.db_path = "brands.db"
        self.conversation_history = []
        self.tool_calls = []  # Track for UI display
        
        # Initialize database
        self._init_database()
        
        # Define available tools
        self.tools = [
            {
                "name": "check_database",
                "description": "Check if a brand exists in the local database of verified brands. Returns cached cruelty-free status if available. Use this FIRST before searching the web to save time.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brand_name": {
                            "type": "string",
                            "description": "The brand name to look up (e.g., 'Maybelline', 'Fenty Beauty')"
                        }
                    },
                    "required": ["brand_name"]
                }
            },
            {
                "name": "web_search",
                "description": "Search the web for information about brands, cruelty-free status, certifications, or product alternatives. Use when information is not in database or needs verification.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query. Be specific (e.g., 'Maybelline cruelty free certification PETA')"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "save_to_database",
                "description": "Save verified brand information to the database for future queries. Use after verifying a brand's status.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "brand_name": {
                            "type": "string",
                            "description": "Brand name"
                        },
                        "is_cruelty_free": {
                            "type": "boolean",
                            "description": "Whether the brand is cruelty-free"
                        },
                        "parent_company": {
                            "type": "string",
                            "description": "Parent company name if applicable"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Brief explanation of the determination"
                        },
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of sources checked"
                        }
                    },
                    "required": ["brand_name", "is_cruelty_free", "explanation"]
                }
            }
        ]
    
    def _init_database(self):
        """Initialize SQLite database with schema"""
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
        
        conn.commit()
        conn.close()
        
        # Seed with popular brands
        self._seed_database()
    
    def _seed_database(self):
        """Pre-populate database with known brands"""
        known_brands = [
            ("Maybelline", False, "L'Oréal", "Owned by L'Oréal which tests on animals and sells in China", "PETA,Leaping Bunny"),
            ("Fenty Beauty", True, "LVMH", "Certified cruelty-free, does not test on animals", "Leaping Bunny,PETA"),
            ("e.l.f. Cosmetics", True, None, "Certified cruelty-free and vegan by Leaping Bunny and PETA", "Leaping Bunny,PETA"),
            ("MAC", False, "Estée Lauder", "Owned by Estée Lauder which tests on animals where required by law", "PETA"),
            ("NYX", False, "L'Oréal", "Owned by L'Oréal which tests on animals", "PETA"),
            ("Urban Decay", True, "L'Oréal", "Certified cruelty-free despite L'Oréal ownership", "Leaping Bunny"),
            ("Too Faced", True, "Estée Lauder", "Maintains cruelty-free status despite parent company", "Leaping Bunny"),
            ("Pacifica", True, None, "100% vegan and cruelty-free certified", "Leaping Bunny,PETA"),
            ("CoverGirl", False, "Coty", "Tests on animals where required by law", "PETA"),
            ("Revlon", False, None, "Not cruelty-free, tests on animals", "PETA"),
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
        """Tool: Check if brand is in database"""
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
            
            # Check if data is stale (>30 days)
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
        """Tool: Search the web (mock for now, integrate real search later)"""
        # TODO: Integrate Brave Search or Tavily API
        # For now, return mock results
        
        query_lower = query.lower()
        
        # Mock search results based on query
        if "l'oreal" in query_lower or "loreal" in query_lower:
            return "L'Oréal is a French cosmetics company that tests on animals where required by law, particularly in mainland China. They own brands including Maybelline, NYX, Garnier, and others."
        
        elif "estee lauder" in query_lower or "estée lauder" in query_lower:
            return "Estée Lauder tests on animals when required by law. They own MAC, Clinique, Bobbi Brown, and other brands. Some subsidiaries like Too Faced maintain cruelty-free status."
        
        elif "leaping bunny" in query_lower:
            return "Leaping Bunny is the gold standard for cruelty-free certification. Certified brands commit to no animal testing at any stage of product development."
        
        elif "peta" in query_lower:
            return "PETA maintains a comprehensive list of cruelty-free and companies that test on animals. Certification requires no animal testing and no sales in mainland China."
        
        elif "alternative" in query_lower:
            if "mascara" in query_lower:
                return "Popular cruelty-free mascara alternatives: e.l.f. Big Mood ($7), Pacifica Dream Big ($12), Essence Lash Princess ($5), Milk Makeup Kush ($24)"
            elif "foundation" in query_lower:
                return "Cruelty-free foundation alternatives: e.l.f. Flawless Finish ($7), Pacifica Alight ($14), Physician's Formula Healthy ($13)"
            elif "lipstick" in query_lower:
                return "Cruelty-free lipstick alternatives: e.l.f. Satin Lipstick ($3), NYX (varies), Pacifica Color Quench ($9)"
        
        return f"Search results for: {query}. General information found."
    
    def _save_to_database(self, brand_name: str, is_cruelty_free: bool, 
                         parent_company: str = None, explanation: str = "",
                         sources: list = None) -> dict:
        """Tool: Save brand info to database"""
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
            
            return {"success": True, "message": f"Saved {brand_name} to database"}
        except Exception as e:
            conn.close()
            return {"success": False, "error": str(e)}
    
    def _execute_tool(self, tool_name: str, tool_input: dict) -> any:
        """Execute a tool and return result"""
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
    
    def process_query(self, user_query: str) -> tuple:
        """
        Main agentic loop
        Returns: (response_text, tool_calls_made)
        """
        self.tool_calls = []  # Reset for new query
        
        # System prompt for the agent
        system_prompt = """You are an intelligent agent helping users determine if beauty products are cruelty-free.

YOUR DECISION-MAKING PROCESS:
1. ALWAYS check the database FIRST using check_database tool
   - If found and recent (<30 days), use that data
   - If found but stale, mention it and optionally verify with web search
   - If not found, proceed to web search

2. When searching the web:
   - Search for brand's cruelty-free certification status
   - Check parent company if relevant
   - Look for Leaping Bunny or PETA certification
   - Check if they sell in China (requires animal testing)

3. Save new information to database using save_to_database

4. If product is NOT cruelty-free, search for alternatives

5. Be transparent about your reasoning and sources

IMPORTANT RULES:
- A brand is NOT cruelty-free if parent company tests OR if they sell in mainland China
- Use multiple searches if needed to verify information
- Always explain your determination clearly
- Suggest 2-3 alternatives with prices if brand is not cruelty-free

Be conversational and helpful!"""

        # Initialize conversation
        messages = [
            {"role": "user", "content": user_query}
        ]
        
        # Agentic loop - agent decides which tools to use
        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                system=system_prompt,
                tools=self.tools,
                messages=messages
            )
            
            # Check if agent wants to use a tool
            if response.stop_reason == "tool_use":
                # Agent decided to use a tool!
                tool_use_block = next(
                    block for block in response.content 
                    if block.type == "tool_use"
                )
                
                tool_name = tool_use_block.name
                tool_input = tool_use_block.input
                
                # Execute the tool
                tool_result = self._execute_tool(tool_name, tool_input)
                
                # Add assistant's tool use to conversation
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Add tool result to conversation
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
                
                # Agent continues reasoning with tool result...
                continue
            
            # Agent is done - return final response
            elif response.stop_reason == "end_turn":
                final_text = next(
                    (block.text for block in response.content if hasattr(block, "text")),
                    ""
                )
                return final_text, self.tool_calls
            
            # Shouldn't reach here, but break just in case
            break
        
        return "Error in agent processing", self.tool_calls


# Example usage
if __name__ == "__main__":
    agent = ConsciousCartAgent()
    
    test_queries = [
        "Is Maybelline cruelty-free?",
        "What about Fenty Beauty?",
        "I use MAC lipstick, is it cruelty-free?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        response, tools_used = agent.process_query(query)
        
        print(f"\nTools used: {len(tools_used)}")
        for tool_call in tools_used:
            print(f"  - {tool_call['tool']}: {tool_call['input']}")
        
        print(f"\nResponse:\n{response}")