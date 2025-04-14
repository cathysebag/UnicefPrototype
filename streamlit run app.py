# Women's Health Navigator Chatbot - Enhanced Version
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
    .emphasis {
        font-weight: bold;
        color: #075E54;
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
        "marital_status": "",
        "education_level": "",
        "annual_checkup": None,
        "cervical_screening": None,
        "breast_screening": None,
        "current_location": "Pune",
        "menstrual_regularity": None,
        "pregnancies": 0,
        "contraceptive_method": None,
        "presenting_complaints": [],
        "family_history_cancer": None,
        "chronic_conditions": [],
        "tobacco_use": None,
        "alcohol_use": None,
        "physical_activity": None
    }
if 'quick_replies' not in st.session_state:
    st.session_state.quick_replies = []
if 'show_clinic_info' not in st.session_state:
    st.session_state.show_clinic_info = False
if 'alternate_location' not in st.session_state:
    st.session_state.alternate_location = ""
if 'waiting_for_input' not in st.session_state:
    st.session_state.waiting_for_input = True
if 'assessment_path' not in st.session_state:
    st.session_state.assessment_path = []
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'test_results' not in st.session_state:
    st.session_state.test_results = {
        "cervical": None,  # Options: "normal", "abnormal_minor", "abnormal_serious"
        "breast": None     # Options: "normal", "abnormal"
    }
if 'visit_complete' not in st.session_state:
    st.session_state.visit_complete = False
if 'follow_up_scheduled' not in st.session_state:
    st.session_state.follow_up_scheduled = False
if 'next_appointment_date' not in st.session_state:
    st.session_state.next_appointment_date = None

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
        [
            "Basic Screening Recommendation", 
            "Test Results Follow-up", 
            "Location Change", 
            "Comprehensive Assessment",
            "Post-Visit Annual Wellness",
            "Post-Visit Cervical Screening",
            "Post-Visit Comprehensive Screening"
        ],
        index=0,
        key="demo_scenario_select"
    )
    
    # For post-visit demos, allow selection of test results
    if "Post-Visit" in demo_scenario and "Cervical" in demo_scenario:
        cervical_result = st.selectbox(
            "Cervical Screening Result",
            ["Normal", "Abnormal (minor)", "Abnormal (serious)"],
            index=0,
            key="cervical_result_select"
        )
        if cervical_result == "Normal":
            st.session_state.test_results["cervical"] = "normal"
        elif cervical_result == "Abnormal (minor)":
            st.session_state.test_results["cervical"] = "abnormal_minor"
        else:
            st.session_state.test_results["cervical"] = "abnormal_serious"
    
    if "Post-Visit" in demo_scenario and "Comprehensive" in demo_scenario:
        breast_result = st.selectbox(
            "Breast Screening Result",
            ["Normal", "Abnormal"],
            index=0,
            key="breast_result_select"
        )
        st.session_state.test_results["breast"] = breast_result.lower()
    
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
            "marital_status": "",
            "education_level": "",
            "annual_checkup": None,
            "cervical_screening": None,
            "breast_screening": None,
            "current_location": "Pune",
            "menstrual_regularity": None,
            "pregnancies": 0,
            "contraceptive_method": None,
            "presenting_complaints": [],
            "family_history_cancer": None,
            "chronic_conditions": [],
            "tobacco_use": None,
            "alcohol_use": None,
            "physical_activity": None
        }
        st.session_state.quick_replies = []
        st.session_state.show_clinic_info = False
        st.session_state.alternate_location = ""
        st.session_state.waiting_for_input = True
        st.session_state.assessment_path = []
        st.session_state.recommendations = []
        st.rerun()

# Helper functions for result messages
def get_cervical_result_message(name, result, include_greeting=True):
    """Generate message for cervical screening results"""
    greeting = f"Hello {name}, I'm contacting you about your cervical cancer screening results. " if include_greeting else ""
    
    if result == "normal":
        return f"{greeting}Your results are normal, which is great news! No abnormal cells were found. You should have your next screening in 3-5 years, depending on your age and risk factors."
    elif result == "abnormal_minor":
        return f"{greeting}Your results show some minor abnormal cells (sometimes called ASCUS or CIN-1). This is quite common and often clears up on its own, but we recommend a follow-up appointment for monitoring in 6 months."
    elif result == "abnormal_serious":
        return f"{greeting}Your results show some abnormal cells that require further evaluation (classified as CIN-2 or CIN-3). This is not cancer, but needs prompt follow-up. We need to schedule you for a colposcopy procedure for further examination."
    return ""

def get_breast_result_message(name, result, include_greeting=True):
    """Generate message for breast screening results"""
    greeting = f"Hello {name}, I'm contacting you about your breast cancer screening results. " if include_greeting else ""
    
    if result == "normal":
        return f"{greeting}Your mammogram results are normal. No suspicious areas were found. Based on your age and risk factors, your next mammogram should be in 1-2 years."
    elif result == "abnormal":
        return f"{greeting}Your mammogram shows an area that requires additional imaging. This is quite common and usually turns out to be normal tissue, but we need you to come back for some additional specialized mammogram images or possibly an ultrasound."
    return ""

def get_cervical_result_replies(result):
    """Generate quick reply options based on cervical results"""
    if result == "normal":
        return ["When is my next screening?", "Can I do anything to prevent cervical cancer?", "I understand, thank you"]
    elif result == "abnormal_minor":
        return ["Schedule follow-up", "What does this mean?", "What should I do differently?"]
    elif result == "abnormal_serious":
        return ["Schedule colposcopy", "Is this cancer?", "How urgent is this?"]
    return []

def get_breast_result_replies(result):
    """Generate quick reply options based on breast results"""
    if result == "normal":
        return ["When is my next screening?", "Can I do anything to prevent breast cancer?", "I understand, thank you"]
    elif result == "abnormal":
        return ["Schedule follow-up imaging", "What does this mean?", "How urgent is this?"]
    return []

def get_comprehensive_result_replies(cervical_result, breast_result):
    """Generate quick reply options for comprehensive screening results"""
    replies = []
    
    # Add most important action items first
    if cervical_result == "abnormal_serious":
        replies.append("Schedule colposcopy")
    elif breast_result == "abnormal":
        replies.append("Schedule follow-up imaging")
    elif cervical_result == "abnormal_minor":
        replies.append("Schedule cervical follow-up")
        
    # Add understanding questions if there are abnormal results
    if cervical_result != "normal" or breast_result != "normal":
        replies.append("What do these results mean?")
        replies.append("How urgent is this?")
    else:
        replies.append("When are my next screenings?")
        replies.append("How can I stay healthy?")
        
    # Always include a confirmation option
    replies.append("I understand, thank you")
    
    return replies

