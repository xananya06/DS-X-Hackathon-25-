# """
# ConsciousCart - Warm neutral UI with collapsible sidebar and white cards
# """
# import streamlit as st
# import sys
# from pathlib import Path

# # Add parent directory to path for imports
# sys.path.append(str(Path(__file__).parent))

# from agent import ConsciousCartAgent

# # Page config
# st.set_page_config(
#     page_title="ConsciousCart",
#     page_icon="🐇",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # Load Font Awesome (icons)
# st.markdown(
#     """<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">""",
#     unsafe_allow_html=True,
# )

# # CSS + JS
# st.markdown(
#     """
# <style>
#   /* Page background - light brown */
#   .stApp {
#     background: #D4A574;
#     color: #0b0b0b;
#     font-family: 'Segoe UI', BlinkMacSystemFont, Roboto, "Helvetica Neue", Arial, sans-serif;
#   }

#   .block-container {
#     padding-top: 20px;
#     padding-left: 40px;
#     padding-right: 40px;
#     padding-bottom: 28px;
#     max-width: 1400px;
#     margin-left: auto;
#     margin-right: auto;
#   }

#   /* Chat message card - white background, centered */
#   [data-testid="stChatMessageContent"] {
#     max-width: 1200px !important;
#     margin: 10px auto !important;
#     background: #ffffff !important;
#     color: #000000 !important;
#     border-radius: 14px !important;
#     padding: 20px !important;
#     border: 2px solid rgba(0,0,0,0.1) !important;
#     box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
#     font-weight: 500;
#     min-height: 60px;
#   }

#   /* Chat input styling - centered and extended */
#   .stChatInputContainer {
#     background: transparent !important;
#     padding: 10px !important;
#     max-width: 1200px !important;
#     margin: 20px auto !important;
#   }
#   .stChatInputContainer textarea, .stChatInputContainer input {
#     background: #ffffff !important;
#     color: #000000 !important;
#     border-radius: 14px !important;
#     border: 2px solid rgba(0,0,0,0.1) !important;
#     padding: 18px !important;
#     font-size: 16px !important;
#     font-weight: 500;
#     min-height: 80px !important;
#   }
#   .stChatInputContainer button {
#     background: #f5f5dc !important;
#     color: #000000 !important;
#     border: none !important;
#     border-radius: 10px !important;
#     padding: 10px 16px !important;
#     margin-left: 8px !important;
#     font-weight: 600 !important;
#     cursor: pointer !important;
#     transition: all 0.3s ease;
#   }
#   .stChatInputContainer button:hover { 
#     background: #000000 !important;
#     color: #ffffff !important;
#     transform: translateY(-2px); 
#     box-shadow: 0 6px 20px rgba(0,0,0,0.15);
#   }

#   /* Tool call boxes */
#   .tool-call {
#     background: rgba(255,255,255,0.95);
#     padding: 12px;
#     border-radius: 12px;
#     margin: 8px 0;
#     border-left: 4px solid #5D4037;
#     box-shadow: 0 2px 8px rgba(0,0,0,0.08);
#   }
#   .tool-name { color: #5D4037; font-weight: 700; font-size: 0.95em; }
#   .tool-input { color: #3E2723; font-family: Monaco, monospace; font-size: 0.88em; margin-top: 4px; }

#   /* Sidebar styling - BLACK */
#   section[data-testid="stSidebar"] {
#     background: #000000 !important;
#     border-right: 2px solid rgba(255, 255, 255, 0.2);
#     padding: 20px !important;
#     transition: transform 0.3s ease, opacity 0.3s ease;
#   }
  
#   section[data-testid="stSidebar"][aria-expanded="false"] {
#     transform: translateX(-100%);
#     opacity: 0;
#   }

#   /* Sidebar text colors */
#   section[data-testid="stSidebar"] h2,
#   section[data-testid="stSidebar"] h3,
#   section[data-testid="stSidebar"] p,
#   section[data-testid="stSidebar"] div,
#   section[data-testid="stSidebar"] li {
#     color: #ffffff !important;
#   }

