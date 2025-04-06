# Women's Health Navigator Chatbot
import streamlit as st
import openai
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (for local development)
load_dotenv()

# Set page configuration for better mobile experience
st.set_page_config(
    page_title="Women's Health Navigator",
    page_icon="💜",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better appearance 
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
    }
    .stChatMessage {
        padding: 0.5rem;
    }
    .stChatMessageContent {
        border-radius: 20px !important;
    }
    .stButton > button {
        border-radius: 20px;
        padding: 0.3rem;
    }
    .clinic-link {
        color: #0078ff;
        text-decoration: underline;
        cursor: pointer;
    }
    .header-section {
        display: flex;
        align-items: center;
        padding: 0.7rem 1rem;
        background-color: #075E54;
        color: white;
        border-radius: 10px 10px 0 0;
        margin-bottom: 1rem;
    }
    .header-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #128C7E;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.2rem;
    }
    .header-title {
        font-weight: bold;
    }
    .header-subtitle {
        font-size: 0.8rem;
        opacity: 0.8;
    }
    .disclaimer {
        font-size: 0.7rem;
        color: #888;
        font-style: italic;
        text-align: center;
        margin-top: 1rem;
    }
    div[data-testid="stHorizontalBlock"] {
        gap: 5px;
    }
    div[data-testid="stHorizontalBlock"] button {
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""
if 'conv_stage' not in st.session_state:
    st.session_state.conv_stage = "intro"
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        "name": "",
        "age": 0,
        "location": "Pune",
        "annual_checkup": None,
        "cervical_screening": None,
        "breast_screening": None,
        "current_location": "Pune"
    }
if 'quick_replies' not in st.session_state:
    st.session_state.quick_replies = []
if 'show_clinic_info' not in st.session_state:
    st.session_state.show_clinic_info = False
if 'alternate_location' not in st.session_state:
    st.session_state.alternate_location = ""
if 'waiting_for_input' not in st.session_state:
    st.session_state.waiting_for_input = True
if 'clinic_recommendations' not in st.session_state:
    st.session_state.clinic_recommendations = {
        "Pune": [
            {
                "name": "St. Mary's Health Center",
                "address": "200 Example Road, Pune",
                "services": ["cervical_cancer_screening", "breast_cancer_screening", "annual_checkup"],
                "phone": "123-456-7880",
                "cost": {"cervical_cancer_screening": 0, "breast_cancer_screening": 0, "annual_checkup": 0, "treatment": 15},
                "notes": "Free screenings available. Open Saturdays for working women."
            },
            {
                "name": "Women's Wellness Clinic",
                "address": "45 Health Avenue, Pune",
                "services": ["cervical_cancer_screening", "breast_cancer_screening", "annual_checkup"],
                "phone": "123-555-9090",
                "cost": {"cervical_cancer_screening": 0, "breast_cancer_screening": 0, "annual_checkup": 0, "treatment": 18},
                "notes": "Specializes in women's health. Female doctors available."
            }
        ],
        "Pipili": [
            {
                "name": "Pipili Community Hospital",
                "address": "78 Main Street, Pipili",
                "services": ["cervical_cancer_screening", "breast_cancer_screening", "annual_checkup"],
                "phone": "987-654-3210",
                "cost": {"cervical_cancer_screening": 5, "breast_cancer_screening": 5, "annual_checkup": 10, "treatment": 20},
                "notes": "Limited appointment availability. Call ahead."
            }
        ]
    }

# Configure API key from secrets or environment
try:
    # Try different secret formats
    if "OPENAI_API_KEY" in st.secrets:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        st.session_state.openai_api_key = openai.api_key
    elif "openai" in st.secrets and "api_key" in st.secrets["openai"]:
        openai.api_key = st.secrets["openai"]["api_key"]
        st.session_state.openai_api_key = openai.api_key
    elif os.getenv("OPENAI_API_KEY"):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        st.session_state.openai_api_key = openai.api_key
except Exception as e:
    pass  # Silently fail, will handle API key input if needed

