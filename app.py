
"""
ConsciousCart - Agentic UI
Cute, colorful design for animal welfare
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from agent import ConsciousCartAgent

# Page config
st.set_page_config(
    page_title="ConsciousCart",
    page_icon="🐇",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Cute, light, animal-themed
st.markdown("""
<style>
    /* Main background - soft cream */
    .stApp {
        background: linear-gradient(135deg, #fef9f3 0%, #fef5eb 100%);
    }
    
    /* Chat messages - lighter pastels */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 20px !important;
        border: 2px solid #ffd4e5 !important;
        padding: 15px !important;
    }
    
    /* User messages - soft pink */
    [data-testid="stChatMessageContent"][data-role="user"] {
        background: linear-gradient(135deg, #ffe0f0 0%, #fff0f7 100%) !important;
        border-color: #ffb3d9 !important;
    }
    
    /* Assistant messages - soft mint */
    [data-testid="stChatMessageContent"][data-role="assistant"] {
        background: linear-gradient(135deg, #e6fff2 0%, #f0fff7 100%) !important;
        border-color: #b3f0d9 !important;
    }
    
    /* Tool call boxes - cute lavender */
    .tool-call {
        background: linear-gradient(135deg, #f0e6ff 0%, #f7f0ff 100%);
        padding: 12px;
        border-radius: 15px;
        margin: 8px 0;
        border-left: 4px solid #d4b3ff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .tool-name {
        font-weight: bold;
        color: #8b5cf6;
        font-size: 0.9em;
    }
    
    .tool-input {
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.85em;
        color: #6b7280;
        margin-top: 4px;
        background: rgba(255,255,255,0.6);
        padding: 6px;
        border-radius: 8px;
    }
    
    /* Sidebar - soft peach */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fff5f0 0%, #ffe8e0 100%) !important;
    }
    
    /* Headers - warm colors */
    h1 {
        color: #ff6b9d !important;
        text-shadow: 2px 2px 4px rgba(255,182,193,0.3);
    }
    
    h2, h3 {
        color: #ff8fab !important;
    }
    
    /* Buttons - cute pink */
    .stButton button {
        background: linear-gradient(135deg, #ff9ebb 0%, #ffb3d4 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 6px rgba(255,107,157,0.3) !important;
        transition: all 0.3s !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 8px rgba(255,107,157,0.4) !important;
    }
    
    /* Input box - soft border */
    .stChatInputContainer {
        border: 2px solid #ffd4e5 !important;
        border-radius: 25px !important;
        background: white !important;
    }
    
    /* Expander - cute style */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #fff0f7 0%, #ffe8f5 100%) !important;
        border-radius: 15px !important;
        border: 2px solid #ffd4e5 !important;
        font-weight: bold !important;
        color: #ff6b9d !important;
    }
    
    /* Divider */
    hr {
        border-color: #ffd4e5 !important;
        opacity: 0.5 !important;
    }
    
    /* Captions - softer */
    .caption {
        color: #ff8fab !important;
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
        "content": "Hey friend! 🐰💕 I'm here to help you shop cruelty-free! Just tell me what beauty product you're curious about, and I'll check if it's kind to our furry friends. Let's make ethical choices together! ✨",
        "tools": []
    })

# Main layout with two columns
col1, col2 = st.columns([2, 1])

with col1:
    # Cute header
    st.markdown("# 🐰 ConsciousCart")
    st.markdown("### *Where Every Purchase Protects Our Friends* 💚")
    st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Show tool calls if any
            if message.get("tools"):
                with st.expander("🔧 See what I did behind the scenes!", expanded=False):
                    st.markdown("*My agent brain was busy! Here's what I checked:*")
                    for i, tool_call in enumerate(message["tools"], 1):
                        st.markdown(f"""
                        <div class="tool-call">
                            <div class="tool-name">🔍 Step {i}: {tool_call['tool']}</div>
                            <div class="tool-input">{tool_call['input']}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Show message content
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("💭 What product do you want to check?"):
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
            with st.spinner("🤔 Thinking... checking my database and searching the web..."):
                try:
                    agent = get_agent()
                    response, tools_used = agent.process_query(prompt)
                    
                    # Show tools used
                    if tools_used:
                        with st.expander("🔧 See what I did behind the scenes!", expanded=True):
                            st.markdown("*My agent brain was busy! Here's what I checked:*")
                            for i, tool_call in enumerate(tools_used, 1):
                                st.markdown(f"""
                                <div class="tool-call">
                                    <div class="tool-name">🔍 Step {i}: {tool_call['tool']}</div>
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
                    error_msg = f"Oops! 🙈 Something went wrong: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "tools": []
                    })

with col2:
    # Cute sidebar content
    st.markdown("## 💝 How It Works")
    
    st.markdown("""
    ### 🤖 Smart Agent System
    
    I'm not just a chatbot - I'm an intelligent agent! 🧠
    
    **🌟 I Make Decisions:**
    - Check my database first 📚
    - Search the web when needed 🔍
    - Learn which sources to trust ✨
    
    **🛠️ I Use Tools:**
    - `check_database` - My memory!
    - `web_search` - Internet detective
    - `save_to_database` - I remember!
    
    **💭 I Reason & Learn:**
    - Compare multiple sources
    - Get smarter with each question
    - Always explain my thinking
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🎯 What I Check
    
    🐰 Leaping Bunny certification  
    🐾 PETA's cruelty-free list  
    🏢 Parent company policies  
    🌏 China market sales  
    📰 Recent policy changes  
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 💡 Try These!
    
    *Ask me about:*
    
    - "Is Maybelline cruelty-free?"
    - "What about Fenty Beauty?"
    - "I use MAC lipstick"
    - "e.l.f. cosmetics?"
    - "Pacifica products"
    """)
    
    st.markdown("---")
    
    # Cute stats box
    with st.container():
        st.markdown("### 📊 My Stats")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("🐰 Brands Saved", "30+", delta="Growing!")
        with col_b:
            st.metric("💚 Animals Helped", "∞", delta="Every query!")
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Start Fresh", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = ConsciousCartAgent()
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hey friend! 🐰💕 I'm here to help you shop cruelty-free! Just tell me what beauty product you're curious about, and I'll check if it's kind to our furry friends. Let's make ethical choices together! ✨",
            "tools": []
        })
        st.rerun()
    
    st.markdown("---")
    
    # Cute footer
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <p style='font-size: 1.2em;'>🐰 Built with 💕</p>
        <p style='color: #ff8fab;'>DS+X Hackathon 2024</p>
        <p style='font-size: 0.9em;'>Every purchase is a vote 🗳️<br/>
        Let's vote for kindness! 🌸</p>
    </div>
    """, unsafe_allow_html=True)