#   section[data-testid="stSidebar"] hr {
#     border-color: rgba(255, 255, 255, 0.3) !important;
#   }

#   /* Snapshot section styling - BEIGE background */
#   section[data-testid="stSidebar"] .element-container:has([data-testid="stMetric"]) {
#     background: #f5f5dc !important;
#     padding: 16px !important;
#     border-radius: 12px !important;
#     margin: 12px 0 !important;
#   }

#   /* Expander styling - WHITE background */
#   .streamlit-expanderHeader {
#     background: #ffffff !important;
#     border-radius: 8px !important;
#     color: #000000 !important;
#     font-weight: 600 !important;
#     padding: 12px !important;
#     margin: 8px 0 !important;
#   }

#   .streamlit-expanderContent {
#     background: #ffffff !important;
#     color: #000000 !important;
#     border-radius: 0 0 8px 8px !important;
#     padding: 12px !important;
#   }

#   /* Metric styling in sidebar - BEIGE with BLACK text */
#   [data-testid="stMetric"] {
#     background: #f5f5dc !important;
#     padding: 14px !important;
#     border-radius: 10px !important;
#     border-left: 3px solid #5D4037 !important;
#     margin-bottom: 12px !important;
#   }
#   [data-testid="stMetricLabel"] {
#     color: #000000 !important;
#     font-weight: 600 !important;
#     font-size: 1em !important;
#   }
#   [data-testid="stMetricValue"] {
#     color: #000000 !important;
#     font-weight: 700 !important;
#     font-size: 1.5em !important;
#   }
#   [data-testid="stMetricDelta"] {
#     color: #000000 !important;
#   }

#   /* Start Fresh button - BIGGER */
#   .stButton>button {
#     background: #f5f5dc !important;
#     color: #000000 !important;
#     border: none !important;
#     border-radius: 14px !important;
#     padding: 16px 24px !important;
#     font-weight: 700 !important;
#     font-size: 17px !important;
#     cursor: pointer !important;
#     transition: all 0.3s ease !important;
#     box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
#     width: 100% !important;
#     display: flex !important;
#     align-items: center !important;
#     justify-content: center !important;
#     gap: 10px !important;
#   }
#   .stButton>button:hover { 
#     background: #000000 !important;
#     color: #ffffff !important;
#     transform: translateY(-2px) !important;
#     box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
#   }

#   /* Summary cards - HORIZONTAL ROW, CENTERED, EXTENDED */
#   .summary-wrap {
#     display: flex;
#     justify-content: center;
#     align-items: stretch;
#     gap: 24px;
#     padding: 20px 40px;
#     margin: 20px auto 30px auto;
#     flex-wrap: nowrap;
#     max-width: 1400px;
#   }
  
#   .summary-wrap.hidden {
#     display: none;
#   }
  
#   .summary-card {
#     background: #ffffff;
#     flex: 1;
#     max-width: 400px;
#     min-width: 280px;
#     height: 180px;
#     border-radius: 16px;
#     padding: 24px;
#     box-shadow: 0 6px 20px rgba(0,0,0,0.12);
#     border: 2px solid rgba(93, 64, 55, 0.15);
#     text-align: left;
#     transition: all 0.3s ease;
#     display: flex;
#     flex-direction: column;
#     justify-content: space-between;
#   }
#   .summary-card:hover {
#     transform: translateY(-5px);
#     box-shadow: 0 10px 30px rgba(0,0,0,0.18);
#   }
#   .summary-card .title { 
#     font-size: 1.15em; 
#     margin-bottom: 10px; 
#     color: #000000; 
#     font-weight: 700;
#   }
#   .summary-card .value { 
#     font-size: 1.8em; 
#     color: #000000; 
#     margin: 10px 0;
#     font-weight: 600;
#   }
#   .summary-card .description {
#     font-size: 0.94em; 
#     color: #000000;
#     font-weight: 400;
#     flex-grow: 1;
#   }

#   /* Page title styling - centered */
#   .page-header {
#     text-align: center;
#     max-width: 1200px;
#     margin: 0 auto 20px auto;
#   }

