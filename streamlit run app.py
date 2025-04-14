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
        ["Basic Screening Recommendation", "Test Results Follow-up", "Location Change", "Comprehensive Assessment"],
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
        "message": "Thank you. What is your marital status?",
        "next_stage": "waiting_marital_status",
        "quick_replies": ["Single", "Married", "Widowed", "Divorced"]
    },
    "ask_education": {
        "message": "What is your highest level of education?",
        "next_stage": "waiting_education",
        "quick_replies": ["No formal education", "Primary", "Secondary", "Higher"]
    },
    "ask_menstrual_regularity": {
        "message": "Now let's talk about your health. Is your menstrual cycle regular?",
        "next_stage": "waiting_menstrual_regularity",
        "quick_replies": ["Regular", "Irregular", "Menopause", "Not applicable"]
    },
    "ask_pregnancies": {
        "message": "How many pregnancies have you had?",
        "next_stage": "waiting_pregnancies",
        "quick_replies": ["0", "1", "2", "3+"]
    },
    "ask_contraceptive": {
        "message": "Are you currently using any contraceptive method?",
        "next_stage": "waiting_contraceptive",
        "quick_replies": ["None", "Oral Pills", "IUD", "Condoms", "Sterilization", "Other"]
    },
    "ask_complaints": {
        "message": "Do you currently have any of these health concerns? (You can select multiple)",
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
        "quick_replies": ["Yes", "No", "I don't know"]
    },
    "ask_chronic_conditions": {
        "message": "Have you been diagnosed with any of these conditions? (You can select multiple)",
        "next_stage": "waiting_chronic_conditions",
        "quick_replies": ["None", "Hypertension", "Diabetes", "Anemia", "Thyroid disorder", "STI/RTI", "Other"]
    },
    "ask_lifestyle": {
        "message": "Let's talk about lifestyle. Do you use tobacco products?",
        "next_stage": "waiting_tobacco",
        "quick_replies": ["Yes", "No"]
    },
    "ask_alcohol": {
        "message": "Do you consume alcohol?",
        "next_stage": "waiting_alcohol",
        "quick_replies": ["Yes", "No"]
    },
    "ask_physical_activity": {
        "message": "How would you describe your level of physical activity?",
        "next_stage": "waiting_physical_activity",
        "quick_replies": ["Very active", "Moderately active", "Lightly active", "Sedentary"]
    },
    "provide_recommendation": {
        "message": lambda name, recommendations: f"{name}, based on your answers, I recommend you schedule {recommendations}. Would you like information on clinics near you?",
        "next_stage": "waiting_clinic_info",
        "quick_replies": ["Yes, show me clinics", "Not now"]
    }
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
    if user_profile["family_history_cancer"] == "Yes":
        recommendations.append("a discussion about your family history of cancer with your healthcare provider")
    
    if "Hypertension" in user_profile["chronic_conditions"] or "Diabetes" in user_profile["chronic_conditions"]:
        recommendations.append("regular monitoring of your chronic condition(s)")
    
    if user_profile["tobacco_use"] == "Yes" or user_profile["alcohol_use"] == "Yes":
        recommendations.append("lifestyle counseling")
    
    if user_profile["physical_activity"] == "Sedentary":
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
                else:
                    message = stage_info["message"](name)
            else:
                message = stage_info["message"]
                
            st.session_state.messages.append({"role": "assistant", "content": message})
            
            if "next_stage" in stage_info:
                st.session_state.conv_stage = stage_info["next_stage"]
            
            if "quick_replies" in stage_info:
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
            
            # If we got here, we couldn't parse the age
            return "I didn't understand that age. Please enter your age as a number between 18-120, or use one of the buttons below."
        except Exception as e:
            st.sidebar.error(f"Error processing age: {str(e)}")
            return "There was a problem with your age input. Please try entering just the number, like '45'."
    
    # Process marital status
    elif current_stage == "waiting_marital_status":
        if response in ["Single", "Married", "Widowed", "Divorced"]:
            st.session_state.user_profile["marital_status"] = response
            st.session_state.conv_stage = "ask_education"
        else:
            return "Please select your marital status from the options provided."
    
    # Process education level
    elif current_stage == "waiting_education":
        if response in ["No formal education", "Primary", "Secondary", "Higher"]:
            st.session_state.user_profile["education_level"] = response
            st.session_state.conv_stage = "ask_annual_checkup"
        else:
            return "Please select your education level from the options provided."
    
    # Process menstrual regularity
    elif current_stage == "waiting_menstrual_regularity":
        if response in ["Regular", "Irregular", "Menopause", "Not applicable"]:
            st.session_state.user_profile["menstrual_regularity"] = response
            st.session_state.conv_stage = "ask_pregnancies"
        else:
            return "Please select an option for your menstrual cycle regularity."
    
    # Process pregnancies
    elif current_stage == "waiting_pregnancies":
        if response in ["0", "1", "2", "3+"]:
            st.session_state.user_profile["pregnancies"] = response
            st.session_state.conv_stage = "ask_contraceptive"
        else:
            return "Please select the number of pregnancies you've had from the options provided."
    
    # Process contraceptive method
    elif current_stage == "waiting_contraceptive":
        if response in ["None", "Oral Pills", "IUD", "Condoms", "Sterilization", "Other"]:
            st.session_state.user_profile["contraceptive_method"] = response
            st.session_state.conv_stage = "ask_complaints"
        else:
            return "Please select your current contraceptive method from the options provided."
    
    # Process complaints (can be multiple)
    elif current_stage == "waiting_complaints":
        if response != "None":
            if response not in st.session_state.user_profile["presenting_complaints"]:
                st.session_state.user_profile["presenting_complaints"].append(response)
                return f"I've noted that you have {response}. Do you have any other concerns? Select another or proceed by clicking 'Continue'."
            else:
                return "You've already selected this concern. Do you have any others? Select another or proceed by clicking 'Continue'."
        else:
            # If None is selected, clear any existing complaints
            st.session_state.user_profile["presenting_complaints"] = []
            # Move to next question
            if "ask_annual_checkup" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_annual_checkup"
            elif "ask_cervical_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_cervical_screening"
            else:
                st.session_state.conv_stage = "ask_family_history"
    
    # Process Continue button for multiple selection questions
    elif response == "Continue":
        if current_stage == "waiting_complaints":
            if "ask_annual_checkup" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_annual_checkup"
            elif "ask_cervical_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_cervical_screening"
            else:
                st.session_state.conv_stage = "ask_family_history"
        elif current_stage == "waiting_chronic_conditions":
            st.session_state.conv_stage = "ask_lifestyle"
    
    # Process annual checkup response
    elif current_stage == "waiting_annual_checkup":
        if response in ["Yes", "No", "Not sure"]:
            st.session_state.user_profile["annual_checkup"] = response
            if "ask_cervical_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_cervical_screening"
            elif "ask_breast_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_breast_screening" 
            else:
                st.session_state.conv_stage = "ask_family_history"
        else:
            return "Please select whether you've had an annual checkup in the last year from the options provided."
    
    # Process cervical screening response
    elif current_stage == "waiting_cervical_screening":
        if response in ["Yes", "No", "I don't know"]:
            st.session_state.user_profile["cervical_screening"] = response
            if "ask_breast_screening" in st.session_state.assessment_path:
                st.session_state.conv_stage = "ask_breast_screening"
            else:
                st.session_state.conv_stage = "ask_family_history"
        else:
            return "Please select whether you've had a cervical cancer screening in the past 5 years from the options provided."
    
    # Process breast screening response
    elif current_stage == "waiting_breast_screening":
        if response in ["Yes", "No", "I don't know"]:
            st.session_state.user_profile["breast_screening"] = response
            st.session_state.conv_stage = "ask_family_history"
        else:
            return "Please select whether you've had a breast cancer screening in the past 5 years from the options provided."
    
    # Process family history
    elif current_stage == "waiting_family_history":
        if response in ["Yes", "No", "I don't know"]:
            st.session_state.user_profile["family_history_cancer"] = response
            st.session_state.conv_stage = "ask_chronic_conditions"
        else:
            return "Please select whether you have a family history of reproductive cancers from the options provided."
    
    # Process chronic conditions (can be multiple)
    elif current_stage == "waiting_chronic_conditions":
        if response != "None":
            if response not in st.session_state.user_profile["chronic_conditions"]:
                st.session_state.user_profile["chronic_conditions"].append(response)
                return f"I've noted that you have {response}. Do you have any other conditions? Select another or proceed by clicking 'Continue'."
            else:
                return "You've already selected this condition. Do you have any others? Select another or proceed by clicking 'Continue'."
        else:
            # If None is selected, clear any existing conditions
            st.session_state.user_profile["chronic_conditions"] = []
            # Move to next question
            st.session_state.conv_stage = "ask_lifestyle"
    
    # Process tobacco use
    elif current_stage == "waiting_tobacco":
        if response in ["Yes", "No"]:
            st.session_state.user_profile["tobacco_use"] = response
            st.session_state.conv_stage = "ask_alcohol"
        else:
            return "Please select whether you use tobacco products from the options provided."
    
    # Process alcohol use
    elif current_stage == "waiting_alcohol":
        if response in ["Yes", "No"]:
            st.session_state.user_profile["alcohol_use"] = response
            st.session_state.conv_stage = "ask_physical_activity"
        else:
            return "Please select whether you consume alcohol from the options provided."
    
    # Process physical activity
    elif current_stage == "waiting_physical_activity":
        if response in ["Very active", "Moderately active", "Lightly active", "Sedentary"]:
            st.session_state.user_profile["physical_activity"] = response
            st.session_state.conv_stage = "provide_recommendation"
        else:
            return "Please select your level of physical activity from the options provided."
    
    # Process clinic info response
    elif current_stage == "waiting_clinic_info":
        if "yes" in response.lower() or "show" in response.lower():
            st.session_state.show_clinic_info = True
        else:
            message = "No problem. If you'd like clinic information in the future, just ask. Is there anything else I can help you with today?"
            st.session_state.conv_stage = "end"
            return message
    
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
