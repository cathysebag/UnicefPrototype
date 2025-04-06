// Women's Health Navigator Chatbot
// This chatbot helps women understand preventive healthcare recommendations
// with a focus on cervical cancer screening, HPV vaccination, and other women's health services

class HealthNavigatorBot {
  constructor() {
    this.userData = {
      name: "",
      age: 0,
      location: "",
      lastScreeningDate: null,
      lastCheckup: null,
      screeningHistory: {
        cervical: false,
        breast: false
      },
      hpvVaccinated: false,
      symptoms: [],
      riskFactors: []
    };
    
    this.clinics = {
      "Pune": [
        {
          name: "FOGSI Women's Health Center - Pune",
          address: "Near Jehangir Hospital, Pune, Maharashtra",
          services: ["cervical_cancer_screening", "breast_cancer_screening", "prenatal_care", "sti_testing"],
          phone: "+91-20-12345678",
          cost: "Free for basic screening",
          distance: "2.5 km"
        },
        {
          name: "Maternal Health Clinic - Shivajinagar",
          address: "Shivajinagar, Pune, Maharashtra",
          services: ["prenatal_care", "postnatal_care", "family_planning", "cervical_cancer_screening"],
          phone: "+91-20-87654321",
          cost: "₹200 for HPV testing",
          distance: "3.8 km"
        },
        {
          name: "Women's Wellness Center",
          address: "Koregaon Park, Pune, Maharashtra",
          services: ["general_wellness", "cervical_cancer_screening", "breast_cancer_screening", "sti_testing"],
          phone: "+91-20-23456789",
          cost: "₹150 for VIA testing",
          distance: "5.1 km"
        }
      ],
      "Pipili": [
        {
          name: "District Hospital Pipili",
          address: "Main Road, Pipili, Odisha",
          services: ["cervical_cancer_screening", "general_healthcare"],
          phone: "+91-6758-223456",
          cost: "₹300 for follow-up treatment",
          distance: "1.2 km"
        },
        {
          name: "Community Health Center",
          address: "Near Bus Stand, Pipili, Odisha",
          services: ["cervical_cancer_screening", "general_healthcare"],
          phone: "+91-6758-223789",
          cost: "₹250 for follow-up treatment",
          distance: "0.8 km"
        }
      ]
    };
    
    this.screeningInfo = {
      via: {
        name: "VIA Test",
        description: "Visual Inspection with Acetic Acid - a simple test where the doctor applies vinegar solution to the cervix and observes any changes that might indicate cancer or pre-cancer.",
        frequency: "Every 1 year",
        cost: "Usually free at primary health centers",
        preparation: "No special preparation needed"
      },
      pap: {
        name: "Pap Smear Test",
        description: "A procedure that collects cells from the cervix to check for abnormalities that may indicate cancer or pre-cancer.",
        frequency: "Every 3 years",
        cost: "Moderately priced, available at district hospitals",
        preparation: "Avoid sexual intercourse, douching, or using vaginal medications for 2 days before the test"
      },
      hpv: {
        name: "HPV Test",
        description: "Tests specifically for high-risk HPV infections that can lead to cervical cancer.",
        frequency: "Every 5 years",
        cost: "More expensive, available at private hospitals and medical colleges",
        preparation: "Similar to Pap test preparation"
      }
    };
    
    this.recommendationByAge = {
      "9-14": {
        hpvVaccine: "Recommended (2 doses)",
        screening: "Not yet required"
      },
      "15-29": {
        hpvVaccine: "Recommended (3 doses)",
        screening: "Start screening at 25 with Pap smear or VIA test"
      },
      "30-45": {
        hpvVaccine: "Consult doctor about vaccination benefits",
        screening: "HPV test or VIA test every 5 years"
      },
      "45-65": {
        hpvVaccine: "Not typically recommended",
        screening: "Continue screening until age 65"
      },
      "65+": {
        hpvVaccine: "Not recommended",
        screening: "Can discontinue after consistent negative results in the past 15 years"
      }
    };
  }

  // Start the conversation
  startConversation(userName, chw) {
    this.userData.name = userName;
    return `Hi ${userName}, this is your health assistant. ${chw || "Your community health worker"} recommended I reach out to you. I want to help you understand the recommended preventative healthcare you should have completed. Are you interested? It does not cost anything and I can help you find the right place and resources.`;
  }

  // Process user response to initial greeting
  processInitialResponse(response) {
    if (this.isPositiveResponse(response)) {
      return "Great, let's start with a few quick free questions. First, how old are you?";
    } else {
      return "I understand. If you change your mind, I'm here to help. Is there anything specific about women's health you're curious about?";
    }
  }

  // Process age response and determine next question
  processAgeResponse(age) {
    this.userData.age = parseInt(age);
    
    if (isNaN(this.userData.age)) {
      return "I didn't catch that. Please share your age as a number.";
    }
    
    return "Ok great. Have you had a doctor or nurse give you an exam in the last year for something unrelated to feeling sick?";
  }