# API key input in sidebar
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your OpenAI API key (if not configured)", type="password")
    if api_key:
        st.session_state.openai_api_key = api_key
        openai.api_key = api_key
    
    # User name input (for demo)
    if not st.session_state.user_profile["name"]:
        user_name = st.text_input("Enter your name (for demo)")
        if user_name:
            st.session_state.user_profile["name"] = user_name
            # Reset conversation to use the name
            if len(st.session_state.messages) <= 1:  # Only if conversation just started
                st.session_state.messages = []
                st.session_state.conv_stage = "intro"
                st.rerun()
    
    # Demo mode selector
    demo_scenario = st.selectbox(
        "Demo Scenario",
        ["Basic Screening Recommendation", "Test Results Follow-up", "Location Change"],
        index=0,
        key="demo_scenario_select"
    )
    
    st.write("Debug Info:")
    st.write(f"Conversation stage: {st.session_state.conv_stage}")
    st.write(f"Age: {st.session_state.user_profile['age']}")
    
    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.conv_stage = "intro"
        st.session_state.user_profile = {
            "name": st.session_state.user_profile["name"],  # Keep the name
            "age": 0,
            "location": "Pune",
            "annual_checkup": None,
            "cervical_screening": None,
            "breast_screening": None,
            "current_location": "Pune"
        }
        st.session_state.quick_replies = []
        st.session_state.show_clinic_info = False
        st.session_state.alternate_location = ""
        st.session_state.waiting_for_input = True
        st.rerun()

# Function to update conversation stage and send the next message
def update_conversation():
    current_stage = st.session_state.conv_stage
    
    # If no name is set, use a default
    name = st.session_state.user_profile["name"]
    if not name:
        name = "there"
    
    # Initial greeting
    if current_stage == "intro":
        message = f"Hi {name}, this is your health assistant. Sameera, your community health worker, recommended I reach out to you. I want to help you understand the recommended preventative healthcare you should have completed. Are you interested? It does not cost anything and I can help you find the right place and resources."
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.conv_stage = "ask_interest"
        st.session_state.quick_replies = ["Yes", "No"]
        return
    
    # Ask for age after confirming interest
    elif current_stage == "ask_age":
        message = "Great, let's start with a few questions. First, how old are you?"
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.conv_stage = "waiting_age"
        st.session_state.quick_replies = ["30", "40", "50", "60+"]
        return
    
    # Ask about annual checkup
    elif current_stage == "ask_annual_checkup":
        message = "Ok great. Have you had a doctor or nurse give you an exam in the last year for something unrelated to feeling sick?"
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.conv_stage = "waiting_annual_checkup"
        st.session_state.quick_replies = ["Yes", "No"]
        return
    
    # Ask about cervical cancer screening
    elif current_stage == "ask_cervical_screening":
        message = "Have you had a cervical cancer screening test in the past 5 years?"
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.conv_stage = "waiting_cervical_screening"
        st.session_state.quick_replies = ["Yes", "No", "I don't know"]
        return
    
    # Ask about breast cancer screening
    elif current_stage == "ask_breast_screening":
        message = "Have you had a breast cancer screening test in the past 5 years?"
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.conv_stage = "waiting_breast_screening"
        st.session_state.quick_replies = ["Yes", "No", "I don't know"]
        return
    
    # Provide recommendation
    elif current_stage == "provide_recommendation":
        # Determine recommendations based on responses
        recommendations = []
        
        if st.session_state.user_profile["annual_checkup"] == "No":
            recommendations.append("an annual wellness exam")
        
        if st.session_state.user_profile["cervical_screening"] == "No" and int(st.session_state.user_profile["age"]) >= 30:
            recommendations.append("an HPV test for cervical cancer screening")
        
        if st.session_state.user_profile["breast_screening"] == "No" and int(st.session_state.user_profile["age"]) >= 40:
            recommendations.append("a breast cancer screening")
        
        location = st.session_state.user_profile["current_location"]
        clinics = st.session_state.clinic_recommendations.get(location, [])
        clinic = clinics[0] if clinics else None
        
        if not recommendations:
            message = f"{name}, based on your answers, you're up-to-date on your recommended screenings. Great job taking care of your health! Remember to continue your regular check-ups. Is there anything specific about women's health you'd like to know more about?"
            st.session_state.quick_replies = ["Cervical cancer", "Breast cancer", "General wellness", "No, thanks"]
        elif clinic:
            services_needed = ", ".join(recommendations)
            
            # Create clinic address with underlined blue text
            clinic_info = f"<span class='clinic-link'>{clinic['name']}, {clinic['address']}, Phone: {clinic['phone']}</span>"
            
            message = f"{name}, based on your answers, I recommend you schedule {services_needed} at the closest clinic, {clinic_info}. "
            
            if "annual wellness exam" in services_needed:
                message += "Making an appointment is easy, call the number and say you want a check-up. "
            
            if "HPV test for cervical cancer screening" in services_needed:
                message += "For the cervical cancer screening, call the number and say you want an HPV test. "
                if clinic['cost']['cervical_cancer_screening'] == 0:
                    message += "This screening is available for free. "
                else:
                    message += f"This screening costs ₹{clinic['cost']['cervical_cancer_screening']}. "
            
            message += "Do you want to learn more about why these screenings are important and what to expect?"
            
            st.session_state.quick_replies = ["Yes, tell me more", "No thanks", "I have questions"]
        else:
            message = f"{name}, based on your answers, you should schedule {', '.join(recommendations)}. However, I don't have clinic information for your area. Please contact your local community health worker for assistance."
            st.session_state.quick_replies = ["OK, I will", "I need help finding a clinic"]
        
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.conv_stage = "post_recommendation"
        st.session_state.show_clinic_info = True
        return
    
    # Follow-up test results demo
    elif current_stage == "test_results_followup":
        message = f"{name}, St. Mary's clinic notified me that your cervical cancer results came back and require follow-up, that may include treatment. The doctor requested you come back for another appointment. Do you need help scheduling? What questions do you have?"
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.conv_stage = "waiting_results_response"
        st.session_state.quick_replies = ["I need help scheduling", "What does this mean?", "How much will it cost?"]
        return
    
    # Handle results questions
    elif current_stage == "answer_results_questions":
        clinic1 = st.session_state.clinic_recommendations["Pune"][0]
        clinic2 = st.session_state.clinic_recommendations["Pune"][1]
        
        message = f"First, you need to go back to clinic to discuss your results. Your doctor may give you some simple antibiotic pills if it's an infection, or do some more tests or treatment for cervical cancer. You can go to <span class='clinic-link'>{clinic1['name']}</span>, and the price is ₹{clinic1['cost']['treatment']}, or you can go to <span class='clinic-link'>{clinic2['name']}</span>, and the price is ₹{clinic2['cost']['treatment']} if you do need treatment. Do you want to learn more about what to expect from your results meeting and what treatment could mean?"
        
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.conv_stage = "waiting_treatment_questions"
        st.session_state.quick_replies = ["Yes, tell me more", "I'm not in Pune anymore", "I can't afford this"]
        return
    
    # Handle location change
    elif current_stage == "handle_location_change":
        alternate_clinic = st.session_state.clinic_recommendations["Pipili"][0]
        
        message = f"Got it. In that case, I suggest you go to <span class='clinic-link'>{alternate_clinic['name']}</span>, their price is ₹{alternate_clinic['cost']['treatment']}. Note there are fewer clinics in this area so it's more expensive, and the time to get an appointment can be longer."
        
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.conv_stage = "post_location_change"
        st.session_state.quick_replies = ["Thanks, I'll call them", "Can I get financial assistance?", "How urgent is this?"]
        return

