import streamlit as st
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()

# Set page configuration for better mobile experience
st.set_page_config(
    page_title="Women's Health Assistant",
    page_icon="💜",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better mobile experience
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        padding: 0.5rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        padding: 0.3rem;
        background-color: #FF69B4;
        color: white;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #F0F0F0;
    }
    .chat-message.assistant {
        background-color: #FFE6F2;
    }
    .chat-message .message-content {
        display: flex;
        margin-top: 0.5rem;
    }
    .chat-message .avatar {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.5rem;
    }
    .chat-message.user .avatar {
        background-color: #6E7A95;
        color: white;
    }
    .chat-message.assistant .avatar {
        background-color: #FF69B4;
        color: white;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #888;
        font-style: italic;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("Women's Health Assistant")
st.markdown("Ask questions about women's health, wellness, and self-care.")

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""

# Function to generate LLM response
def generate_response(prompt, history):
    # System prompt to guide the model
    system_prompt = """
    You are a helpful assistant focused on women's health information. Provide accurate, 
    empathetic, and informative responses about women's health topics including but not limited to:
    - Reproductive health
    - Menstrual health
    - Pregnancy and postpartum care
    - Menopause
    - General wellness and preventive care
    - Mental health
    
    Always clarify that you're providing general information, not medical advice,
    and encourage consulting healthcare providers for personalized guidance.
    Be respectful, inclusive, and sensitive when discussing health topics.
    """
    
    # Combine conversation history with current prompt
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can change to other models as needed
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Set API key from environment or secrets if available
try:
    # Try to get from Streamlit secrets (preferred for deployment)
    openai.api_key = st.secrets["openai"]["api_key"]
    st.session_state.openai_api_key = openai.api_key
except:
    # If not in secrets, try environment variable
    if os.getenv("OPENAI_API_KEY"):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        st.session_state.openai_api_key = openai.api_key

# API key input in sidebar (as backup or for user's own key)
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your OpenAI API key (optional if configured in deployment)", type="password")
    if api_key:
        st.session_state.openai_api_key = api_key
        openai.api_key = api_key
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This Women's Health Assistant provides information on various women's health topics.
    
    **Note:** This app is for informational purposes only and doesn't replace professional medical advice.
    """)

# Display chat history
for message in st.session_state.messages:
    with st.container():
        st.markdown(f"""
        <div class="chat-message {message['role']}">
            <div class="avatar">
                {message['role'][0].upper()}
            </div>
            <div class="message-content">
                {message['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# User input area
user_input = st.text_input("Type your question here...", key="user_input")

# Check if the user has provided an API key
if not st.session_state.openai_api_key and user_input:
    st.warning("Please enter your OpenAI API key in the sidebar to continue.")

# Process user input
if user_input and st.session_state.openai_api_key:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display "Assistant is typing..." message
    with st.spinner("Assistant is thinking..."):
        # Generate response
        response = generate_response(user_input, st.session_state.messages[:-1])
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun the app to update the display with the new messages
    st.rerun()

# Display disclaimer at the bottom
st.markdown("""
<div class="disclaimer">
    Disclaimer: This chatbot provides general information about women's health topics and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.
</div>
""", unsafe_allow_html=True)
