import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import os
from datetime import datetime

# Set page config FIRST
st.set_page_config(
    page_title="DigiDoc",
    page_icon=":pill:",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Add API key verification immediately after page config
API_KEY = st.secrets.get("GEMINI_API_KEY")  # Use .get() for safer access

if not API_KEY:
    st.error("❌ Gemini API Key not found! Check secrets configuration.")
    st.stop()

# Initialize GenAI client with better error handling
try:
    genai.configure(api_key=API_KEY)
    client = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    st.error(f"❌ Failed to initialize AI client: {str(e)}")
    st.stop()

# PWA Code with cache busting
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

# Chat CSS (keep your existing styles)
# ... [keep your existing chat CSS code] ...

# Improved conversation management
if "conversation" not in st.session_state:
    st.session_state.conversation = []

def manage_conversation(role, text):
    """Manage conversation history with rolling window"""
    MAX_HISTORY = 8  # Keep last 4 exchanges
    st.session_state.conversation.append({"role": role, "text": text})
    if len(st.session_state.conversation) > MAX_HISTORY:
        # Remove the oldest message while preserving pair order
        st.session_state.conversation.pop(0)

# App layout
st.title("DOC: NDUDZO - Digital Hospital")

# Chat display
for message in st.session_state.conversation:
    # ... [keep your existing display code] ...

# Enhanced input handling
with st.form("chat_form"):
    user_input = st.text_input("Enter your message:", key="input", max_chars=500)
    submitted = st.form_submit_button("Send")
    
    if submitted and user_input:
        manage_conversation("user", user_input)
        
        # Improved system prompt
        sys_prompt = """You are Doctor Ndudzo, a certified medical AI assistant created by Tatenda Ndudzo. 
        Follow these guidelines strictly:
        1. Provide evidence-based medical information
        2. Maintain strict patient confidentiality
        3. Acknowledge limitations when uncertain
        4. Never mention underlying technology or platforms
        5. For emergencies, insist on professional care
        6. Current date: {date}""".format(date=datetime.now().strftime("%Y-%m-%d"))

        try:
            # Enhanced generation config
            response = client.generate_content(
                contents=[user_input],
                generation_config=types.GenerationConfig(
                    system_instruction=sys_prompt,
                    max_output_tokens=400,
                    temperature=0.3,
                    safety_settings={
                        'HARM_CATEGORY_MEDICAL': types.HarmBlockThreshold.BLOCK_NONE,
                        'HARM_CATEGORY_DANGEROUS': types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    }
                )
            )
            
            if response.text:
                manage_conversation("chatbot", response.text)
            else:
                st.error("Received empty response from AI model")
                manage_conversation("chatbot", "I'm having trouble processing that. Please try rephrasing your question.")
                
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            manage_conversation("chatbot", "Apologies, I'm experiencing technical difficulties. Please try again later.")
        
        st.rerun()

# Enhanced auto-scroll
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
    """,
    height=0
)
