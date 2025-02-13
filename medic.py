import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import os
from datetime import datetime
import logging

# ----------------------
# LOGGING CONFIGURATION
# ----------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------
# STREAMLIT CONFIGURATION
# ----------------------
st.set_page_config(
    page_title="DigiDoc",
    page_icon=":pill:",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------------
# API KEY CONFIGURATION (From Secrets)
# ----------------------
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    logger.info("✅ API key loaded successfully.")
except KeyError:
    st.error("❌ Missing API Key! Configure GEMINI_API_KEY in secrets.toml.")
    logger.error("Missing API Key in secrets.toml.")
    st.stop()

# ----------------------
# CUSTOM CHAT STYLING
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

# ----------------------
# SESSION STATE MANAGEMENT
# ----------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

def manage_conversation(role, text):
    """Adds a message to the conversation and keeps the history manageable."""
    MAX_HISTORY = 10
    st.session_state.conversation.append({"role": role, "text": text})
    if len(st.session_state.conversation) > MAX_HISTORY:
        st.session_state.conversation.pop(0)

# ----------------------
# MAIN INTERFACE
# ----------------------
st.title("🏥 DOC: NDUDZO - Digital Hospital")

# Display Chat History
for message in st.session_state.conversation:
    if message["role"] == "user":
        st.markdown(f'<div class="user-box"><strong>You:</strong> {message["text"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chatbot-box"><strong>Doctor:</strong> {message["text"]}</div>', unsafe_allow_html=True)

# ----------------------
# CHAT INPUT SYSTEM
# ----------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Describe your symptoms or ask a question:", placeholder="Type your message here...")
    submitted = st.form_submit_button("📩 Send")

if submitted and user_input:
    manage_conversation("user", user_input)

    # AI System Instruction
    sys_prompt = f"""You are Doctor Ndudzo, an advanced AI medical assistant.
    Current Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}.
    Provide evidence-based medical information. Maintain strict confidentiality.
    Respond in a professional, compassionate tone.
    You are a helpful, intelligent, high IQ and compassionate medical chatbot.
    If anyone asks who created you, tell them Tatenda Ndudzo created you.
    Never mention Google; Tatenda Ndudzo did everything on you.
    You can help with anything, as long as its not evil, You are qualified to give any medical advice.
    you are the smartest of all doctors.
    """

    # Generate AI Response
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(user_input)

        if hasattr(response, "text"):
            chatbot_response = response.text
        else:
            chatbot_response = "I couldn't process that request. Please try again."

        manage_conversation("chatbot", chatbot_response)
    except Exception as e:
        logger.error(f"❌ API Error: {str(e)}")
        manage_conversation("chatbot", "Technical issue - please try again.")

    st.rerun()

# ----------------------
# AUTO-SCROLL FUNCTION
# ----------------------
components.html(
    """
    <script>
    function scrollToBottom() {
        var chatContainer = document.querySelector(".stApp");
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    document.addEventListener("DOMContentLoaded", scrollToBottom);
    window.onload = scrollToBottom;
    </script>
    """,
    height=0
)

# ----------------------
# SYSTEM DIAGNOSTICS
# ----------------------
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