# Assessment flow configuration
ASSESSMENT_FLOW = {
    "intro": {
        "message": lambda name: f"Hi {name}, this is your health assistant. Sameera, your community health worker, recommended I reach out to you. I want to help you understand the recommended preventative healthcare you should have completed. Are you interested? It does not cost anything and I can help you find the right place and resources.",
        "next_stage": "ask_interest",
        "quick_replies": ["Yes", "No"]
    },
    "ask_interest": {
        "yes": "ask_age",
        "no": "end",
        "no_message": "I understand. If you change your mind, your community health worker Sameera can help you reconnect with me. Stay healthy!"
    },
    "ask_age": {
        "message": "Great, let's start with a few questions to understand your health needs better. First, how old are you?",
        "next_stage": "waiting_age",
        "quick_replies": ["25-30", "31-40", "41-50", "51+"]
    },
    "ask_marital_status": {
        "message": "Thank you. What is your marital status? You can also type 'Skip' if you prefer not to answer.",
        "next_stage": "waiting_marital_status",
        "quick_replies": ["Single", "Married", "Widowed", "Divorced", "Skip"]
    },
    "ask_education": {
        "message": "What is your highest level of education? You can also type 'Skip' if you prefer not to answer.",
        "next_stage": "waiting_education",
        "quick_replies": ["No formal education", "Primary", "Secondary", "Higher", "Skip"]
    },
    "ask_menstrual_regularity": {
        "message": "Now let's talk about your health. Is your menstrual cycle regular? Feel free to tell me in your own words.",
        "next_stage": "waiting_menstrual_regularity",
        "quick_replies": ["Regular", "Irregular", "Menopause", "Not applicable", "Skip"]
    },
    "ask_pregnancies": {
        "message": "How many pregnancies have you had? Just type the number or select from the options.",
        "next_stage": "waiting_pregnancies",
        "quick_replies": ["0", "1", "2", "3+", "Skip"]
    },
    "ask_contraceptive": {
        "message": "Are you currently using any contraceptive method? You can tell me in your own words.",
        "next_stage": "waiting_contraceptive",
        "quick_replies": ["None", "Oral Pills", "IUD", "Condoms", "Sterilization", "Other", "Skip"]
    },
    "ask_complaints": {
        "message": "Do you currently have any health concerns? Feel free to describe them in your own words, or select from common issues below.",
        "next_stage": "waiting_complaints",
        "quick_replies": ["None", "Pelvic pain", "Vaginal discharge", "Irregular bleeding", "Pain during intercourse", "Urinary issues", "Other"]
    },
    "ask_annual_checkup": {
        "message": "Have you had a doctor or nurse give you an exam in the last year for something unrelated to feeling sick?",
        "next_stage": "waiting_annual_checkup",
        "quick_replies": ["Yes", "No", "Not sure"]
    },
    "ask_cervical_screening": {
        "message": "Have you had a cervical cancer screening test (like a Pap smear or HPV test) in the past 5 years?",
        "next_stage": "waiting_cervical_screening",
        "quick_replies": ["Yes", "No", "I don't know"]
    },
    "ask_breast_screening": {
        "message": "Have you had a breast cancer screening test in the past 5 years?",
        "next_stage": "waiting_breast_screening",
        "quick_replies": ["Yes", "No", "I don't know"]
    },
    "ask_family_history": {
        "message": "Is there any history of reproductive cancers in your family, such as breast cancer, cervical cancer, or ovarian cancer?",
        "next_stage": "waiting_family_history",
        "quick_replies": ["Yes", "No", "I don't know", "Skip"]
    },
    "ask_chronic_conditions": {
        "message": "Do you have any ongoing health conditions? Feel free to mention them in your own words, or select from common ones below.",
        "next_stage": "waiting_chronic_conditions",
        "quick_replies": ["None", "Hypertension", "Diabetes", "Anemia", "Thyroid disorder", "STI/RTI", "Other"]
    },
    "ask_lifestyle": {
        "message": "Let's talk about lifestyle. Do you use tobacco products?",
        "next_stage": "waiting_tobacco",
        "quick_replies": ["Yes", "No", "Skip"]
    },
    "ask_alcohol": {
        "message": "Do you consume alcohol?",
        "next_stage": "waiting_alcohol",
        "quick_replies": ["Yes", "No", "Skip"]
    },
    "ask_physical_activity": {
        "message": "How would you describe your level of physical activity? You can tell me in your own words.",
        "next_stage": "waiting_physical_activity",
        "quick_replies": ["Very active", "Moderately active", "Lightly active", "Sedentary", "Skip"]
    },
    "provide_recommendation": {
        "message": lambda name, recommendations: f"{name}, based on your answers, I recommend you schedule {recommendations}. Would you like information on clinics near you?",
        "next_stage": "waiting_clinic_info",
        "quick_replies": ["Yes, show me clinics", "Not now"]
    },
    
    # Post-visit flows for different screening scenarios
    "post_visit_annual": {
        "message": lambda name: f"Hello {name}, I wanted to check in with you after your annual wellness visit at the clinic yesterday. How are you feeling? Is there anything from your visit that you have questions about?",
        "next_stage": "waiting_annual_feedback",
        "quick_replies": ["I have a question", "Everything is clear", "When should I come back?"]
    },
    "post_visit_cervical": {
        "message": lambda name: f"Hello {name}, I wanted to check in with you after your cervical cancer screening yesterday. Your results will be ready in about 3-4 weeks. Do you have any questions about the procedure or what happens next?",
        "next_stage": "waiting_cervical_feedback",
        "quick_replies": ["How will I get results?", "What could the results show?", "Everything is clear"]
    },
    "post_visit_comprehensive": {
        "message": lambda name: f"Hello {name}, I wanted to check in with you after your comprehensive screening yesterday that included both cervical and breast cancer screening. Your results will be ready in about 3-4 weeks. How are you feeling, and do you have any questions?",
        "next_stage": "waiting_comprehensive_feedback",
        "quick_replies": ["How will I get results?", "What could the results show?", "Everything is clear"]
    },
    
    # Result notification stages for cervical screening
    "cervical_results_notification": {
        "message": lambda name, result: get_cervical_result_message(name, result),
        "next_stage": "waiting_cervical_results_response",
        "quick_replies": lambda result: get_cervical_result_replies(result)
    },
    
    # Result notification stages for breast screening
    "breast_results_notification": {
        "message": lambda name, result: get_breast_result_message(name, result),
        "next_stage": "waiting_breast_results_response",
        "quick_replies": lambda result: get_breast_result_replies(result)
    },
    
    # Comprehensive results (both cervical and breast)
    "comprehensive_results_notification": {
        "message": lambda name, cervical_result, breast_result: f"Hello {name}, I'm reaching out regarding your recent screening results.\n\n{get_cervical_result_message(name, cervical_result, include_greeting=False)}\n\n{get_breast_result_message(name, breast_result, include_greeting=False)}",
        "next_stage": "waiting_comprehensive_results_response",
        "quick_replies": lambda cervical_result, breast_result: get_comprehensive_result_replies(cervical_result, breast_result)
    },
}

# Function to determine the assessment path based on age and risk factors
def determine_assessment_path(age, initial_response=None):
    """
    Determines which questions to ask based on age and initial responses
    """
    # Basic path for all women
    basic_path = ["ask_age", "ask_marital_status", "ask_education", "ask_annual_checkup"]
    
    # Add reproductive health questions for women of reproductive age (under 50)
    if age < 50:
        basic_path.extend(["ask_menstrual_regularity", "ask_pregnancies", "ask_contraceptive"])
    
    # Always ask about complaints
    basic_path.append("ask_complaints")
    
    # Add screening questions based on age
    if age >= 30:
        basic_path.append("ask_cervical_screening")
    
    if age >= 40:
        basic_path.append("ask_breast_screening")
    
    # Add family history and risk factors for all
    basic_path.extend(["ask_family_history", "ask_chronic_conditions"])
    
    # Add lifestyle questions
    basic_path.extend(["ask_lifestyle", "ask_alcohol", "ask_physical_activity"])
    
    # End with recommendation
    basic_path.append("provide_recommendation")
    
    return basic_path

# Function to determine health recommendations based on user profile
def determine_recommendations(user_profile):
    """
    Analyzes user profile to provide appropriate health recommendations
    """
    recommendations = []
    needs_annual = False
    needs_cervical = False
    needs_breast = False
    
    # Annual wellness check recommendation
    if user_profile["annual_checkup"] == "No" or user_profile["annual_checkup"] == "Not sure":
        needs_annual = True
        recommendations.append("an annual wellness exam")
    
    # Cervical cancer screening recommendation
    age = int(user_profile["age"]) if isinstance(user_profile["age"], int) else int(user_profile["age"].split("-")[0])
    if age >= 30 and (user_profile["cervical_screening"] == "No" or user_profile["cervical_screening"] == "I don't know"):
        needs_cervical = True
        if not needs_annual:
            recommendations.append("a cervical cancer screening (HPV test)")
    
    # Breast cancer screening recommendation
    if age >= 40 and (user_profile["breast_screening"] == "No" or user_profile["breast_screening"] == "I don't know"):
        needs_breast = True
        if not needs_annual:
            recommendations.append("a breast cancer screening (mammogram)")
    
    # Combine recommendations if needed
    if needs_annual and needs_cervical and needs_breast:
        recommendations = ["an annual wellness exam that includes both cervical and breast cancer screening"]
    elif needs_annual and needs_cervical:
        recommendations = ["an annual wellness exam that includes cervical cancer screening"]
    elif needs_annual and needs_breast:
        recommendations = ["an annual wellness exam that includes breast cancer screening"]
    
    # Add additional recommendations based on risk factors
    if user_profile.get("family_history_cancer") == "Yes":
        recommendations.append("a discussion about your family history of cancer with your healthcare provider")
    
    if "chronic_conditions" in user_profile and ("Hypertension" in user_profile["chronic_conditions"] or "Diabetes" in user_profile["chronic_conditions"]):
        recommendations.append("regular monitoring of your chronic condition(s)")
    
    if user_profile.get("tobacco_use") == "Yes" or user_profile.get("alcohol_use") == "Yes":
        recommendations.append("lifestyle counseling")
    
    if user_profile.get("physical_activity") == "Sedentary":
        recommendations.append("guidance on increasing physical activity")
    
    # Save recommendations for later use
    st.session_state.recommendations = recommendations
    
    return recommendations

