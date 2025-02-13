import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import os
from datetime import datetime

# Set page config first
st.set_page_config(
    page_title="DigiDoc",
    page_icon=":pill:",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# API key handling
API_KEY = st.secrets.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ Gemini API Key not found! Check secrets configuration.")
    st.stop()

# Initialize GenAI client
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"❌ Failed to initialize AI client: {str(e)}")
    st.stop()

# PWA implementation
st.markdown(f"""
  <link rel="manifest" href="/static/manifest.json?v={datetime.now().timestamp()}">
  <script>
    if ('serviceWorker' in navigator) {{
      navigator.serviceWorker.register('/static/service-worker.js?v={datetime.now().timestamp()}')
        .then(reg => console.log('SW registered:', reg.scope))
        .catch(err => console.error('SW registration failed:', err));
    }}
  </script>
""", unsafe_allow_html=True)

# Chat interface styling
chat_css = """
<style>
.user-box {
    background-color: #0d1b2a;
    padding: 1rem;
    border-radius: 15px;
    margin: 0.5rem 0;
    max-width: 80%;
    float: right;
    clear: both;
    color: white;
}
.chatbot-box {
    background-color: #0B0B0B;
    padding: 1rem;
    border-radius: 15px;
    margin: 0.5rem 0;
    max-width: 80%;
    float: left;
    clear: both;
    color: white;
}
@media (max-width: 768px) {
    .user-box, .chatbot-box {
        max-width: 90%;
    }
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# Conversation management
if "conversation" not in st.session_state:
    st.session_state.conversation = []

def manage_conversation(role, text):
    """Maintain conversation history with rolling window"""
    MAX_HISTORY = 8  # Keep last 4 exchanges
    st.session_state.conversation.append({"role": role, "text": text})
    if len(st.session_state.conversation) > MAX_HISTORY:
        st.session_state.conversation.pop(0)

# App interface
st.title("DOC: NDUDZO - Digital Hospital")

# Display conversation
for message in st.session_state.conversation:
    if message["role"] == "user":
        st.markdown(f'<div class="user-box"><strong>You:</strong> {message["text"]}</div>', 
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chatbot-box"><strong>Doctor:</strong> {message["text"]}</div>', 
                    unsafe_allow_html=True)

# Chat input form
with st.form("chat_form"):
    user_input = st.text_input("Enter your message:", key="input", max_chars=500)
    submitted = st.form_submit_button("Send")
    
    if submitted and user_input:
        manage_conversation("user", user_input)
        
        # System instructions
        sys_prompt = """You are Doctor Ndudzo, a certified medical AI assistant created by Tatenda Ndudzo.
        Follow these guidelines strictly:
        1. Provide evidence-based medical information
        2. Maintain patient confidentiality
        3. Acknowledge knowledge limitations
        4. Never mention technical platforms
        5. Advise professional care for emergencies
        6. Current date: {date}""".format(date=datetime.now().strftime("%Y-%m-%d"))

        try:
            # Generate response
            response = client.models.generate_content(
                model='gemini-pro',
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt,
                    max_output_tokens=400,
                    temperature=0.3,
                    safety_settings={
                        'HARM_CATEGORY_MEDICAL': types.HarmBlockThreshold.BLOCK_NONE,
                        'HARM_CATEGORY_DANGEROUS': types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    }
                ),
                contents=[user_input]
            )
            
            if response.text:
                manage_conversation("chatbot", response.text)
            else:
                st.error("Received empty response from AI model")
                manage_conversation("chatbot", "I'm having trouble processing that. Please try rephrasing.")
                
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            manage_conversation("chatbot", "Apologies, technical difficulties. Please try again.")
        
        st.rerun()

# Auto-scroll functionality
components.html(
    """
    <script>
    function scrollToBottom() {
        var element = document.getElementById('end-of-chat');
        if (element) element.scrollIntoView({behavior: 'smooth', block: 'end'});
    }
    window.addEventListener('load', scrollToBottom);
    window.addEventListener('DOMContentLoaded', scrollToBottom);
    </script>
    <div id="end-of-chat"></div>
    """,
    height=0
)
