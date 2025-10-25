"""
ConsciousCart - Agentic UI
Cute, colorful design for animal welfare
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from agent import ConsciousCartAgent

# Page config
st.set_page_config(
    page_title="ConsciousCart",
    page_icon="🐇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Cute, light, animal-themed
st.markdown("""

""", unsafe_allow_html=True)

# Initialize agent
@st.cache_resource
def get_agent():
    return ConsciousCartAgent()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello — I'm ConsciousCart. Tell me a brand or product and I'll check its cruelty-free status using trusted sources and explain the evidence I found.",
        "tools": []
    })

# Main layout with two columns
col1, col2 = st.columns([2, 1])

with col1:
    # Neutral header
    st.markdown("# ConsciousCart")
    st.markdown("### *Ethical shopping made simple*")
    st.markdown("---")
   
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Show tool calls if any
            if message.get("tools"):
                with st.expander("See details of my checks", expanded=False):
                    st.markdown("*Here's what I looked up:*")
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
    if prompt := st.chat_input("What product or brand would you like to check?"):
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
            with st.spinner("Checking trusted sources and summarizing evidence..."):
                try:
                    agent = get_agent()
                    response, tools_used = agent.process_query(prompt)
                    
                    # Show tools used
                    if tools_used:
                        with st.expander("See details of my checks", expanded=True):
                            st.markdown("*Here's what I looked up:*")
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
                    error_msg = f"An error occurred: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "tools": []
                    })             
with col2:
    # Neutral sidebar content
    st.markdown("## How it works")
    
    st.markdown("""
    **ConsciousCart checks reputable signals to estimate cruelty-free status:**
    
    - Recognized certifications (Leaping Bunny, PETA)  
    - Curated cruelty-free databases  
    - Public company policy statements  
    - Market presence that may imply testing requirements  
    - Recent news and ownership changes
    """)
    
    st.markdown("---")
    
    st.markdown("### Quick tips")
    st.markdown("""
    - Ask about a brand (e.g., *"Is Maybelline cruelty-free?"*).  
    - I provide a confidence estimate and links to sources.  
    - Use *Start Fresh* to clear the conversation history.
    """)
    
    st.markdown("---")
    
    # Clean stats box
    with st.container():
        st.markdown("### Summary")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Brands checked", "30+", delta="Updating")
        with col_b:
            st.metric("Confidence", "Varies", delta="Source-dependent")
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("Start Fresh", use_container_width=True):
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello — I'm ConsciousCart. Tell me a brand or product and I'll check its cruelty-free status using trusted sources and explain the evidence I found.",
            "tools": []
        })
        st.rerun()
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p style='font-size: 1em; margin: 0;'>Built with care</p>
        <p style='font-size: 0.9em; margin: 0; color: #6b5a47;'>DS+X Hackathon</p>
        <p style='font-size: 0.85em; margin-top: 8px; color: #6b5a47;'>Every purchase matters — choose thoughtfully.</p>
    </div>
    """, unsafe_allow_html=True)