# Process user response
def process_user_response(response):
    current_stage = st.session_state.conv_stage
    
    # Process interest response
    if current_stage == "ask_interest":
        if response.lower() == "yes":
            st.session_state.conv_stage = "ask_age"
        else:
            st.session_state.conv_stage = "end"
            return "I understand. If you change your mind, your community health worker Sameera can help you reconnect with me. Stay healthy!"
    
    # Process age response
    elif current_stage == "waiting_age":
        try:
            # First check if it's one of our quick reply options
            if response in ["30", "40", "50", "60+"]:
                age = int(response.replace("+", ""))
                st.session_state.user_profile["age"] = age
                st.session_state.conv_stage = "ask_annual_checkup"
                return None
            
            # Otherwise try to extract numbers from the response
            digits = ''.join(filter(str.isdigit, response))
            if digits:
                age = int(digits)
                if 18 <= age <= 120:  # Reasonable age range
                    st.session_state.user_profile["age"] = age
                    st.session_state.conv_stage = "ask_annual_checkup"
                    return None
            
            # If we got here, we couldn't parse the age
            return "I didn't understand that age. Please enter your age as a number between 18-120, or use one of the buttons below."
        except Exception as e:
            st.sidebar.error(f"Error processing age: {str(e)}")
            return "There was a problem with your age input. Please try entering just the number, like '45'."
    
    # Process annual checkup response
    elif current_stage == "waiting_annual_checkup":
        if response.lower() in ["yes", "no"]:
            st.session_state.user_profile["annual_checkup"] = response
            st.session_state.conv_stage = "ask_cervical_screening"
        else:
            return "Please answer with Yes or No. Have you had a doctor or nurse give you an exam in the last year for something unrelated to feeling sick?"
    
    # Process cervical screening response
    elif current_stage == "waiting_cervical_screening":
        if response.lower() in ["yes", "no", "i don't know"]:
            st.session_state.user_profile["cervical_screening"] = response
            st.session_state.conv_stage = "ask_breast_screening"
        else:
            return "Please answer with Yes, No, or I don't know. Have you had a cervical cancer screening test in the past 5 years?"
    
    # Process breast screening response
    elif current_stage == "waiting_breast_screening":
        if response.lower() in ["yes", "no", "i don't know"]:
            st.session_state.user_profile["breast_screening"] = response
            st.session_state.conv_stage = "provide_recommendation"
        else:
            return "Please answer with Yes, No, or I don't know. Have you had a breast cancer screening test in the past 5 years?"
    
    # Process results response
    elif current_stage == "waiting_results_response":
        st.session_state.conv_stage = "answer_results_questions"
    
    # Process treatment questions
    elif current_stage == "waiting_treatment_questions":
        if "not in pune" in response.lower() or "i'm not in pune" in response.lower() or "location" in response.lower():
            st.session_state.conv_stage = "handle_location_change"
            st.session_state.user_profile["current_location"] = "Pipili"
        else:
            # Generic response for other questions
            return "I understand your concerns. The most important step is to go back to the clinic to understand your specific situation. The doctor will explain all options and costs based on your results. Would you like me to help schedule an appointment?"
    
    # No specific handling needed for other stages
    return None

