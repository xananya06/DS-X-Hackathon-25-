"""
ConsciousCart - Personalized Agentic UI
Shows user profile and learning in real-time
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from agent import ConsciousCartAgent

# Page config
st.set_page_config(
    page_title="ConsciousCart 🐰",
    page_icon="🐰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Clean and minimal
st.markdown("""
<style>
    /* Kraft paper background */
    .stApp {
        background: linear-gradient(135deg, #e8dcc8 0%, #f5ede1 50%, #e8dcc8 100%);
    }
    
    /* Main content area */
    .main {
        background: none;
    }
    
    /* Reduce padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    
    /* Chat messages - clean white cards */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px !important;
        border: 1px solid #c4b5a0 !important;
        padding: 15px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        margin: 8px 0 !important;
    }
    
    /* Headers - darker brown */
    h1 {
        color: #4a3f35 !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 5px !important;
        text-align: center !important;
    }
    
    h2 {
        color: #5a4d42 !important;
        font-weight: 600 !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        text-align: center !important;
    }
    
    h3 {
        color: #6b5d52 !important;
        font-weight: 500 !important;
        margin-top: 8px !important;
        margin-bottom: 8px !important;
    }
    
    /* Regular text - darker */
    p, li, span {
        color: #4a3f35 !important;
    }
    
    /* Tool call boxes - subtle with green accent */
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
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
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
    
    /* Sidebar - natural kraft */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5ede1 0%, #e8dcc8 100%) !important;
        border-right: 1px solid #c4b5a0 !important;
    }
    
    /* Buttons - sage green */
    .stButton button {
        background: linear-gradient(135deg, #7a9b76 0%, #8fae8b 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(122, 155, 118, 0.3) !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(122, 155, 118, 0.4) !important;
        background: linear-gradient(135deg, #8fae8b 0%, #7a9b76 100%) !important;
    }
    
    /* Input box - clean natural */
    .stChatInputContainer {
        border: 2px solid #c4b5a0 !important;
        border-radius: 12px !important;
        background: white !important;
    }
    
    /* Expander - minimal with green accent */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f9f5f0 0%, #fefcf9 100%) !important;
        border-radius: 10px !important;
        border: 1px solid #7a9b76 !important;
        font-weight: 600 !important;
        color: #4a3f35 !important;
    }
    
    /* Metrics - darker text */
    [data-testid="stMetricValue"] {
        color: #4a3f35 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #5a4d42 !important;
    }
    
    /* Divider - green accent */
    hr {
        border-color: #7a9b76 !important;
        opacity: 0.3 !important;
        margin: 15px 0 !important;
    }
    
    /* Subtitle style - green */
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
    
    /* Center everything in header */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize agent (with session state to persist)
if "agent" not in st.session_state:
    st.session_state.agent = ConsciousCartAgent()

agent = st.session_state.agent

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm here to help you discover cruelty-free beauty products. As we talk, I'll learn your preferences to give you personalized recommendations. What product would you like to check?",
        "tools": []
    })

# Main layout - equal columns
col1, col2 = st.columns([1, 1])

with col1:
    # Clean centered header
    st.markdown("""
    <div class="header-container">
        <h1>🐰 ConsciousCart</h1>
        <p class="subtitle">Every purchase is a choice — Choose compassion</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Show tool calls if any
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
    if prompt := st.chat_input("Enter product or brand name..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "tools": []
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                try:
                    response, tools_used = agent.process_query(prompt)
                    
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
                        "tools": tools_used
                    })
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "tools": []
                    })

with col2:
    # Simple bunny icon
    st.markdown("""
    <div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
        <div style="font-size: 80px;">🐰</div>
    </div>
    """, unsafe_allow_html=True)
    
    # USER PROFILE SECTION (NEW!)
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
        st.markdown("### Recently Checked")
        for item in profile.product_history[-5:]:
            status = "✓" if item["is_cruelty_free"] else "✗"
            st.text(f"{status} {item['brand']}")
    
    st.markdown("---")
    
    st.markdown("## How It Works")
    st.markdown("---")
    
    st.markdown("""
    ### Intelligent Agent System
    
    **Decision Making**
    - Checks database first
    - Searches when needed
    - Evaluates source credibility
    
    **Personalization** 🌟
    - Learns your budget
    - Remembers your values
    - Adapts recommendations
    
    **Multi-Source Verification**
    - Leaping Bunny certification
    - PETA's cruelty-free list
    - Parent company policies
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### Try Saying
    
    - "Is Maybelline cruelty-free?"
    - "Too expensive" (I'll learn!)
    - "Is it vegan?" (I'll remember!)
    - "What about foundation?"
    """)
    
    st.markdown("---")
    
    # Stats
    st.markdown("### Impact")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Brands", f"{len(profile.product_history)}")
    with col_b:
        st.metric("Learned", f"{1 if profile.budget_max else 0}")
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("Clear Chat & Profile", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = ConsciousCartAgent()  # Reset agent
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm here to help you discover cruelty-free beauty products. As we talk, I'll learn your preferences to give you personalized recommendations. What product would you like to check?",
            "tools": []
        })
        st.rerun()
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style='text-align: center; padding: 15px; color: #5a4d42;'>
        <p style='font-size: 0.9em; margin: 5px 0; font-weight: 600;'>DS+X Hackathon 2024</p>
        <p style='font-size: 0.85em; margin: 5px 0;'>Boston University</p>
    </div>
    """, unsafe_allow_html=True)