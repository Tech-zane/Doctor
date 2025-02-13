import streamlit as st
import streamlit.components.v1 as components
from google import genai
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config first
st.set_page_config(
    page_title="DigiDoc",
    page_icon=":pill:",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# API KEY CONFIGURATION
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    logger.info("API key loaded successfully")
except KeyError:
    st.error("Missing API Key! Configure GEMINI_API_KEY in secrets.")
    st.stop()

# CLIENT INITIALIZATION
genai.configure(api_key=API_KEY)
logger.info("GenAI client initialized successfully")

# CHAT INTERFACE STYLING
chat_css = """
<style>
.user-box {
    background: #0d1b2a;
    padding: 1.2rem;
    border-radius: 15px;
    margin: 1rem 0;
    max-width: 80%;
    float: right;
    color: white;
}
.chatbot-box {
    background: #1a1a1a;
    padding: 1.2rem;
    border-radius: 15px;
    margin: 1rem 0;
    max-width: 80%;
    float: left;
    color: white;
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# CONVERSATION MANAGEMENT
if "conversation" not in st.session_state:
    st.session_state.conversation = []

def manage_conversation(role, text):
    MAX_HISTORY = 10
    st.session_state.conversation.append({"role": role, "text": text})
    while len(st.session_state.conversation) > MAX_HISTORY:
        st.session_state.conversation.pop(0)

# MAIN APP INTERFACE
st.title("🏥 DOC: NDUDZO - Digital Hospital")

# Display conversation history
for message in st.session_state.conversation:
    if message["role"] == "user":
        st.markdown(f'<div class="user-box"><strong>You:</strong> {message["text"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chatbot-box"><strong>Doctor:</strong> {message["text"]}</div>', unsafe_allow_html=True)

# CHAT INPUT SYSTEM
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Describe your symptoms or ask a question:", placeholder="Type your message here...")
    submitted = st.form_submit_button("📩 Send")
    
    if submitted and user_input:
        manage_conversation("user", user_input)
        
        sys_prompt = f"""You are Doctor Ndudzo, an advanced medical AI assistant.
        Current Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}.
        Provide evidence-based medical information. Maintain strict confidentiality.
        Respond in a professional, compassionate tone."""
        
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(user_input)
            
            if response and hasattr(response, 'text'):
                manage_conversation("chatbot", response.text)
            else:
                manage_conversation("chatbot", "I couldn't process that request.")
        
        except Exception as e:
            logger.error(f"API Error: {str(e)}")
            manage_conversation("chatbot", "Technical issue - please try again.")
            
        st.rerun()

# AUTO-SCROLL MECHANISM
components.html(
    """
    <script>
    function scrollToBottom() {
        const container = document.querySelector('.stApp');
        if (container) container.scrollTop = container.scrollHeight;
    }
    window.addEventListener('load', scrollToBottom);
    document.addEventListener('DOMContentLoaded', scrollToBottom);
    </script>
    """,
    height=0
)

# SYSTEM DIAGNOSTICS
with st.expander("⚙️ System Diagnostics", expanded=False):
    st.json({
        "api_connected": True,
        "model": "gemini-2.0-flash",
        "last_update": datetime.now().isoformat(),
        "messages_in_history": len(st.session_state.conversation)
    })
    
    if st.button("🔄 Clear Conversation History"):
        st.session_state.conversation = []
        st.rerun()