# Function to handle quick reply buttons
def handle_quick_reply(reply):
    st.session_state.messages.append({"role": "user", "content": reply})
    
    # Process response
    response_message = process_user_response(reply)
    if response_message:
        st.session_state.messages.append({"role": "assistant", "content": response_message})
    else:
        update_conversation()
    
    # Clear quick replies
    st.session_state.quick_replies = []
    st.rerun()

# App header
st.markdown("""
<div class="header-section">
    <div class="header-avatar">💜</div>
    <div>
        <div class="header-title">Women's Health Navigator</div>
        <div class="header-subtitle">Your personal health guide</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle demo scenario selection
demo_scenario = st.session_state.get("demo_scenario_select", "Basic Screening Recommendation")
if len(st.session_state.messages) == 0:
    if demo_scenario == "Test Results Follow-up":
        # Set up profile for test results scenario
        st.session_state.user_profile = {
            "name": st.session_state.user_profile["name"] or "Priya",
            "age": 45,
            "location": "Pune",
            "annual_checkup": "Yes",
            "cervical_screening": "Yes",
            "breast_screening": "Yes",
            "current_location": "Pune"
        }
        st.session_state.conv_stage = "test_results_followup"
    elif demo_scenario == "Location Change":
        # Set up profile for location change scenario
        st.session_state.user_profile = {
            "name": st.session_state.user_profile["name"] or "Priya",
            "age": 45,
            "location": "Pune",
            "annual_checkup": "Yes",
            "cervical_screening": "Yes",
            "breast_screening": "Yes",
            "current_location": "Pune"
        }
        st.session_state.conv_stage = "test_results_followup"

# Start or continue conversation
if len(st.session_state.messages) == 0:
    update_conversation()

# Display chat messages using Streamlit's built-in components
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar="💜"):
            st.markdown(message["content"], unsafe_allow_html=True)
    else:
        with st.chat_message("user", avatar="👤"):
            st.write(message["content"])

# Display quick reply buttons if available
if st.session_state.quick_replies and len(st.session_state.quick_replies) > 0:
    # Create columns based on the number of quick replies
    cols = st.columns(min(len(st.session_state.quick_replies), 3))
    
    # Add buttons to each column
    for i, reply in enumerate(st.session_state.quick_replies):
        col_idx = i % len(cols)
        if cols[col_idx].button(reply, key=f"qr_{reply}_{i}"):
            handle_quick_reply(reply)

# Chat input using Streamlit's chat_input
if prompt := st.chat_input("Type a message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Process response
    response_message = process_user_response(prompt)
    if response_message:
        st.session_state.messages.append({"role": "assistant", "content": response_message})
    else:
        update_conversation()
    
    # Clear quick replies and rerun
    st.session_state.quick_replies = []
    st.rerun()

# Display disclaimer
st.markdown("""
<div class="disclaimer">
    This Women's Health Navigator chatbot is a prototype demonstration developed by the consortium of FOGSI, JHPIEGO, and DL Analytics, LLC.
    It is for informational purposes only and does not provide medical advice.
</div>
""", unsafe_allow_html=True)

# Check if OpenAI API key is missing
if not st.session_state.openai_api_key:
    # Only show a minimal warning in the sidebar to not disrupt the demo flow
    st.sidebar.warning("⚠️ OpenAI API key not set (needed for advanced features)")