#   h2, h3 {
#     color: #5D4037 !important;
#   }

#   /* Quick access section - centered, below chat */
#   .quick-access-section {
#     text-align: center;
#     max-width: 800px;
#     margin: 30px auto;
#     padding: 20px;
#   }
  
#   .quick-access-section.hidden {
#     display: none;
#   }

#   .quick-access-section h3 {
#     color: #5D4037;
#     margin-bottom: 15px;
#   }

#   .quick-access-section p {
#     color: #000000;
#     font-size: 1.05em;
#     margin: 8px 0;
#   }

#   /* Footer */
#   .footer { 
#     text-align: center; 
#     color: #5D4037; 
#     margin-top: 20px;
#     font-weight: 500;
#   }

#   /* Mobile responsive */
#   @media (max-width: 1200px) {
#     .summary-wrap {
#       flex-wrap: wrap;
#       gap: 20px;
#     }
#     .summary-card {
#       flex: 1 1 calc(50% - 20px);
#       min-width: 260px;
#     }
#   }

#   @media (max-width: 880px) {
#     .block-container { 
#       padding-left: 20px; 
#       padding-right: 20px; 
#     }
#     .summary-wrap { 
#       flex-wrap: wrap;
#       gap: 15px;
#       padding: 20px 15px;
#     }
#     .summary-card { 
#       flex: 1 1 100%;
#       max-width: 100%;
#       height: auto;
#       min-height: 160px;
#     }
#     [data-testid="stChatMessageContent"] {
#       max-width: 100% !important;
#     }
#     .stChatInputContainer {
#       max-width: 100% !important;
#     }
#   }

#   @media (max-width: 640px) {
#     .summary-card {
#       min-height: 140px;
#       padding: 18px;
#     }
#     .summary-card .title {
#       font-size: 1em;
#     }
#     .summary-card .value {
#       font-size: 1.5em;
#     }
#     h2 {
#       font-size: 1.5em !important;
#     }
#     h3 {
#       font-size: 1.2em !important;
#     }
#     .stChatInputContainer textarea, .stChatInputContainer input {
#       min-height: 60px !important;
#       padding: 14px !important;
#     }
#   }
# </style>

# <script>
#   (function() {
#     let sidebarOpen = false;
    
#     function findSidebar() {
#       return document.querySelector('section[data-testid="stSidebar"]');
#     }
    
#     function initializeSidebar() {
#       const sidebar = findSidebar();
#       if (sidebar && !sidebarOpen) {
#         sidebar.style.transform = 'translateX(-100%)';
#         sidebar.style.opacity = '0';
#         sidebar.setAttribute('aria-expanded', 'false');
#       }
#     }
    
#     window.toggleSidebarFunc = function() {
#       const sidebar = findSidebar();
#       if (!sidebar) return;
      
#       sidebarOpen = !sidebarOpen;
      
#       if (sidebarOpen) {
#         sidebar.style.transform = 'translateX(0)';
#         sidebar.style.opacity = '1';
#         sidebar.setAttribute('aria-expanded', 'true');
#       } else {
#         sidebar.style.transform = 'translateX(-100%)';
#         sidebar.style.opacity = '0';
#         sidebar.setAttribute('aria-expanded', 'false');
#       }
#     };
    
#     // Hide elements when there are messages
#     function checkAndHideElements() {
#       const chatMessages = document.querySelectorAll('[data-testid="stChatMessageContent"]');
#       const summaryWrap = document.querySelector('.summary-wrap');
#       const quickAccess = document.querySelector('.quick-access-section');
      
#       if (chatMessages.length > 1) { // More than just the welcome message
#         if (summaryWrap) summaryWrap.classList.add('hidden');
#         if (quickAccess) quickAccess.classList.add('hidden');
#       } else {
#         if (summaryWrap) summaryWrap.classList.remove('hidden');
#         if (quickAccess) quickAccess.classList.remove('hidden');
#       }
#     }
    