  // Process checkup response
  processCheckupResponse(response) {
    this.userData.lastCheckup = this.isPositiveResponse(response);
    
    if (this.userData.age >= 30) {
      return "Have you had a cervical cancer screening test in the past 5 years?";
    } else if (this.userData.age >= 9 && this.userData.age <= 14) {
      return "Has your daughter received the HPV vaccine? This is recommended for girls aged 9-14 years to prevent cervical cancer in the future.";
    } else {
      return "Where are you currently located? This will help me recommend the nearest healthcare facilities.";
    }
  }

  // Process cervical screening response
  processCervicalScreeningResponse(response) {
    this.userData.screeningHistory.cervical = this.isPositiveResponse(response);
    
    if (this.userData.age >= 40) {
      return "Have you had a breast cancer screening test in the past 2 years?";
    } else {
      return "Where are you currently located? This will help me recommend the nearest healthcare facilities.";
    }
  }

  // Process breast screening response
  processBreastScreeningResponse(response) {
    this.userData.screeningHistory.breast = this.isPositiveResponse(response);
    return "Where are you currently located? This will help me recommend the nearest healthcare facilities.";
  }

  // Process location response
  processLocationResponse(location) {
    this.userData.location = location;
    return this.generateRecommendation();
  }

  // Generate recommendation based on user data
  generateRecommendation() {
    const ageGroup = this.getAgeGroup();
    const recommendation = this.recommendationByAge[ageGroup];
    const nearestClinic = this.findNearestClinic();
    
    let message = `${this.userData.name}, based on your answers, `;
    
    if (this.userData.age >= 30 && !this.userData.screeningHistory.cervical) {
      message += `I recommend you schedule a time for a cervical cancer screening test at the closest clinic, ${nearestClinic.name}, ${nearestClinic.address}, Phone: ${nearestClinic.phone}. `;
      
      if (this.userData.age >= 30 && this.userData.age <= 45) {
        message += `For your age group (${this.userData.age}), an HPV test is the best option, which should be done every 5 years. `;
      } else {
        message += `For your age group (${this.userData.age}), a VIA test is a good option, which is free and quick. `;
      }
      
      message += `Making an appointment is easy, call the number and say you want a cervical cancer screening. `;
    } else if (this.userData.age >= 9 && this.userData.age <= 14 && !this.userData.hpvVaccinated) {
      message += `I recommend HPV vaccination, which is best given at your age (9-14 years). The vaccination requires 2 doses, given 6 months apart. You can get this at ${nearestClinic.name}, ${nearestClinic.address}, Phone: ${nearestClinic.phone}. `;
      message += `This vaccination helps prevent cervical cancer later in life. `;
    } else if (this.userData.age >= 40 && !this.userData.screeningHistory.breast) {
      message += `I recommend you schedule a breast cancer screening. You can get this at ${nearestClinic.name}, ${nearestClinic.address}, Phone: ${nearestClinic.phone}. `;
    } else {
      message += `based on your age (${this.userData.age}) and screening history, you appear to be up-to-date with recommended preventive care. It's important to continue regular screenings. `;
      message += `Your nearest women's health center is ${nearestClinic.name}, ${nearestClinic.address}, Phone: ${nearestClinic.phone} if you need any services in the future. `;
    }
    
    message += "Do you want to learn more about why these screenings are important and what to expect?";
    
    return message;
  }

  // Process user's interest in learning more
  processLearnMoreResponse(response) {
    if (this.isPositiveResponse(response)) {
      if (this.userData.age >= 30 && !this.userData.screeningHistory.cervical) {
        return this.getCervicalCancerInfo();
      } else if (this.userData.age >= 9 && this.userData.age <= 14) {
        return this.getHPVVaccineInfo();
      } else if (this.userData.age >= 40 && !this.userData.screeningHistory.breast) {
        return this.getBreastCancerInfo();
      } else {
        return this.getGeneralPreventionInfo();
      }
    } else {
      return "No problem. If you have any questions in the future, feel free to ask. Would you like me to remind you when it's time for your next screening?";
    }
  }

  // Follow-up after test results
  followUpAfterResults(testType, result) {
    if (testType === "cervical" && result === "abnormal") {
      return `${this.userData.name}, the clinic notified me that your cervical cancer screening results came back and require follow-up, that may include treatment. The doctor requested you come back for another appointment. Do you need help scheduling? What questions do you have?`;
    } else if (testType === "cervical" && result === "normal") {
      return `${this.userData.name}, good news! Your cervical cancer screening results came back normal. You should have your next screening in ${this.userData.age >= 30 && this.userData.age <= 45 ? "5 years" : "1 year"}. I'll remind you when it's time. Do you have any questions?`;
    }
    
    return `${this.userData.name}, the clinic contacted me about your recent test results. They've asked for you to follow up. Can I help you schedule an appointment?`;
  }

