import streamlit as st
from google import genai
import logging
from datetime import datetime

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
    layout="wide",
    initial_sidebar_state="collapsed"
)

hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        max-width: 100% !important;
        padding: 2rem 1rem !important;
    }
    
    @media (max-width: 600px) {
        .stApp {
            padding: 1rem 0.5rem !important;
        }
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ----------------------
# CUSTOM CHAT STYLING
# ----------------------
chat_css = """
<style>
    .stChatMessage {
        width: 100% !important;
        padding: 0 1rem !important;
    }

    .user-box {
        background: #4CAF50;
        padding: 1.2rem;
        border-radius: 15px 15px 0 15px;
        margin: 1rem 0;
        max-width: 80%;
        margin-left: auto;
        color: white;
        text-align: left;
        word-wrap: break-word;
        white-space: pre-wrap;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }

    .chatbot-box {
        background: #2196F3;
        padding: 1.2rem;
        border-radius: 15px 15px 15px 0;
        margin: 1rem 0;
        max-width: 80%;
        margin-right: auto;
        color: white;
        text-align: left;
        word-wrap: break-word;
        white-space: pre-wrap;
        box-shadow: -2px 2px 5px rgba(0,0,0,0.1);
    }

    .stTextArea textarea {
        min-height: 60px !important;
        max-height: 200px !important;
        overflow-y: auto !important;
        resize: vertical !important;
        line-height: 1.5 !important;
        padding: 12px !important;
    }

    .stTextArea label {
        display: none !important;
    }
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# ----------------------
# API KEY CONFIGURATION
# ----------------------
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
    logger.info("✅ API key loaded successfully.")
except Exception as e:
    st.error(f"❌ API Error: {str(e)}")
    logger.error(f"API Error: {str(e)}")
    st.stop()

# ----------------------
# SESSION STATE MANAGEMENT
# ----------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

def manage_conversation(role, text):
    MAX_HISTORY = 15
    st.session_state.conversation.append({"role": role, "text": text})
    if len(st.session_state.conversation) > MAX_HISTORY:
        st.session_state.conversation = st.session_state.conversation[-MAX_HISTORY:]

# ----------------------
# MAIN INTERFACE
# ----------------------
st.title("\U0001F3E5 DOC: NDUDZO - Digital Hospital")

# ----------------------
# CHAT DISPLAY
# ----------------------
chat_container = st.container()

def display_chat():
    with chat_container:
        for message in st.session_state.conversation:
            if message["role"] == "user":
                st.markdown(f'<div class="user-box"><strong>You:</strong>\n{message["text"]}</div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chatbot-box"><strong>Doctor:</strong>\n{message["text"]}</div>', 
                           unsafe_allow_html=True)

display_chat()

# ----------------------
# CHAT INPUT SYSTEM
# ----------------------
with st.form("chat_form", clear_on_submit=True):
    input_col, btn_col = st.columns([5, 1])
    
    with input_col:
        user_input = st.text_area(
            "Type your message:",
            placeholder="Describe your symptoms or ask a question....",
            label_visibility="collapsed",
            height=100,
            key="input_area"
        )
    
    with btn_col:
        submitted = st.form_submit_button("\U0001F4E9 Send", use_container_width=True)

if submitted and user_input.strip():
    manage_conversation("user", user_input.strip())
    display_chat()
    
    with st.spinner("Doctor Ndudzo is thinking...🩺"):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[{
                    "role": "user",
                    "parts": [f"Current datetime: {datetime.now().isoformat()}\n\n{user_input}"]
                }]
            )
            
            if response.text:
                bot_response = response.text
                manage_conversation("chatbot", bot_response)
            else:
                manage_conversation("chatbot", "I couldn't process that request. Please try again.")
            
        except Exception as e:
            logger.error(f"API Error: {str(e)}")
            manage_conversation("chatbot", "Technical difficulty - please try again shortly.")
    
    display_chat()
    st.rerun()
