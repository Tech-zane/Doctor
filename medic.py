import streamlit as st
from google import genai
import logging
from datetime import datetime
from functools import wraps

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

# ----------------------
# CUSTOM STYLING
# ----------------------
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
</style>
"""

st.markdown(hide_streamlit_style + chat_css, unsafe_allow_html=True)

# ----------------------
# API CONFIGURATION
# ----------------------
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
    logger.info("✅ API configured successfully")
except Exception as e:
    st.error("🔴 Critical system error: Failed to initialize medical AI")
    logger.critical(f"API Init Failure: {str(e)}")
    st.stop()

# ----------------------
# SESSION MANAGEMENT
# ----------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

def manage_conversation(role: str, text: str):
    MAX_HISTORY = 20
    st.session_state.conversation.append({"role": role, "text": text})
    if len(st.session_state.conversation) > MAX_HISTORY:
        st.session_state.conversation = st.session_state.conversation[-MAX_HISTORY:]

# ----------------------
# ERROR HANDLING
# ----------------------
def handle_api_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except genai.types.BlockedPromptException as e:
            logger.warning(f"Content safety block: {str(e)}")
            return "I can't discuss that due to medical ethics guidelines. Please ask about health-related topics."
        except genai.types.StopCandidateException as e:
            logger.error(f"Generation stopped: {str(e)}")
            return "My response was interrupted. Please repeat your question."
        except PermissionError as e:
            logger.critical(f"Auth error: {str(e)}")
            return "System authentication failed. Technical team has been alerted."
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return "Temporary system overload. Please try again shortly."
    return wrapper

# ----------------------
# CORE FUNCTIONALITY
# ----------------------
@handle_api_errors
def generate_medical_response(prompt: str) -> str:
    """Generate AI response with medical safety checks"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[{
            "role": "user",
            "parts": [f"{datetime.now().isoformat()}\n\n{prompt}"]
        }],
        safety_settings={
            'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH'
        },
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 1500
        }
    )
    
    if response.prompt_feedback.block_reason:
        raise genai.types.BlockedPromptException(
            f"Blocked reason: {response.prompt_feedback.block_reason}"
        )
    
    return response.text if response.text else "Couldn't process that query. Please rephrase."

# ----------------------
# UI COMPONENTS
# ----------------------
st.title("🏥 DOC: NDUDZO - Digital Hospital")

# Chat Display
chat_container = st.container()
def display_chat():
    with chat_container:
        for msg in st.session_state.conversation:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-box"><strong>You:</strong>\n{msg["text"]}</div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chatbot-box"><strong>Dr. Ndudzo:</strong>\n{msg["text"]}</div>', 
                           unsafe_allow_html=True)

# Chat Input
with st.form("chat_form", clear_on_submit=True):
    input_col, btn_col = st.columns([5, 1])
    
    with input_col:
        user_input = st.text_area(
            "Medical query input:",
            placeholder="Describe symptoms or ask health questions...\n(Shift+Enter for new line)",
            label_visibility="collapsed",
            height=100,
            key="medical_input"
        )
    
    with btn_col:
        submitted = st.form_submit_button("📤 Send", use_container_width=True)

# ----------------------
# CHAT PROCESSING
# ----------------------
if submitted and user_input.strip():
    manage_conversation("user", user_input.strip())
    display_chat()
    
    with st.spinner("🔍 Analyzing symptoms..."):
        try:
            if len(user_input) > 2000:
                raise ValueError("Excessive input length")
                
            bot_response = generate_medical_response(user_input)
            manage_conversation("chatbot", bot_response)
            
        except ValueError:
            error_msg = "Please limit queries to 2000 characters for accurate analysis."
            manage_conversation("chatbot", error_msg)
            
        except Exception as e:
            error_msg = "Medical system busy. Please try again in 1 minute."
            manage_conversation("chatbot", error_msg)
    
    display_chat()
    st.rerun()
elif submitted:
    st.warning("Please enter a medical query before sending")

# Initial display
display_chat()
