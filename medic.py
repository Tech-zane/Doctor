import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types
import os  # Added for environment variables

st.set_page_config(
    page_title="DigiDoc",
    page_icon=":pill:",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. THEN ADD PWA CODE
st.markdown("""
  <link rel="manifest" href="/static/manifest.json">
  <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/static/service-worker.js', { scope: '/' })
        .then(registration => {
          console.log('ServiceWorker registered with scope:', registration.scope);
          registration.addEventListener('updatefound', () => window.location.reload());
        })
        .catch(error => console.error('ServiceWorker registration failed:', error));
    }
  </script>
""", unsafe_allow_html=True)

# Initialize GenAI client securely (use environment variables)
API_KEY = os.getenv("GEMINI_API_KEY")  # Move to secrets.toml
client = genai.Client(api_key=API_KEY)

# Enhanced chat CSS with responsive design
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

# Session state management
if "conversation" not in st.session_state:
    st.session_state.conversation = []

def manage_conversation(role, text):
    """Manage conversation history with rolling window"""
    MAX_HISTORY = 6  # Keep last 3 exchanges
    st.session_state.conversation.append({"role": role, "text": text})
    if len(st.session_state.conversation) > MAX_HISTORY:
        st.session_state.conversation = st.session_state.conversation[-MAX_HISTORY:]

# App layout
st.title("DOC: NDUDZO - Digital Hospital")

# Chat display
for message in st.session_state.conversation:
    if message["role"] == "user":
        st.markdown(f'<div class="user-box"><strong>You:</strong> {message["text"]}</div>', 
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chatbot-box"><strong>Doctor:</strong> {message["text"]}</div>', 
                    unsafe_allow_html=True)

# Input area with safety controls
with st.form("chat_form"):
    user_input = st.text_input("Enter your message:", key="input", max_chars=500)
    submitted = st.form_submit_button("Send")
    
    if submitted and user_input:
        # Add user message
        manage_conversation("user", user_input)
        
        # Enhanced system prompt
        sys_prompt = (
            "You are Doctor Ndudzo, a highly intelligent medical AI assistant created by Tatenda Ndudzo. "
            "Follow these guidelines strictly:\n"
            "1. Provide evidence-based medical information\n"
            "2. Always maintain patient confidentiality\n"
            "3. Clarify when information is beyond your knowledge\n"
            "4. Never mention Google or other third-party platforms\n"
            "5. For emergencies, advise seeking immediate professional care\n"
            "6. Maintain compassionate and professional tone"
        )
        
        try:
            # Generate response
            response = client.models.generate_content(
                model='gemini-pro',
                config=types.GenerateContentConfig(
                    system_instruction=sys_prompt,
                    max_output_tokens=300,
                    temperature=0.7,
                    safety_settings={
                        'HARM_CATEGORY_MEDICAL': types.HarmBlockThreshold.BLOCK_NONE,
                    }
                ),
                contents=[user_input]
            )
            
            if response.text:
                manage_conversation("chatbot", response.text)
            else:
                manage_conversation("chatbot", "I'm having trouble processing that. Please try again.")
                
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            manage_conversation("chatbot", "Apologies, I'm experiencing technical difficulties. Please try again later.")
        
        st.rerun()

# Auto-scroll implementation
components.html(
    """
    <script>
    window.addEventListener('load', function() {
        var element = document.getElementById('end-of-chat');
        if (element) element.scrollIntoView({behavior: 'smooth'});
    });
    </script>
    """,
    height=0
)
