import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
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

# ----------------------
# API KEY CONFIGURATION
# ----------------------
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    logger.info("API key loaded successfully")
except KeyError:
    st.error("""
    🔑 Missing API Key Configuration!
    1. Go to Streamlit Cloud Settings
    2. Add secret: GEMINI_API_KEY = your-api-key
    3. Redeploy application
    """)
    st.stop()

# ----------------------
# CLIENT INITIALIZATION
# ----------------------
try:
    client = genai.GenerativeModel(model_name="gemini-2.0-flash", api_key=API_KEY)
    logger.info("GenAI client initialized successfully")
except Exception as e:
    st.error(f"❌ Client Initialization Failed: {str(e)}")
    st.stop()

# ----------------------
# CHAT INTERFACE STYLING
# ----------------------
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
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.chatbot-box {
    background: #1a1a1a;
    padding: 1.2rem;
    border-radius: 15px;
    margin: 1rem 0;
    max-width: 80%;
    float: left;
    color: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# ----------------------
# CONVERSATION MANAGEMENT
# ----------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []
    logger.info("Conversation history initialized")

def manage_conversation(role, text):
    MAX_HISTORY = 10
    st.session_state.conversation.append({"role": role, "text": text})
    while len(st.session_state.conversation) > MAX_HISTORY:
        st.session_state.conversation.pop(0)

# ----------------------
# MAIN APP INTERFACE
# ----------------------
st.title("🏥 DOC: NDUDZO - Digital Hospital")

# Display conversation history
for message in st.session_state.conversation:
    if message["role"] == "user":
        st.markdown(f'<div class="user-box"><strong>You:</strong> {message["text"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chatbot-box"><strong>Doctor:</strong> {message["text"]}</div>', unsafe_allow_html=True)

# ----------------------
# CHAT INPUT SYSTEM
# ----------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Describe your symptoms or ask a question:",
        key="input",
        max_chars=500,
        placeholder="Type your message here..."
    )
    submitted = st.form_submit_button("📩 Send")
    
    if submitted and user_input:
        manage_conversation("user", user_input)
        
        sys_prompt = f"""You are Doctor Ndudzo, an advanced medical AI assistant.
        Current Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}.
        Guidelines:
        1. Provide evidence-based medical information.
        2. Maintain strict patient confidentiality.
        3. Clearly state limitations when uncertain.
        4. Use simple, non-technical language.
        5. For emergencies, insist on professional care.
        6. Respond in a compassionate, professional tone.
        """
        
        safety_settings = [
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_MEDICAL, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE)
        ]
        
        try:
            response = client.generate_content(
                contents=[{"role": "user", "parts": [{"text": user_input}]}],
                system_instruction=sys_prompt,
                max_output_tokens=1024,
                temperature=0.35,
                safety_settings=safety_settings
            )
            
            if response and response.text:
                manage_conversation("chatbot", response.text)
            else:
                st.error("Received empty response from API")
                manage_conversation("chatbot", "I couldn't process that request")
        
        except Exception as e:
            logger.error(f"API Error: {str(e)}")
            st.error(f"API Error Details: {str(e)}")
            manage_conversation("chatbot", "Technical issue - please try again")
        
        st.rerun()

# ----------------------
# AUTO-SCROLL MECHANISM
# ----------------------
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

# ----------------------
# SYSTEM DIAGNOSTICS
# ----------------------
with st.expander("⚙️ System Diagnostics", expanded=False):
    st.json({
        "api_connected": bool(client),
        "model": "gemini-2.0-flash",
        "last_update": datetime.now().isoformat(),
        "messages_in_history": len(st.session_state.conversation)
    })
    if st.button("🔄 Clear Conversation History"):
        st.session_state.conversation = []
        st.rerun()