# Function to format recommendations as text
def format_recommendations(recommendations):
    if not recommendations:
        return "continuing with your current health routine"
    
    if len(recommendations) == 1:
        return recommendations[0]
    elif len(recommendations) == 2:
        return f"{recommendations[0]} and {recommendations[1]}"
    else:
        return f"{', '.join(recommendations[:-1])}, and {recommendations[-1]}"

# Function to update conversation stage and send the next message
def update_conversation():
    current_stage = st.session_state.conv_stage
    
    # If no name is set, use a default
    name = st.session_state.user_profile["name"]
    if not name:
        name = "there"
    
    # Check if we're in the assessment flow
    if current_stage in ASSESSMENT_FLOW:
        stage_info = ASSESSMENT_FLOW[current_stage]
        
        if "message" in stage_info:
            # Handle dynamic messages with lambdas
            if callable(stage_info["message"]):
                if current_stage == "provide_recommendation":
                    recommendations = determine_recommendations(st.session_state.user_profile)
                    formatted_recs = format_recommendations(recommendations)
                    message = stage_info["message"](name, formatted_recs)
                elif current_stage == "cervical_results_notification":
                    cervical_result = st.session_state.test_results.get("cervical", "normal")
                    message = stage_info["message"](name, cervical_result)
                elif current_stage == "breast_results_notification":
                    breast_result = st.session_state.test_results.get("breast", "normal")
                    message = stage_info["message"](name, breast_result)
                elif current_stage == "comprehensive_results_notification":
                    cervical_result = st.session_state.test_results.get("cervical", "normal")
                    breast_result = st.session_state.test_results.get("breast", "normal")
                    message = stage_info["message"](name, cervical_result, breast_result)
                else:
                    message = stage_info["message"](name)
            else:
                message = stage_info["message"]
                
            st.session_state.messages.append({"role": "assistant", "content": message})
            
            if "next_stage" in stage_info:
                st.session_state.conv_stage = stage_info["next_stage"]
            
            if "quick_replies" in stage_info:
                if callable(stage_info["quick_replies"]):
                    if current_stage == "cervical_results_notification":
                        cervical_result = st.session_state.test_results.get("cervical", "normal")
                        st.session_state.quick_replies = stage_info["quick_replies"](cervical_result)
                    elif current_stage == "breast_results_notification":
                        breast_result = st.session_state.test_results.get("breast", "normal")
                        st.session_state.quick_replies = stage_info["quick_replies"](breast_result)
                    elif current_stage == "comprehensive_results_notification":
                        cervical_result = st.session_state.test_results.get("cervical", "normal")
                        breast_result = st.session_state.test_results.get("breast", "normal")
                        st.session_state.quick_replies = stage_info["quick_replies"](cervical_result, breast_result)
                else:
                    st.session_state.quick_replies = stage_info["quick_replies"]
            
            return
    
    # Handle showing clinic information
    elif current_stage == "waiting_clinic_info" and st.session_state.show_clinic_info:
        location = st.session_state.user_profile["current_location"]
        clinics = st.session_state.clinic_recommendations.get(location, [])
        
        if clinics:
            message = f"Here are the clinics in {location} that offer the services you need:\n\n"
            
            for i, clinic in enumerate(clinics, 1):
                services = []
                costs = []
                
                for rec in st.session_state.recommendations:
                    if "annual wellness" in rec:
                        services.append("annual wellness exam")
                        costs.append(f"₹{clinic['cost']['annual_checkup']}")
                    if "cervical" in rec:
                        services.append("cervical cancer screening")
                        costs.append(f"₹{clinic['cost']['cervical_cancer_screening']}")
                    if "breast" in rec:
                        services.append("breast cancer screening")
                        costs.append(f"₹{clinic['cost']['breast_cancer_screening']}")
                
                message += f"<span class='clinic-link'>{i}. {clinic['name']}</span>\n"
                message += f"   Address: {clinic['address']}\n"
                message += f"   Phone: {clinic['phone']}\n"
                
                if services:
                    message += f"   Services: {', '.join(services)}\n"
                if costs:
                    message += f"   Costs: {', '.join(costs)}\n"
                
                if clinic['notes']:
                    message += f"   Note: {clinic['notes']}\n"
                
                message += "\n"
            
            message += "Would you like me to explain more about why these screenings are important and what to expect?"
            
            st.session_state.messages.append({"role": "assistant", "content": message})
            st.session_state.conv_stage = "waiting_screening_info"
            st.session_state.quick_replies = ["Yes, tell me more", "No, thank you", "I have questions"]
            return
        else:
            message = f"{name}, I don't have clinic information for your area. Please contact your local community health worker for assistance."
            st.session_state.messages.append({"role": "assistant", "content": message})
            st.session_state.conv_stage = "end"
            return
    
    # Provide screening information
    elif current_stage == "waiting_screening_info" and st.session_state.messages[-1]["role"] == "user" and "yes" in st.session_state.messages[-1]["content"].lower():
        message = "Here's what to expect for each screening:\n\n"
        
        for rec in st.session_state.recommendations:
            if "annual wellness" in rec:
                message += "<span class='emphasis'>Annual Wellness Exam:</span> This is a check-up where the doctor will measure your blood pressure, weight, and ask about your overall health. They might do a basic physical examination. It typically takes 30-45 minutes.\n\n"
            
            if "cervical" in rec:
                message += "<span class='emphasis'>Cervical Cancer Screening:</span> This involves either a Pap smear or HPV test where the doctor collects a small sample of cells from your cervix. It only takes a few minutes and may cause mild discomfort but not pain. You'll lie on an exam table with your feet in stirrups, and the doctor will use a speculum to examine your cervix.\n\n"
            
            if "breast" in rec:
                message += "<span class='emphasis'>Breast Cancer Screening:</span> This usually means a mammogram, which is an X-ray of your breast tissue. You'll stand in front of the mammogram machine, and each breast will be compressed between two plates for a few seconds to take the image. Some women find it uncomfortable but it's quick.\n\n"
        
        message += "These screenings are important because they can detect health issues before you have symptoms, when they're easier to treat. Early detection saves lives, especially with cancers.\n\n"
        message += "Do you have any specific questions about these procedures?"
        
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.conv_stage = "answer_screening_questions"
        st.session_state.quick_replies = ["How long will it take?", "Will it hurt?", "What should I wear?", "No, I'm ready to schedule"]
        return
    
    # End of conversation
    elif current_stage == "end":
        message = f"Thank you for using the Women's Health Navigator, {name}. Remember that preventative health care is important. Your community health worker Sameera is always available if you need further assistance. Stay healthy!"
        st.session_state.messages.append({"role": "assistant", "content": message})
        st.session_state.quick_replies = ["Start over", "Goodbye"]
        return
    
    # Test results follow-up demo
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
            st.session_state.assessment_path = determine_assessment_path(0)  # Will update after getting age
        else:
            st.session_state.conv_stage = "end"
            return "I understand. If you change your mind, your community health worker Sameera can help you reconnect with me. Stay healthy!"
    
    # Process age response
    elif current_stage == "waiting_age":
        try:
            # First check if it's one of our quick reply options
            if response in ["25-30", "31-40", "41-50", "51+"]:
                # Parse age range and use the lower bound
                age = int(response.split("-")[0])
                st.session_state.user_profile["age"] = age
                # Determine assessment path based on age
                st.session_state.assessment_path = determine_assessment_path(age)
                st.session_state.conv_stage = "ask_marital_status"
                return None
            
            # Otherwise try to extract numbers from the response
            digits = ''.join(filter(str.isdigit, response))
            if digits:
                age = int(digits)
                if 18 <= age <= 120:  # Reasonable age range
                    st.session_state.user_profile["age"] = age
                    # Determine assessment path based on age
                    st.session_state.assessment_path = determine_assessment_path(age)
                    st.session_state.conv_stage = "ask_marital_status"
                    return None
            
            # If we got here, we couldn't parse the age but will still move on
            st.session_state.user_profile["age"] = 35  # Default to middle age
            st.session_state.assessment_path = determine_assessment_path(35)
            st.session_state.conv_stage = "ask_marital_status"
            return "I'm not sure I got your age correctly, but let's continue. I'll use an estimate for now. What is your marital status?"
        except Exception as e:
            st.sidebar.error(f"Error processing age: {str(e)}")
            st.session_state.user_profile["age"] = 35  # Default to middle age
            st.session_state.assessment_path = determine_assessment_path(35)
            st.session_state.conv_stage = "ask_marital_status"
            return "Let's move on to the next question. What is your marital status?"
    
    # Process marital status
    elif current_stage == "waiting_marital_status":
        # Direct matches for button clicks
        if response in ["Single", "Married", "Widowed", "Divorced", "Skip"]:
            if response == "Skip":
                st.session_state.user_profile["marital_status"] = "Not specified"
            else:
                st.session_state.user_profile["marital_status"] = response
            st.session_state.conv_stage = "ask_education"
            return None
            
        # Allow for flexible matching of marital status
        status_mapping = {
            "single": "Single",
            "never married": "Single",
            "unmarried": "Single",
            "married": "Married",
            "widow": "Widowed", 
            "widowed": "Widowed",
            "divorce": "Divorced",
            "divorced": "Divorced",
            "separated": "Divorced"
        }
        
        # Try to match their response to a known status
        matched = False
        for key, value in status_mapping.items():
            if key in response.lower():
                st.session_state.user_profile["marital_status"] = value
                matched = True
                break
        
        # If we couldn't match, or they want to skip, still move forward
        if not matched:
            if "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
                st.session_state.user_profile["marital_status"] = "Not specified"
            else:
                # Just use their response directly
                st.session_state.user_profile["marital_status"] = response
        
        # Always move forward
        st.session_state.conv_stage = "ask_education"
        return None
    
    # Process education level - more flexible
    elif current_stage == "waiting_education":
        # Direct matches for button clicks
        if response in ["No formal education", "Primary", "Secondary", "Higher", "Skip"]:
            if response == "Skip":
                st.session_state.user_profile["education_level"] = "Not specified"
            else:
                st.session_state.user_profile["education_level"] = response
            st.session_state.conv_stage = "ask_annual_checkup"
            return None
            
        education_mapping = {
            "no": "No formal education",
            "none": "No formal education",
            "primary": "Primary",
            "elementary": "Primary",
            "secondary": "Secondary",
            "high school": "Secondary",
            "higher": "Higher",
            "college": "Higher",
            "university": "Higher",
            "graduate": "Higher"
        }
        
        # Try to match their response to a known education level
        matched = False
        for key, value in education_mapping.items():
            if key in response.lower():
                st.session_state.user_profile["education_level"] = value
                matched = True
                break
        
        # If we couldn't match, still move forward
        if not matched:
            if "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
                st.session_state.user_profile["education_level"] = "Not specified"
            else:
                # Just use their response directly
                st.session_state.user_profile["education_level"] = response
        
        # Always move forward
        st.session_state.conv_stage = "ask_annual_checkup"
        return None
    
    # Process menstrual regularity
    elif current_stage == "waiting_menstrual_regularity":
        # Direct matches for button clicks
        if response in ["Regular", "Irregular", "Menopause", "Not applicable", "Skip"]:
            if response == "Skip":
                st.session_state.user_profile["menstrual_regularity"] = "Not specified"
            else:
                st.session_state.user_profile["menstrual_regularity"] = response
            st.session_state.conv_stage = "ask_pregnancies"
            return None
            
        regularity_mapping = {
            "regular": "Regular",
            "irregular": "Irregular",
            "not regular": "Irregular",
            "menopause": "Menopause",
            "stopped": "Menopause",
            "no period": "Menopause",
            "not applicable": "Not applicable",
            "n/a": "Not applicable",
            "na": "Not applicable"
        }
        
        # Try to match their response
        matched = False
        for key, value in regularity_mapping.items():
            if key in response.lower():
                st.session_state.user_profile["menstrual_regularity"] = value
                matched = True
                break
        
        # If we couldn't match, still move forward
        if not matched:
            if "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
                st.session_state.user_profile["menstrual_regularity"] = "Not specified"
            else:
                # Use their response or mark as irregular if unclear
                st.session_state.user_profile["menstrual_regularity"] = response
        
        # Always move forward
        st.session_state.conv_stage = "ask_pregnancies"
        return None
    
    # Process pregnancies
    elif current_stage == "waiting_pregnancies":
        # Direct matches for button clicks
        if response in ["0", "1", "2", "3+", "Skip"]:
            if response == "Skip":
                st.session_state.user_profile["pregnancies"] = "Not specified"
            else:
                st.session_state.user_profile["pregnancies"] = response
            st.session_state.conv_stage = "ask_contraceptive"
            return None
            
        # Try to extract a number
        digits = ''.join(filter(str.isdigit, response))
        if digits:
            st.session_state.user_profile["pregnancies"] = digits
        elif "none" in response.lower() or "zero" in response.lower() or "0" in response:
            st.session_state.user_profile["pregnancies"] = "0"
        elif "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
            st.session_state.user_profile["pregnancies"] = "Not specified"
        else:
            # Default to some value to continue
            st.session_state.user_profile["pregnancies"] = response
        
        # Always move forward
        st.session_state.conv_stage = "ask_contraceptive"
        return None
    
    # Process contraceptive method
    elif current_stage == "waiting_contraceptive":
        # Direct matches for button clicks
        if response in ["None", "Oral Pills", "IUD", "Condoms", "Sterilization", "Other", "Skip"]:
            if response == "Skip":
                st.session_state.user_profile["contraceptive_method"] = "Not specified"
            else:
                st.session_state.user_profile["contraceptive_method"] = response
            st.session_state.conv_stage = "ask_complaints"
            return None
            
        contraceptive_mapping = {
            "none": "None",
            "no": "None",
            "don't use": "None",
            "do not use": "None",
            "pill": "Oral Pills",
            "oral": "Oral Pills",
            "iud": "IUD",
            "intrauterine": "IUD",
            "condom": "Condoms",
            "barrier": "Condoms",
            "sterilization": "Sterilization",
            "tubes tied": "Sterilization",
            "tubal": "Sterilization",
            "other": "Other"
        }
        
        # Try to match their response
        matched = False
        for key, value in contraceptive_mapping.items():
            if key in response.lower():
                st.session_state.user_profile["contraceptive_method"] = value
                matched = True
                break
        
        # If we couldn't match, still move forward
        if not matched:
            if "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
                st.session_state.user_profile["contraceptive_method"] = "Not specified"
            else:
                # Just use their response
                st.session_state.user_profile["contraceptive_method"] = response
        
        # Always move forward
        st.session_state.conv_stage = "ask_complaints"
        return None
    
    # Process complaints (can be multiple)
    elif current_stage == "waiting_complaints":
        # Handle continue command
        if response.lower() == "continue":
            # If they click continue, move to next question
            if "ask_annual_checkup" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_annual_checkup"
            elif "ask_cervical_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_cervical_screening"
            else:
                st.session_state.conv_stage = "ask_family_history"
            return None
        
        # Direct match for None button
        if response == "None":
            st.session_state.user_profile["presenting_complaints"] = []
            if "ask_annual_checkup" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_annual_checkup"
            elif "ask_cervical_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_cervical_screening"
            else:
                st.session_state.conv_stage = "ask_family_history"
            return None
            
        # Direct matches for other buttons
        if response in ["Pelvic pain", "Vaginal discharge", "Irregular bleeding", "Pain during intercourse", "Urinary issues", "Other"]:
            if response not in st.session_state.user_profile["presenting_complaints"]:
                st.session_state.user_profile["presenting_complaints"].append(response)
                concerns = ", ".join(st.session_state.user_profile["presenting_complaints"])
                return f"I've noted your health concerns: {concerns}. Do you have any other concerns? Select another or say 'Continue' to proceed."
            else:
                return "You've already selected this concern. Do you have any others? Select another or say 'Continue' to proceed."
                
        complaint_mapping = {
            "none": "None",
            "no": "None",
            "nothing": "None",
            "pain": "Pelvic pain",
            "pelvic pain": "Pelvic pain",
            "cramps": "Pelvic pain",
            "discharge": "Vaginal discharge",
            "vaginal discharge": "Vaginal discharge",
            "bleed": "Irregular bleeding",
            "irregular bleeding": "Irregular bleeding",
            "spotting": "Irregular bleeding",
            "intercourse pain": "Pain during intercourse",
            "sex pain": "Pain during intercourse",
            "painful sex": "Pain during intercourse",
            "urinary": "Urinary issues",
            "urine": "Urinary issues",
            "bladder": "Urinary issues",
            "other": "Other"
        }
        
        # Check for "None" first
        if any(key in response.lower() for key in ["none", "no", "nothing", "healthy"]):
            # If None is selected, clear any existing complaints
            st.session_state.user_profile["presenting_complaints"] = []
            # Move to next question
            if "ask_annual_checkup" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_annual_checkup"
            elif "ask_cervical_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_cervical_screening"
            else:
                st.session_state.conv_stage = "ask_family_history"
            return None
            
        # Try to match their response to a known complaint
        matched = False
        for key, value in complaint_mapping.items():
            if key in response.lower() and value != "None":
                if value not in st.session_state.user_profile["presenting_complaints"]:
                    st.session_state.user_profile["presenting_complaints"].append(value)
                    matched = True
        
        if matched:
            concerns = ", ".join(st.session_state.user_profile["presenting_complaints"])
            return f"I've noted your health concerns: {concerns}. Do you have any other concerns? Select another or say 'Continue' to proceed."
        else:
            # If they mentioned something we don't recognize, just add it as "Other"
            if "Other" not in st.session_state.user_profile["presenting_complaints"] and response.lower() not in ["skip", "prefer not", "next"]:
                st.session_state.user_profile["presenting_complaints"].append("Other: " + response)
                
            # Provide option to continue
            concerns = ", ".join(st.session_state.user_profile["presenting_complaints"])
            if concerns:
                return f"I've noted your health concerns: {concerns}. Do you have any other concerns? Select another or say 'Continue' to proceed."
            else:
                # If we couldn't match anything and they have no concerns yet, just move forward
                if "ask_annual_checkup" in st.session_state.assessment_path:
                    st.session_state.conv_stage = "ask_annual_checkup"
                elif "ask_cervical_screening" in st.session_state.assessment_path:
                    st.session_state.conv_stage = "ask_cervical_screening"
                else:
                    st.session_state.conv_stage = "ask_family_history"
                return None
    
    # Process annual checkup response
    elif current_stage == "waiting_annual_checkup":
        # Direct matches for buttons
        if response in ["Yes", "No", "Not sure"]:
            st.session_state.user_profile["annual_checkup"] = response
            if "ask_cervical_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_cervical_screening"
            elif "ask_breast_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_breast_screening" 
            else:
                st.session_state.conv_stage = "ask_family_history"
            return None
            
        if response.lower() == "yes" or "had" in response.lower() or "done" in response.lower():
            st.session_state.user_profile["annual_checkup"] = "Yes"
        elif response.lower() == "no" or "haven't" in response.lower() or "have not" in response.lower():
            st.session_state.user_profile["annual_checkup"] = "No"
        elif "not sure" in response.lower() or "maybe" in response.lower() or "don't know" in response.lower():
            st.session_state.user_profile["annual_checkup"] = "Not sure"
        elif "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
            st.session_state.user_profile["annual_checkup"] = "Not specified"
        else:
            # Default to Not sure if we can't categorize
            st.session_state.user_profile["annual_checkup"] = "Not sure"
        
        # Always move to next question
        if "ask_cervical_screening" in st.session_state.assessment_path:
            st.session_state.conv_stage = "ask_cervical_screening"
        elif "ask_breast_screening" in st.session_state.assessment_path:
            st.session_state.conv_stage = "ask_breast_screening" 
        else:
            st.session_state.conv_stage = "ask_family_history"
        return None
    
    # Process cervical screening response
    elif current_stage == "waiting_cervical_screening":
        # Direct matches for buttons
        if response in ["Yes", "No", "I don't know"]:
            st.session_state.user_profile["cervical_screening"] = response
            if "ask_breast_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_breast_screening"
            else:
                st.session_state.conv_stage = "ask_family_history"
            return None
            
        if response.lower() == "yes" or "had" in response.lower() or "done" in response.lower():
            st.session_state.user_profile["cervical_screening"] = "Yes"
        elif response.lower() == "no" or "haven't" in response.lower() or "have not" in response.lower():
            st.session_state.user_profile["cervical_screening"] = "No"
        elif "don't know" in response.lower() or "not sure" in response.lower() or "maybe" in response.lower():
            st.session_state.user_profile["cervical_screening"] = "I don't know"
        elif "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
            st.session_state.user_profile["cervical_screening"] = "Not specified"
        else:
            # Default to I don't know if we can't categorize
            st.session_state.user_profile["cervical_screening"] = "I don't know"
        
        # Always move to next question
        if "ask_breast_screening" in st.session_state.assessment_path:
            st.session_state.conv_stage = "ask_breast_screening"
        else:
            st.session_state.conv_stage = "ask_family_history"
        return None
    
    # Process breast screening response
    elif current_stage == "waiting_breast_screening":
        # Direct matches for buttons
        if response in ["Yes", "No", "I don't know"]:
            st.session_state.user_profile["breast_screening"] = response
            st.session_state.conv_stage = "ask_family_history"
            return None
            
        if response.lower() == "yes" or "had" in response.lower() or "done" in response.lower():
            st.session_state.user_profile["breast_screening"] = "Yes"
        elif response.lower() == "no" or "haven't" in response.lower() or "have not" in response.lower():
            st.session_state.user_profile["breast_screening"] = "No"
        elif "don't know" in response.lower() or "not sure" in response.lower() or "maybe" in response.lower():
            st.session_state.user_profile["breast_screening"] = "I don't know"
        elif "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
            st.session_state.user_profile["breast_screening"] = "Not specified"
        else:
            # Default to I don't know if we can't categorize
            st.session_state.user_profile["breast_screening"] = "I don't know"
        
        # Always move to next question
        st.session_state.conv_stage = "ask_family_history"
        return None
    
    # Process family history
    elif current_stage == "waiting_family_history":
        # Direct matches for buttons
        if response in ["Yes", "No", "I don't know", "Skip"]:
            if response == "Skip":
                st.session_state.user_profile["family_history_cancer"] = "Not specified"
            else:
                st.session_state.user_profile["family_history_cancer"] = response
            st.session_state.conv_stage = "ask_chronic_conditions"
            return None
            
        if response.lower() == "yes" or "family" in response.lower() and "history" in response.lower() and not "no" in response.lower():
            st.session_state.user_profile["family_history_cancer"] = "Yes"
        elif response.lower() == "no" or "don't" in response.lower() and "have" in response.lower():
            st.session_state.user_profile["family_history_cancer"] = "No"
        elif "don't know" in response.lower() or "not sure" in response.lower() or "maybe" in response.lower() or "uncertain" in response.lower():
            st.session_state.user_profile["family_history_cancer"] = "I don't know"
        elif "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
            st.session_state.user_profile["family_history_cancer"] = "Not specified"
        else:
            # If we can't categorize, assume they're trying to tell us something about family history
            st.session_state.user_profile["family_history_cancer"] = "Yes - details: " + response
        
        # Always move to next question
        st.session_state.conv_stage = "ask_chronic_conditions"
        return None
    
    # Process chronic conditions (can be multiple)
    elif current_stage == "waiting_chronic_conditions":
        # Handle continue command
        if response.lower() == "continue":
            st.session_state.conv_stage = "ask_lifestyle"
            return None
        
        # Direct match for None button
        if response == "None":
            st.session_state.user_profile["chronic_conditions"] = []
            st.session_state.conv_stage = "ask_lifestyle"
            return None
            
        # Direct matches for other buttons
        if response in ["Hypertension", "Diabetes", "Anemia", "Thyroid disorder", "STI/RTI", "Other"]:
            if response not in st.session_state.user_profile["chronic_conditions"]:
                st.session_state.user_profile["chronic_conditions"].append(response)
                conditions = ", ".join(st.session_state.user_profile["chronic_conditions"])
                return f"I've noted your conditions: {conditions}. Do you have any other conditions? Select another or say 'Continue' to proceed."
            else:
                return "You've already selected this condition. Do you have any others? Select another or say 'Continue' to proceed."
            
        condition_mapping = {
            "none": "None",
            "no": "None",
            "nothing": "None",
            "high blood pressure": "Hypertension",
            "hypertension": "Hypertension",
            "blood pressure": "Hypertension",
            "sugar": "Diabetes",
            "diabetes": "Diabetes",
            "anemia": "Anemia",
            "blood": "Anemia",
            "iron": "Anemia",
            "thyroid": "Thyroid disorder",
            "sti": "STI/RTI",
            "std": "STI/RTI",
            "infection": "STI/RTI",
            "reproductive": "STI/RTI",
            "other": "Other"
        }
        
        # Check for "None" first
        if any(key in response.lower() for key in ["none", "no", "nothing", "healthy"]):
            # If None is selected, clear any existing conditions
            st.session_state.user_profile["chronic_conditions"] = []
            st.session_state.conv_stage = "ask_lifestyle"
            return None
        
        # Try to match their response to a known condition
        matched = False
        for key, value in condition_mapping.items():
            if key in response.lower() and value != "None":
                if value not in st.session_state.user_profile["chronic_conditions"]:
                    st.session_state.user_profile["chronic_conditions"].append(value)
                    matched = True
        
        if matched:
            conditions = ", ".join(st.session_state.user_profile["chronic_conditions"])
            return f"I've noted your conditions: {conditions}. Do you have any other conditions? Select another or say 'Continue' to proceed."
        else:
            # If they mentioned something we don't recognize, just add it as "Other"
            if "Other" not in st.session_state.user_profile["chronic_conditions"] and response.lower() not in ["skip", "prefer not", "next"]:
                st.session_state.user_profile["chronic_conditions"].append("Other: " + response)
                
            # Provide option to continue
            conditions = ", ".join(st.session_state.user_profile["chronic_conditions"])
            if conditions:
                return f"I've noted your conditions: {conditions}. Do you have any other conditions? Select another or say 'Continue' to proceed."
            else:
                # If we couldn't match anything and they have no conditions yet, just move forward
                st.session_state.conv_stage = "ask_lifestyle"
                return None
    
    # Process tobacco use
    elif current_stage == "waiting_tobacco":
        # Direct matches for buttons
        if response in ["Yes", "No", "Skip"]:
            if response == "Skip":
                st.session_state.user_profile["tobacco_use"] = "Not specified"
            else:
                st.session_state.user_profile["tobacco_use"] = response
            st.session_state.conv_stage = "ask_alcohol"
            return None
            
        if response.lower() == "yes" or "smoke" in response.lower() or "use tobacco" in response.lower():
            st.session_state.user_profile["tobacco_use"] = "Yes"
        elif response.lower() == "no" or "don't" in response.lower() or "do not" in response.lower():
            st.session_state.user_profile["tobacco_use"] = "No"
        elif "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
            st.session_state.user_profile["tobacco_use"] = "Not specified"
        else:
            # Default to No if unclear
            st.session_state.user_profile["tobacco_use"] = "No"
        
        # Always move to next question
        st.session_state.conv_stage = "ask_alcohol"
        return None
    
    # Process alcohol use
    elif current_stage == "waiting_alcohol":
        # Direct matches for buttons
        if response in ["Yes", "No", "Skip"]:
            if response == "Skip":
                st.session_state.user_profile["alcohol_use"] = "Not specified"
            else:
                st.session_state.user_profile["alcohol_use"] = response
            st.session_state.conv_stage = "ask_physical_activity"
            return None
            
        if response.lower() == "yes" or "drink" in response.lower() or "alcohol" in response.lower() and not "don't" in response.lower():
            st.session_state.user_profile["alcohol_use"] = "Yes"
        elif response.lower() == "no" or "don't" in response.lower() or "do not" in response.lower():
            st.session_state.user_profile["alcohol_use"] = "No"
        elif "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
            st.session_state.user_profile["alcohol_use"] = "Not specified"
        else:
            # Default to No if unclear
            st.session_state.user_profile["alcohol_use"] = "No"
        
        # Always move to next question
        st.session_state.conv_stage = "ask_physical_activity"
        return None
    
    # Process physical activity
    elif current_stage == "waiting_physical_activity":
        # Direct matches for buttons
        if response in ["Very active", "Moderately active", "Lightly active", "Sedentary", "Skip"]:
            if response == "Skip":
                st.session_state.user_profile["physical_activity"] = "Not specified"
            else:
                st.session_state.user_profile["physical_activity"] = response
            st.session_state.conv_stage = "provide_recommendation"
            return None
            
        activity_mapping = {
            "very active": "Very active",
            "very": "Very active",
            "lot": "Very active",
            "athlete": "Very active",
            "moderate": "Moderately active",
            "moderately": "Moderately active",
            "some": "Moderately active",
            "light": "Lightly active",
            "lightly": "Lightly active",
            "little": "Lightly active",
            "not much": "Lightly active",
            "sedentary": "Sedentary",
            "none": "Sedentary",
            "no": "Sedentary",
            "don't": "Sedentary",
            "sit": "Sedentary"
        }
        
        # Try to match their response
        matched = False
        for key, value in activity_mapping.items():
            if key in response.lower():
                st.session_state.user_profile["physical_activity"] = value
                matched = True
                break
        
        # If we couldn't match, still move forward
        if not matched:
            if "skip" in response.lower() or "prefer not" in response.lower() or "next" in response.lower():
                st.session_state.user_profile["physical_activity"] = "Not specified"
            else:
                # Default to moderately active if unclear
                st.session_state.user_profile["physical_activity"] = "Moderately active"
        
        # Always move to recommendation
        st.session_state.conv_stage = "provide_recommendation"
        return None
    
    # Process clinic info response
    elif current_stage == "waiting_clinic_info":
        if "yes" in response.lower() or "show" in response.lower():
            st.session_state.show_clinic_info = True
        else:
            message = "No problem. If you'd like clinic information in the future, just ask. Is there anything else I can help you with today?"
            st.session_state.conv_stage = "end"
            return message
    
    # Process post-visit annual wellness feedback
    elif current_stage == "waiting_annual_feedback":
        if "question" in response.lower():
            return "What questions do you have about your visit? I'm happy to explain any part of the examination or advice you received."
        elif "when" in response.lower() or "come back" in response.lower():
            return f"Based on your current health status, we recommend you have your next annual wellness exam in one year. I'll send you a reminder when it's time. For cervical cancer screening, women aged 30-65 should have an HPV test every 5 years. For breast cancer screening, women 40 and older should have a mammogram every 1-2 years. Is there anything else you'd like to know?"
        else:
            st.session_state.conv_stage = "end"
            return "I'm glad everything is clear! Remember that your annual wellness exam is an important part of maintaining your health. I'll be in touch in about a year to remind you about your next checkup. Feel free to reach out if you have any health questions before then!"
    
    # Process post-visit cervical screening feedback
    elif current_stage == "waiting_cervical_feedback":
        if "how" in response.lower() and "result" in response.lower():
            return "Your clinic will contact you when the results are ready, usually in 3-4 weeks. If they haven't contacted you after 4 weeks, you can call them directly. I'll also follow up with you once I receive information about your results. Would you like me to remind you in 3 weeks if you haven't heard anything?"
        elif "what" in response.lower() and "result" in response.lower():
            return "Your results will typically fall into one of three categories: normal (no abnormal cells found), minor abnormalities (often referred to as ASCUS or CIN-1, which may resolve on their own), or more significant abnormalities that require follow-up (CIN-2 or CIN-3). The majority of results are normal. Even with abnormal results, it rarely means cancer - it often just means some cells need monitoring or treatment to prevent potential future problems. Do you have any other questions?"
        else:
            # Set up for the results notification in 3-4 weeks
            st.session_state.conv_stage = "cervical_results_notification"
            return "Great! I'll follow up with you in about a3-4 weeks with your results. In the meantime, if you have any concerns or questions, feel free to reach out to me or your healthcare provider."
    
    # Process post-visit comprehensive screening feedback
    elif current_stage == "waiting_comprehensive_feedback":
        if "how" in response.lower() and "result" in response.lower():
            return "Your clinic will contact you when the results are ready, usually in 3-4 weeks. For both the cervical cancer screening and mammogram results. If they haven't contacted you after 4 weeks, you can call them directly. I'll also follow up with you once I receive information about your results. Would you like me to remind you in 3 weeks if you haven't heard anything?"
        elif "what" in response.lower() and "result" in response.lower():
            return "For your cervical screening, results will typically be normal, minor abnormalities that may resolve on their own, or more significant abnormalities requiring follow-up. For your mammogram, results will either be normal or require additional imaging. The majority of results are normal for both tests. Even with abnormal results, it rarely means cancer - it often just means additional evaluation is needed. Do you have any other questions?"
        else:
            # Set up for the results notification in 3-4 weeks
            st.session_state.conv_stage = "comprehensive_results_notification"
            return "Great! I'll follow up with you in about 3-4 weeks with your results for both screenings. In the meantime, if you have any concerns or questions, feel free to reach out to me or your healthcare provider."
    
    # Process cervical results response
    elif current_stage == "waiting_cervical_results_response":
        cervical_result = st.session_state.test_results.get("cervical", "normal")
        
        if "schedule" in response.lower():
            if cervical_result == "abnormal_minor":
                st.session_state.follow_up_scheduled = True
                st.session_state.next_appointment_date = "June 15, 2025"
                return f"I've scheduled your follow-up appointment for {st.session_state.next_appointment_date} at St. Mary's Health Center. This will be a simple check-up to see if the minor abnormal cells have resolved on their own, which they often do. Would you like a reminder a few days before the appointment?"
            elif cervical_result == "abnormal_serious":
                st.session_state.follow_up_scheduled = True
                st.session_state.next_appointment_date = "May 2, 2025"
                return f"I've scheduled your colposcopy for {st.session_state.next_appointment_date} at St. Mary's Health Center. This procedure allows the doctor to examine your cervix more closely. It's similar to your screening but with a special magnifying device. The doctor may take a small tissue sample (biopsy) if needed. Would you like me to explain more about what to expect during this procedure?"
        elif "cancer" in response.lower() or "mean" in response.lower():
            if cervical_result == "abnormal_minor":
                return "Having minor abnormal cells (ASCUS or CIN-1) is quite common and doesn't mean you have cancer. These cellular changes are often caused by temporary HPV infections that your body clears naturally over time. The follow-up is to monitor and make sure they resolve, which they do in most cases. This is why we do screenings - to catch any changes early when they're easy to monitor or treat."
            elif cervical_result == "abnormal_serious":
                return "Having abnormal cells classified as CIN-2 or CIN-3 doesn't mean you have cancer, but it does indicate more significant cellular changes that require closer examination and possibly treatment. These cells have a higher chance of developing into cancer over time if left untreated, which is why prompt follow-up is important. The good news is that when caught at this stage, treatment is usually very effective at preventing cancer from developing."
            else:
                return "Your normal results mean no abnormal cells were detected in your cervical screening sample. This is good news and means your risk of cervical cancer is very low at this time. Regular screenings are still important to maintain this low risk by catching any future changes early."
        elif "urgent" in response.lower():
            if cervical_result == "abnormal_minor":
                return "This is not urgent. Minor cell changes often resolve on their own within 6-12 months. The follow-up is precautionary to ensure the changes don't progress. There's no need to worry, but it is important to keep your follow-up appointment."
            elif cervical_result == "abnormal_serious":
                return "While this isn't an emergency, it is important to have the colposcopy within the next few weeks. These cell changes can potentially develop into cancer over time (usually years), but prompt evaluation and treatment is very effective at preventing this progression. The appointment I've scheduled for you is within the recommended timeframe."
        else:
            st.session_state.conv_stage = "end"
            if cervical_result == "normal":
                return "I'm glad I could share this good news with you! Continue with your regular health practices, and I'll be in touch when it's time for your next screening in 3-5 years. Feel free to contact me if you have any health questions in the meantime."
            else:
                return "I understand. Remember that these screenings are effective at finding changes early when they're most treatable. I'll send you a reminder before your upcoming appointment. If you have any other questions or concerns before then, please don't hesitate to reach out."
    
    # Process breast results response
    elif current_stage == "waiting_breast_results_response":
        breast_result = st.session_state.test_results.get("breast", "normal")
        
        if "schedule" in response.lower():
            if breast_result == "abnormal":
                st.session_state.follow_up_scheduled = True
                st.session_state.next_appointment_date = "May 5, 2025"
                return f"I've scheduled your follow-up imaging for {st.session_state.next_appointment_date} at St. Mary's Health Center. This will include additional mammogram views and possibly an ultrasound to get a better look at the area in question. These additional images help the radiologist determine if what they're seeing is normal breast tissue or something that needs further evaluation. Would you like more information about what to expect?"
        elif "mean" in response.lower():
            if breast_result == "abnormal":
                return "An abnormal mammogram simply means the radiologist saw an area that needs a closer look. This is quite common and happens in about 10% of mammograms. In most cases (over 80%), the follow-up imaging shows normal breast tissue. The initial screening mammogram takes general images, while the follow-up can focus specifically on areas of interest with specialized techniques. This is a normal part of the screening process for many women."
            else:
                return "Your normal results mean the radiologist did not see any areas of concern in your breast tissue. This is good news and means your risk of breast cancer is low at this time. Regular screenings are still important as they help catch any future changes early."
        elif "urgent" in response.lower():
            if breast_result == "abnormal":
                return "This is not urgent, but it is important to complete the follow-up imaging within the next few weeks. The vast majority of follow-up imaging shows normal results, but it's an important step to ensure nothing is missed. The appointment I've scheduled for you is within the recommended timeframe."
        else:
            st.session_state.conv_stage = "end"
            if breast_result == "normal":
                return "I'm glad I could share this good news with you! Continue with your regular health practices, and I'll be in touch when it's time for your next mammogram in 1-2 years. Feel free to contact me if you have any health questions in the meantime."
            else:
                return "I understand. Remember that these follow-up images are a normal part of the screening process for many women and usually show normal results. I'll send you a reminder before your upcoming appointment. If you have any other questions or concerns before then, please don't hesitate to reach out."
    
    # Process comprehensive results response
    elif current_stage == "waiting_comprehensive_results_response":
        cervical_result = st.session_state.test_results.get("cervical", "normal")
        breast_result = st.session_state.test_results.get("breast", "normal")
        
        if "schedule" in response.lower():
            # Prioritize the more serious follow-up
            if "colposcopy" in response.lower() or cervical_result == "abnormal_serious":
                st.session_state.follow_up_scheduled = True
                st.session_state.next_appointment_date = "May 2, 2025"
                return f"I've scheduled your colposcopy for {st.session_state.next_appointment_date} at St. Mary's Health Center. This procedure allows the doctor to examine your cervix more closely. " + (f"We'll also schedule your breast imaging follow-up separately." if breast_result == "abnormal" else "") + " Would you like me to explain more about what to expect during the colposcopy?"
            elif "imaging" in response.lower() or breast_result == "abnormal":
                st.session_state.follow_up_scheduled = True
                st.session_state.next_appointment_date = "May 5, 2025"
                return f"I've scheduled your follow-up breast imaging for {st.session_state.next_appointment_date} at St. Mary's Health Center. This will include additional mammogram views and possibly an ultrasound. " + (f"We'll also schedule your cervical follow-up separately." if cervical_result == "abnormal_minor" else "") + " Would you like more information about what to expect?"
            elif cervical_result == "abnormal_minor":
                st.session_state.follow_up_scheduled = True
                st.session_state.next_appointment_date = "June 15, 2025"
                return f"I've scheduled your cervical follow-up appointment for {st.session_state.next_appointment_date} at St. Mary's Health Center. This will be a simple check-up to see if the minor abnormal cells have resolved on their own, which they often do. Would you like a reminder a few days before the appointment?"
        elif "mean" in response.lower():
            response_text = ""
            if cervical_result != "normal":
                if cervical_result == "abnormal_minor":
                    response_text += "For your cervical screening, having minor abnormal cells (ASCUS or CIN-1) is quite common and doesn't mean you have cancer. These cellular changes are often caused by temporary HPV infections that your body clears naturally over time. The follow-up is to monitor and make sure they resolve, which they do in most cases.\n\n"
                else:  # abnormal_serious
                    response_text += "For your cervical screening, having abnormal cells classified as CIN-2 or CIN-3 doesn't mean you have cancer, but it does indicate more significant cellular changes that require closer examination and possibly treatment. These cells have a higher chance of developing into cancer over time if left untreated, which is why prompt follow-up is important.\n\n"
            
            if breast_result != "normal":
                response_text += "For your mammogram, an abnormal result simply means the radiologist saw an area that needs a closer look. This is quite common and happens in about 10% of mammograms. In most cases (over 80%), the follow-up imaging shows normal breast tissue.\n\n"
            
            if response_text:
                response_text += "These screenings are designed to catch changes early when they're easiest to address. Having follow-ups is a normal part of the screening process for many women."
                return response_text
            else:
                return "Your results were normal for both screenings, which is excellent news! This means no abnormal cells were detected in your cervical screening and no areas of concern were found in your breast tissue. This indicates your risk for both cervical and breast cancer is low at this time."
        elif "urgent" in response.lower():
            if cervical_result == "abnormal_serious":
                return "For your cervical screening results, while this isn't an emergency, it is important to have the colposcopy within the next few weeks. These cell changes can potentially develop into cancer over time (usually years), but prompt evaluation and treatment is very effective at preventing this progression."
            elif breast_result == "abnormal":
                return "For your mammogram, this is not urgent, but it is important to complete the follow-up imaging within the next few weeks. The vast majority of follow-up imaging shows normal results, but it's an important step to ensure nothing is missed."
            elif cervical_result == "abnormal_minor":
                return "For your cervical screening, this is not urgent. Minor cell changes often resolve on their own within 6-12 months. The follow-up is precautionary to ensure the changes don't progress. There's no need to worry, but it is important to keep your follow-up appointment."
            else:
                return "Since your results were normal, there's no urgency for follow-up testing. Just continue with your regular health practices."
        else:
            st.session_state.conv_stage = "end"
            if cervical_result == "normal" and breast_result == "normal":
                return "I'm glad I could share this good news with you! Continue with your regular health practices. I'll be in touch when it's time for your next screenings - cervical cancer screening in 3-5 years and breast cancer screening in 1-2 years. Feel free to contact me if you have any health questions in the meantime."
            else:
                return "I understand. Remember that these screenings are effective at finding changes early when they're most treatable. I'll send you a reminder before your upcoming appointment(s). If you have any other questions or concerns before then, please don't hesitate to reach out."
                
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
    # Special case for Continue button
    if reply == "Continue":
        response_message = process_user_response(reply)
        if response_message:
            st.session_state.messages.append({"role": "assistant", "content": response_message})
        else:
            update_conversation()
        
        # Clear quick replies
        st.session_state.quick_replies = []
        st.rerun()
        return

    # For regular replies, add to messages
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
            "current_location": "Pune",
            "marital_status": "Married",
            "education_level": "Secondary",
            "menstrual_regularity": "Regular",
            "pregnancies": "2",
            "contraceptive_method": "None",
            "presenting_complaints": [],
            "family_history_cancer": "No",
            "chronic_conditions": [],
            "tobacco_use": "No",
            "alcohol_use": "No",
            "physical_activity": "Moderately active"
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
            "current_location": "Pune",
            "marital_status": "Married",
            "education_level": "Secondary",
            "menstrual_regularity": "Regular",
            "pregnancies": "2",
            "contraceptive_method": "None",
            "presenting_complaints": [],
            "family_history_cancer": "No",
            "chronic_conditions": [],
            "tobacco_use": "No",
            "alcohol_use": "No",
            "physical_activity": "Moderately active"
        }
        st.session_state.conv_stage = "test_results_followup"
    elif demo_scenario == "Comprehensive Assessment":
        # Set up profile for comprehensive assessment
        st.session_state.user_profile = {
            "name": st.session_state.user_profile["name"] or "Priya",
            "age": 35,
            "location": "Pune",
            "current_location": "Pune"
        }
        st.session_state.conv_stage = "intro"
        st.session_state.assessment_path = determine_assessment_path(35)
    elif demo_scenario == "Post-Visit Annual Wellness":
        # Set up profile for post-visit annual wellness demo
        st.session_state.user_profile = {
            "name": st.session_state.user_profile["name"] or "Priya",
            "age": 35,
            "location": "Pune",
            "annual_checkup": "No",
            "cervical_screening": "Yes",
            "breast_screening": "Yes",
            "current_location": "Pune",
            "marital_status": "Married",
            "education_level": "Secondary"
        }
        st.session_state.conv_stage = "post_visit_annual"
        st.session_state.recommendations = ["an annual wellness exam"]
    elif demo_scenario == "Post-Visit Cervical Screening":
        # Set up profile for post-visit cervical screening demo
        st.session_state.user_profile = {
            "name": st.session_state.user_profile["name"] or "Priya",
            "age": 35,
            "location": "Pune",
            "annual_checkup": "No",
            "cervical_screening": "No",
            "breast_screening": "Yes",
            "current_location": "Pune",
            "marital_status": "Married",
            "education_level": "Secondary"
        }
        st.session_state.conv_stage = "post_visit_cervical"
        st.session_state.recommendations = ["an annual wellness exam that includes cervical cancer screening"]
        
        # Fast-forward to results notification mode if we have a selected result
        if "cervical_result_select" in st.session_state:
            st.session_state.conv_stage = "cervical_results_notification"
            # This will trigger an automatic message in the conversation update
    
    elif demo_scenario == "Post-Visit Comprehensive Screening":
        # Set up profile for post-visit comprehensive screening demo
        st.session_state.user_profile = {
            "name": st.session_state.user_profile["name"] or "Priya",
            "age": 45,
            "location": "Pune",
            "annual_checkup": "No",
            "cervical_screening": "No",
            "breast_screening": "No",
            "current_location": "Pune",
            "marital_status": "Married",
            "education_level": "Secondary"
        }
        st.session_state.conv_stage = "post_visit_comprehensive"
        st.session_state.recommendations = ["an annual wellness exam that includes both cervical and breast cancer screening"]
        
        # Fast-forward to results notification mode if we have selected results
        if "cervical_result_select" in st.session_state and "breast_result_select" in st.session_state:
            st.session_state.conv_stage = "comprehensive_results_notification"
            # This will trigger an automatic message in the conversation update

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
    # Add a "Continue" button for multiple selection questions
    if st.session_state.conv_stage in ["waiting_complaints", "waiting_chronic_conditions"]:
        if len(st.session_state.user_profile.get("presenting_complaints", [])) > 0 or len(st.session_state.user_profile.get("chronic_conditions", [])) > 0:
            st.session_state.quick_replies.append("Continue")
    
    # Create columns based on the number of quick replies
    num_cols = min(len(st.session_state.quick_replies), 3)
    cols = st.columns(num_cols)
    
    # Add buttons to each column
    buttons_per_col = (len(st.session_state.quick_replies) + num_cols - 1) // num_cols
    for i, reply in enumerate(st.session_state.quick_replies):
        col_idx = (i // buttons_per_col) % num_cols
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