#     // Initialize on load
#     if (document.readyState === 'loading') {
#       document.addEventListener('DOMContentLoaded', function() {
#         initializeSidebar();
#         checkAndHideElements();
#       });
#     } else {
#       initializeSidebar();
#       checkAndHideElements();
#     }
    
#     // Reinitialize after Streamlit rerenders
#     setInterval(function() {
#       initializeSidebar();
#       checkAndHideElements();
#     }, 500);
#   })();
# </script>
# """,
#     unsafe_allow_html=True,
# )

# # Initialize agent
# @st.cache_resource
# def get_agent():
#     return ConsciousCartAgent()

# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#     st.session_state.messages.append({
#         "role": "assistant",
#         "content": "🌿 Hello — I'm ConsciousCart. Tell me a brand or product and I'll check its cruelty-free status using trusted sources and summarize the evidence.",
#         "tools": []
#     })

# # --- Sidebar ---
# with st.sidebar:
#     st.markdown("## 🧭 ConsciousCart")
#     st.markdown("A quick tool to check cruelty-free signals and summarize evidence.")
#     st.markdown("---")

#     # Collapsible expanders - WHITE background
#     with st.expander("How it works", expanded=True):
#         st.markdown("""
#         • Recognized certifications (Leaping Bunny, PETA)  
#         • Curated cruelty-free databases  
#         • Company policy statements  
#         • Market presence & recent news
#         """)
    
#     with st.expander("Quick tips", expanded=True):
#         st.markdown("""
#         • Ask about a brand (e.g., *Is Maybelline cruelty-free?*)  
#         • I return a confidence estimate + links.  
#         • Use **Start Fresh** to clear the chat history.
#         """)
    
#     st.markdown("---")

#     # Stat cards in sidebar - BEIGE with BLACK text
#     st.markdown("### Snapshot")
#     st.metric("Brands checked", "30+", delta="Updating")
#     st.metric("Confidence", "Varies", delta="Source-dependent")

#     st.markdown("---")

#     # Start Fresh button - BIGGER
#     if st.button("🔄 Start Fresh", key="start-fresh-btn"):
#         st.session_state.messages = []
#         st.session_state.messages.append({
#             "role": "assistant",
#             "content": "🌿 Hello — I'm ConsciousCart. Tell me a brand or product and I'll check its cruelty-free status using trusted sources and summarize the evidence.",
#             "tools": []
#         })
#         st.rerun()

#     st.markdown("---")
#     st.markdown("<div style='font-size:0.9em;color:#ffffff;'>Built with care • DS+X Hackathon</div>", unsafe_allow_html=True)

# # --- Main layout - CENTERED ---
# st.markdown('<div class="page-header">', unsafe_allow_html=True)
# st.markdown("## 🐇 ConsciousCart")
# st.markdown("### *Ethical shopping made simple*")
# st.markdown("</div>", unsafe_allow_html=True)
# st.markdown("---")

# # Centered summary cards - HORIZONTAL ROW
# st.markdown(
#     """
#     <div class="summary-wrap">
#       <div class="summary-card">
#         <div>
#           <div class="title">Brands Saved</div>
#           <div class="value">30+</div>
#         </div>
#         <div class="description">We track brands across certified lists.</div>
#       </div>
#       <div class="summary-card">
#         <div>
#           <div class="title">Confidence</div>
#           <div class="value">Source-based</div>
#         </div>
#         <div class="description">We combine certifications, policies, and market signals.</div>
#       </div>
#       <div class="summary-card">
#         <div>
#           <div class="title">Impact</div>
#           <div class="value">Every query</div>
#         </div>
#         <div class="description">Small choices add up — we help you decide with evidence.</div>
#       </div>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

# # Display chat messages
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         if message.get("tools"):
#             with st.expander("🔎 View checks", expanded=False):
#                 st.markdown("*Details of what I checked:*")
#                 for i, tool_call in enumerate(message["tools"], 1):
#                     st.markdown(f"""
#                     <div class="tool-call">
#                       <div class="tool-name">Step {i}: {tool_call['tool']}</div>
#                       <div class="tool-input">{tool_call['input']}</div>
#                     </div>
#                     """, unsafe_allow_html=True)
#         st.markdown(message["content"])

