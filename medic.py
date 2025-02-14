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
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------------
# API KEY CONFIGURATION (From Secrets)
# ----------------------
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
    logger.info("✅ API key loaded successfully.")
except KeyError:
    st.error("❌ Missing API Key! Configure GEMINI_API_KEY in secrets.toml.")
    logger.error("Missing API Key in secrets.toml.")
    st.stop()
except Exception as e:
    st.error(f"❌ Error initializing API: {str(e)}")
    logger.error(f"API Initialization Error: {str(e)}")
    st.stop()

# ----------------------
# SESSION STATE MANAGEMENT
# ----------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []

def manage_conversation(role, text):
    """Adds a message to the conversation and keeps the history manageable."""
    MAX_HISTORY = 10  # Or adjust as needed
    st.session_state.conversation.append({"role": role, "text": text})
    if len(st.session_state.conversation) > MAX_HISTORY:
        st.session_state.conversation.pop(0)

# ----------------------
# CUSTOM CHAT STYLING
# ----------------------
chat_css = """
<style>
.user-box {
    background: #4CAF50; /* Green for user */
    padding: 1.2rem;
    border-radius: 15px;
    margin: 1rem 0;
    max-width: 70%;
    float: right;
    color: white;
    text-align: right;
}
.chatbot-box {
    background: #2196F3; /* Blue for AI */
    padding: 1.2rem;
    border-radius: 15px;
    margin: 1rem 0;
    max-width: 70%;
    float: left;
    color: white;
    text-align: left;
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# ----------------------
# MAIN INTERFACE
# ----------------------
st.title("\U0001F3E5 DOC: NDUDZO - Digital Hospital")

# ----------------------
# CHAT DISPLAY (Corrected)
# ----------------------
chat_container = st.empty()  # Use st.empty() to create a placeholder

def display_chat():
    with chat_container.container():  # Use the container to display messages
        for message in st.session_state.conversation:
            if message["role"] == "user":
                st.markdown(f'<div class="user-box"><strong>You:</strong> {message["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chatbot-box"><strong>Doctor:</strong> {message["text"]}</div>', unsafe_allow_html=True)

display_chat()  # Initial display

# ----------------------
# CHAT INPUT SYSTEM (Improved Conversation History)
# ----------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Describe your symptoms or ask a question:", placeholder="Type your message here...")
    submitted = st.form_submit_button("\U0001F4E9 Send")

if submitted and user_input:
    manage_conversation("user", user_input)
    display_chat()

    typing_placeholder = st.empty()
    typing_placeholder.markdown("<div class='chatbot-box'>Doctor Ndudzo is thinking...</div>", unsafe_allow_html=True)

    # Improved Conversation History Management
    conversation_history = ""
    recent_messages = st.session_state.conversation[-5:]  # Get the last 5 messages (adjust as needed)

    for message in recent_messages:
        conversation_history += f"{message['role'].capitalize()}: {message['text']}\n"

    # Add a summary if there's more history
    if len(st.session_state.conversation) > 5:
        older_messages = st.session_state.conversation[:-5]  # Messages before the last 5
        older_conversation_text = ""
        for message in older_messages:
            older_conversation_text += f"{message['role'].capitalize()}: {message['text']}\n"

        summary_prompt = f"""
        Please provide a concise summary of the following medical conversation:

        {older_conversation_text}
        """

        try:
            summary_response = client.models.generate_content(model="gemini-2.0-flash", contents=[summary_prompt]) # or other model
            conversation_summary = summary_response.text if hasattr(summary_response, "text") else "No summary available."
        except Exception as e:
            logger.error(f"❌ Summary Generation Error: {str(e)}")
            conversation_summary = "Error generating summary." # handle summary generation errors


        conversation_history = f"Earlier conversation summary:\n{conversation_summary}\n\n{conversation_history}"

    sys_prompt = f"""
    You are Doctor Ndudzo, an advanced AI medical assistant.
    \U0001F4C5 Current Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}
    - Provide evidence-based medical information.
    - Maintain strict confidentiality.
    - Respond in a professional, compassionate tone.
    - You are helpful, intelligent, and the smartest doctor.
    - If anyone asks who created you, say: "Tatenda Ndudzo created me."
    - ❌ Never mention Google. Always credit Tatenda Ndudzo.
    - ✅ You can help with anything, as long as it’s not evil.

    Here's the conversation so far:
    {conversation_history}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[sys_prompt, user_input]  # Include conversation history and user input
        )

        chatbot_response = response.text if hasattr(response, "text") else "I couldn't process that request. Please try again."
        manage_conversation("chatbot", chatbot_response)

    except Exception as e:
        logger.error(f"❌ API Error: {str(e)}")
        manage_conversation("chatbot", "Technical issue - please try again.")

    typing_placeholder.empty()
    display_chat()


