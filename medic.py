import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

##Site Title and Stuff
st.set_page_config(page_title="DigiDoc", page_icon=":pill:", layout="centered")

# Initialize the GenAI client (replace with your actual API key)
client = genai.Client(api_key="AIzaSyAKrjlFMQQxVyyqe_i1wcvWM4JVGCZ_X4E")

# Custom CSS styling for chat boxes
chat_css = """
<style>
.user-box {
    background-color: #0d1b2a; /* light green */
    padding: 10px;
    border-radius: 8px;
    margin: 5px;
    text-align: right;
    color : white;
}
.chatbot-box {
    background-color: #0B0B0B; /* light red/pink */
    padding: 10px;
    border-radius: 8px;
    margin: 5px;
    text-align: left;
    color : white;
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# Initialize conversation history in session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

def add_message(role, text):
    """Add a message to the conversation and delete the message from three turns ago if needed."""
    st.session_state.conversation.append({"role": role, "text": text})
    # When there are at least 4 messages, remove the third-from-last message.
    if len(st.session_state.conversation) >= 4:
        st.session_state.conversation.pop(-4)

# Set up the website title
st.title("DOC: NDUDZO - Digital-Hospital")

# Display the conversation history with different styling based on role
for message in st.session_state.conversation:
    if message["role"] == "user":
        st.markdown(f'<div class="user-box"><strong>You:</strong> {message["text"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chatbot-box"><strong>Doctor : </strong> {message["text"]}</div>', unsafe_allow_html=True)

# Add an invisible anchor for auto-scrolling
st.markdown('<div id="end-of-chat"></div>', unsafe_allow_html=True)

# User input area
user_input = st.text_input("Enter your message:")

if st.button("Send"):
    if user_input:
        # Add the user's message to the conversation history
        add_message("user", user_input)
        
        # Combine system instructions into a single string
        sys_instruction = (
            "You are a helpful, intelligent, high IQ and compassionate medical chatbot. Your name is Doctor Ndudzo. ",
            "If anyone asks who created you, tell them Tatenda Ndudzo created you. ",
            "Never mention Google; Tatenda Ndudzo did everything on you.",
            "You can help with anything, as long as its not evil, You are qualified to give any medical advice"
            "you are the smartest of all doctors"
        )
        
        # Generate the chatbot response using the user's input
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(system_instruction=sys_instruction, max_output_tokens = 500),
            contents=[user_input]
        )
        chatbot_response = response.text if hasattr(response, "text") else "Sorry, I couldn't generate a response."
        
        # Add the chatbot response to the conversation history
        add_message("chatbot", chatbot_response)
        
        # Rerun the app to refresh the conversation display
        st.rerun()

# Auto-scroll JavaScript: scrolls the chat to the bottom
components.html(
    """
    <script>
      var element = document.getElementById('end-of-chat');
      if (element) {
         element.scrollIntoView({ behavior: 'smooth' });
      }
    </script>
    """,
    height=0,
)