# # Quick access section - centered, below chat


# # Chat input - CENTERED AND EXTENDED
# if prompt := st.chat_input("What product or brand would you like to check?"):
#     st.session_state.messages.append({"role": "user", "content": prompt, "tools": []})
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     with st.chat_message("assistant"):
#         with st.spinner("Checking trusted sources and summarizing evidence..."):
#             try:
#                 agent = get_agent()
#                 response, tools_used = agent.process_query(prompt)
#                 if tools_used:
#                     with st.expander("🔎 View checks", expanded=True):
#                         st.markdown("*Details of what I checked:*")
#                         for i, tool_call in enumerate(tools_used, 1):
#                             st.markdown(f"""
#                             <div class="tool-call">
#                               <div class="tool-name">Step {i}: {tool_call['tool']}</div>
#                               <div class="tool-input">{tool_call['input']}</div>
#                             </div>
#                             """, unsafe_allow_html=True)
#                 st.markdown(response)
#                 st.session_state.messages.append({"role": "assistant", "content": response, "tools": tools_used})
#             except Exception as e:
#                 error_msg = f"An error occurred: {str(e)}"
#                 st.error(error_msg)
#                 st.session_state.messages.append({"role": "assistant", "content": error_msg, "tools": []})




"""
ConsciousCart - Enhanced UI with Confidence Scoring & Analytics
Shows verification confidence and agent decision-making stats
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from agent import ConsciousCartAgent

# Page config
st.set_page_config(
    page_title="ConsciousCart 🐰",
    page_icon="🐰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Kraft paper background */
    .stApp {
        background: linear-gradient(135deg, #e8dcc8 0%, #f5ede1 50%, #e8dcc8 100%);
    }
    
    .main {
        background: none;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        border: 1px solid #c4b5a0 !important;
        padding: 15px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        margin: 8px 0 !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #4a3f35 !important;
        font-weight: 600 !important;
    }
    
    h1 {
        text-align: center !important;
        margin-bottom: 5px !important;
    }
    
    /* FORCE ALL TEXT TO BE DARK - FIX WHITE TEXT */
    * {
        color: #4a3f35 !important;
    }
    
    /* Sidebar - force dark text */
    section[data-testid="stSidebar"] * {
        color: #4a3f35 !important;
    }
    
    /* All paragraph and list text */
    p, li, span, div, label {
        color: #4a3f35 !important;
    }
    
    /* Markdown content */
    .stMarkdown, .stMarkdown * {
        color: #4a3f35 !important;
    }
    
    /* Tool call boxes */
    .tool-call {
        background: linear-gradient(135deg, #f9f5f0 0%, #fefcf9 100%);
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 3px solid #7a9b76;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .tool-name {
        font-weight: 600;
        color: #4a3f35;
        font-size: 0.9em;
    }
    
    .tool-input {
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.85em;
        color: #6b5d52;
        margin-top: 6px;
        background: rgba(255,255,255,0.7);
        padding: 8px;
        border-radius: 6px;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5ede1 0%, #e8dcc8 100%) !important;
        border-right: 1px solid #c4b5a0 !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #7a9b76 0%, #8fae8b 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(122, 155, 118, 0.3) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(122, 155, 118, 0.4) !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #4a3f35 !important;
        font-weight: 600 !important;
    }
    
    /* Progress bar text - make it visible */
    .stProgress > div > div > div {
        color: #4a3f35 !important;
        font-weight: 600 !important;
    }
    
    /* Divider */
    hr {
        border-color: #7a9b76 !important;
        opacity: 0.3 !important;
        margin: 15px 0 !important;
    }
    
    /* Subtitle */
    .subtitle {
        color: #6b8167;
        font-size: 0.95em;
        font-style: italic;
        margin-top: 5px;
        margin-bottom: 15px;
        text-align: center;
        font-weight: 500;
    }
    
    /* Profile badge */
    .profile-badge {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        border: 2px solid #7a9b76;
        border-radius: 10px;
        padding: 12px;
        margin: 10px 0;
    }
    
    /* Confidence badge */
    .confidence-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85em;
        margin: 4px 0;
    }
    
    .confidence-high {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .confidence-medium {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .confidence-low {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize agent
if "agent" not in st.session_state:
    st.session_state.agent = ConsciousCartAgent()

agent = st.session_state.agent

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm here to help you discover cruelty-free beauty products. As we talk, I'll learn your preferences to give you personalized recommendations. What product would you like to check?",
        "tools": [],
        "confidence": None
    })

# Main layout
col1, col2 = st.columns([1, 1])

with col1:
    # Header
    st.markdown("""
    <div style="text-align: center;">
        <h1>🐰 ConsciousCart</h1>
        <p class="subtitle">Every purchase is a choice — Choose compassion</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Show confidence score if available
            if message.get("confidence"):
                conf = message["confidence"]
                conf_class = "confidence-high" if conf >= 0.75 else "confidence-medium" if conf >= 0.5 else "confidence-low"
                conf_label = "Very High" if conf >= 0.9 else "High" if conf >= 0.75 else "Medium" if conf >= 0.5 else "Low"
                
                st.markdown(f"""
                <div class="confidence-badge {conf_class}">
                    🎯 Confidence: {conf_label} ({conf:.0%})
                </div>
                """, unsafe_allow_html=True)
            
            # Show tool calls
            if message.get("tools"):
                with st.expander("🔍 Research Process", expanded=False):
                    for i, tool_call in enumerate(message["tools"], 1):
                        st.markdown(f"""
                        <div class="tool-call">
                            <div class="tool-name">Step {i}: {tool_call['tool']}</div>
                            <div class="tool-input">{tool_call['input']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Show message content
            st.markdown(message["content"])
    
    # Chat input
    prompt = st.chat_input("Enter product or brand name...")

    if prompt:
    # if prompt == st.chat_input("Enter product or brand name..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "tools": [],
            "confidence": None
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                try:
                    response, tools_used = agent.process_query(prompt)
                    
                    # Get confidence if available
                    confidence_score = None
                    if agent.last_verification_result:
                        vr = agent.last_verification_result
                        confidence_score = vr.confidence
                        
                        # Display confidence badge
                        conf_class = "confidence-high" if confidence_score >= 0.75 else "confidence-medium" if confidence_score >= 0.5 else "confidence-low"
                        conf_label = vr.get_confidence_label()
                        
                        st.markdown(f"""
                        <div class="confidence-badge {conf_class}">
                            🎯 Confidence: {conf_label} ({confidence_score:.0%})
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show tools used
                    if tools_used:
                        with st.expander("🔍 Research Process", expanded=True):
                            for i, tool_call in enumerate(tools_used, 1):
                                st.markdown(f"""
                                <div class="tool-call">
                                    <div class="tool-name">Step {i}: {tool_call['tool']}</div>
                                    <div class="tool-input">{tool_call['input']}</div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Show response
                    st.markdown(response)
                    
                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "tools": tools_used,
                        "confidence": confidence_score
                    })
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "tools": [],
                        "confidence": None
                    })

with col2:
    # Bunny icon
    st.markdown("""
    <div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
        <div style="font-size: 80px;">🐰</div>
    </div>
    """, unsafe_allow_html=True)
    
    # USER PROFILE SECTION
    st.markdown("## 👤 Your Profile")
    
    profile = agent.user_profile
    
    # Show learned preferences
    if profile.budget_max or profile.values["vegan"] or profile.preferred_brands:
        st.markdown(f"""
        <div class="profile-badge">
            <strong>What I've Learned About You:</strong>
        </div>
        """, unsafe_allow_html=True)
        
        if profile.budget_max:
            st.success(f"💰 Budget: Under ${profile.budget_max}")
        
        if profile.values["vegan"]:
            st.success("🌱 Vegan products only")
        
        if profile.values["fragrance_free"]:
            st.success("🌸 Fragrance-free preferred")
        
        if profile.preferred_brands:
            st.info(f"❤️ You like: {', '.join(list(profile.preferred_brands)[:3])}")
    else:
        st.info("💬 I'm learning your preferences as we chat!")
    
    # Show product history
    if profile.product_history:
        st.markdown("### 📜 Recently Checked")
        for item in profile.product_history[-5:]:
            status = "✓" if item["is_cruelty_free"] else "✗"
            st.text(f"{status} {item['brand']}")
    
    st.markdown("---")
    
    # ANALYTICS DASHBOARD (NEW!)
    st.markdown("## 📊 Agent Analytics")
    
    # Calculate stats
    total_messages = len([m for m in st.session_state.messages if m["role"] == "user"]) - 1
    total_tools = sum(len(m.get("tools", [])) for m in st.session_state.messages)
    avg_tools = total_tools / max(total_messages, 1) if total_messages > 0 else 0
    
    # Show confidence distribution
    confidences = [m.get("confidence") for m in st.session_state.messages if m.get("confidence")]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    # Metrics with emojis
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("🔍 Queries", total_messages)
    with col_b:
        st.metric("⚡ Tool Calls", total_tools)
    with col_c:
        st.metric("📈 Avg Tools", f"{avg_tools:.1f}")
    
    # Confidence meter
    if avg_confidence > 0:
        st.markdown("### 🎯 Verification Confidence")
        st.progress(avg_confidence, text=f"**{avg_confidence:.0%}** Average Confidence")
    
    # Tool usage breakdown
    if total_tools > 0:
        st.markdown("### 🔧 Tool Usage")
        all_tools = []
        for msg in st.session_state.messages:
            for tool in msg.get("tools", []):
                all_tools.append(tool["tool"])
        
        if all_tools:
            tool_counts = {}
            for tool in all_tools:
                tool_counts[tool] = tool_counts.get(tool, 0) + 1
            
            # Add emojis to tool names
            tool_emojis = {
                "check_database": "💾",
                "web_search": "🌐",
                "save_to_database": "💿"
            }
            
            for tool, count in tool_counts.items():
                pct = count / len(all_tools)
                emoji = tool_emojis.get(tool, "🔹")
                tool_display = tool.replace("_", " ").title()
                st.progress(pct, text=f"**{emoji} {tool_display}:** {count}x ({pct:.0%})")
    
    st.markdown("---")
    
    # HOW IT WORKS
    st.markdown("## 🔬 How It Works")
    st.markdown("---")
    
    st.markdown("""
    ### 🤖 Intelligent Agent System
    
    **🧠 Decision Making**
    - Checks database first
    - Searches when needed
    - Evaluates source credibility
    
    **✨ Personalization**
    - Learns your budget
    - Remembers your values
    - Adapts recommendations
    
    **🎯 Confidence Scoring**
    - Multi-source verification
    - Conflict detection
    - Transparency in certainty
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 💬 Try Saying
    
    - 🔍 "Is Maybelline cruelty-free?"
    - 💰 "Too expensive" (I'll learn!)
    - 🌱 "Is it vegan?" (I'll remember!)
    - 💄 "What about foundation?"
    """)
    
    st.markdown("---")
    
    # Impact stats
    st.markdown("### 🌍 Impact")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("🔎 Brands Checked", f"{len(profile.product_history)}")
    with col_b:
        learned = sum([
            1 if profile.budget_max else 0,
            1 if profile.values["vegan"] else 0,
            1 if profile.values["fragrance_free"] else 0
        ])
        st.metric("💡 Learned", learned)
    
    st.markdown("---")
    
    # Clear button
    if st.button("🔄 Clear Chat & Profile", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = ConsciousCartAgent()
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm here to help you discover cruelty-free beauty products. As we talk, I'll learn your preferences to give you personalized recommendations. What product would you like to check?",
            "tools": [],
            "confidence": None
        })
        st.rerun()
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; padding: 15px; color: #5a4d42;'>
        <p style='font-size: 0.9em; margin: 5px 0; font-weight: 600;'>DS+X Hackathon 2025</p>
        <p style='font-size: 0.85em; margin: 5px 0;'>Boston University</p>
    </div>
    """, unsafe_allow_html=True)