  // Process follow-up response
  processFollowUpResponse(response, location) {
    if (location && location !== this.userData.location) {
      const clinics = this.clinics[location] || [];
      
      if (clinics.length > 0) {
        const clinic = clinics[0];
        return `Got it. In ${location}, I suggest you go to ${clinic.name}, ${clinic.address}, phone: ${clinic.phone}. Their price is ${clinic.cost}. Note there might be fewer clinics in this area, so appointments might take longer to get. Would you like me to help you schedule an appointment?`;
      } else {
        return `I don't have information about clinics in ${location} yet. Can you tell me which town or city you're nearest to, and I'll try to find resources for you?`;
      }
    }
    
    if (this.isPositiveResponse(response)) {
      return `I'll help you schedule. The doctor will likely discuss your results and possible next steps. This might include simple medication if it's an infection, or further testing or treatment if there are abnormal cells. Treatment is usually quick and effective, especially when caught early. Would you prefer a morning or afternoon appointment?`;
    } else {
      return `I understand. When you're ready to schedule, I'm here to help. Remember that follow-up is important, as early treatment is very effective. Is there anything else I can help with?`;
    }
  }

  // Helper methods
  isPositiveResponse(response) {
    response = response.toLowerCase();
    return response.includes('yes') || response.includes('yeah') || response.includes('sure') || response.includes('ok') || response.includes('okay');
  }

  getAgeGroup() {
    const age = this.userData.age;
    
    if (age >= 9 && age <= 14) return "9-14";
    if (age >= 15 && age <= 29) return "15-29";
    if (age >= 30 && age <= 45) return "30-45";
    if (age >= 46 && age <= 65) return "45-65";
    return "65+";
  }

  findNearestClinic() {
    const clinicsInLocation = this.clinics[this.userData.location] || this.clinics["Pune"];
    return clinicsInLocation[0]; // For simplicity, return the first clinic
  }

  // Information methods
  getCervicalCancerInfo() {
    return `
About Cervical Cancer:
• Cervical cancer is a type of cancer that occurs in the cells of the cervix - the lower part of the uterus.
• Almost all cervical cancers are caused by Human Papillomavirus (HPV), a common infection transmitted through intimate contact.
• Cervical cancer takes years to develop, often decades, and most women don't show any symptoms until the cancer is advanced.
• This is why regular screening is so important - it can detect changes before they become cancer.

About the screening:
• The screening is quick (5-10 minutes) and done by a female health worker or doctor.
• You'll lie on an exam table, and the provider will gently insert a device called a speculum to see your cervix.
• Depending on the test type, they'll either apply a vinegar solution (VIA test) or take a small sample of cells (Pap or HPV test).
• The test isn't painful but might be slightly uncomfortable.

Would you like me to help you schedule an appointment?`;
  }

  getHPVVaccineInfo() {
    return `
About HPV Vaccination:
• The HPV vaccine protects against the types of HPV that most commonly cause cervical cancer.
• It works best when given before any exposure to HPV, which is why it's recommended for girls aged 9-14 years.
• At this age, only 2 doses are needed (compared to 3 doses for older ages).
• The vaccine is safe and effective, with minimal side effects (usually just soreness at the injection site).
• Getting vaccinated now provides long-term protection against cervical cancer in the future.
• Even with vaccination, regular screening is still recommended after age 30.

Would you like me to help you schedule a vaccination appointment?`;
  }

  getBreastCancerInfo() {
    return `
About Breast Cancer Screening:
• Breast cancer screening can help find breast cancer early, when it's easier to treat.
• The main screening test is a mammogram, which is an X-ray of the breast.
• It's recommended every 2 years for women age 40 and older.
• The test takes about 20 minutes and involves compressing each breast between two plates for a few seconds.
• It might be uncomfortable but shouldn't be painful.
• Regular screenings, along with breast self-awareness, are the best ways to detect breast cancer early.

Would you like me to help you schedule a mammogram?`;
  }

  getGeneralPreventionInfo() {
    return `
General Health Tips for Women:
• Maintain a healthy diet rich in fruits and vegetables
• Exercise regularly
• Avoid or limit alcohol consumption
• Maintain a healthy weight
• Avoid all forms of tobacco
• For cervical cancer prevention, vaccination of girls aged 9-14 and regular screening for women aged 30-65 are the most effective strategies.
• Remember that most cervical cancers can be prevented through vaccination and screening.

Is there anything specific you'd like more information about?`;
  }
}

// Usage example:
/*
const bot = new HealthNavigatorBot();
let response = bot.startConversation("Meera", "Sameera");
console.log(response);

// Simulate user responses
response = bot.processInitialResponse("Yes");
console.log(response);

response = bot.processAgeResponse("45");
console.log(response);

response = bot.processCheckupResponse("No");
console.log(response);

response = bot.processCervicalScreeningResponse("No");
console.log(response);

response = bot.processBreastScreeningResponse("Yes");
console.log(response);

response = bot.processLocationResponse("Pune");
console.log(response);

response = bot.processLearnMoreResponse("Yes");
console.log(response);

// Later follow-up
response = bot.followUpAfterResults("cervical", "abnormal");
console.log(response);

response = bot.processFollowUpResponse("I'm actually not in this area now, I went to Pipili to take care of my ailing mother. I'm going to be here for the next couple of months.", "Pipili");
console.log(response);
*/

module.exports = HealthNavigatorBot;
