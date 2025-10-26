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
    if prompt := st.chat_input("Enter product or brand name..."):
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