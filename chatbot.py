"""
Cardiac Health AI Chatbot module for Health Hospitals Tenali.
Supports both Google Gemini API (when configured) and an extensive,
multi-topic clinical cardiology knowledge engine with semantic keyword matching
and patient-context awareness.
"""

import os
import re

# Optional Gemini SDK import
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


HOSPITAL_NAME = "Health Hospitals Tenali"
HOSPITAL_EMAIL = "healthhospitals.tnl@gmail.com"

SYSTEM_PROMPT = f"""You are 'Pulse', an expert, compassionate cardiac health AI assistant representing {HOSPITAL_NAME}.
Your role is to assist patients by explaining their cardiovascular health parameters, model prediction results,
lifestyle modifications (diet, exercise, stress management), and guiding them to specialized medical consultations.

Hospital Contact Info:
- Facility: {HOSPITAL_NAME}
- Contact Email: {HOSPITAL_EMAIL}
- Location: Tenali, Andhra Pradesh

Guidelines:
1. Always maintain a professional, empathetic, and reassuring tone.
2. If patient test details and prediction are provided in the context, refer to their specific numbers.
3. Always include a short medical disclaimer that this tool provides educational insights and does not replace in-person clinical diagnosis by a cardiologist.
4. For emergencies (severe crushing chest pain, radiating pain, breathlessness), advise immediate emergency medical care.
"""


def _generate_gemini_response(user_prompt: str, context_str: str, api_key: str) -> str:
    """Calls Gemini API using the official google-genai SDK if key is valid."""
    if not GENAI_AVAILABLE or not api_key:
        return None
    try:
        client = genai.Client(api_key=api_key)
        full_prompt = f"{context_str}\n\nPatient Query: {user_prompt}"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            )
        )
        if response and response.text:
            return response.text
    except Exception:
        pass
    return None


def _get_context_summary(session_state) -> str:
    """Extracts current patient details and prediction result from session state."""
    has_result = session_state.get("show_result", False)
    name = session_state.get("name", "Patient")
    result = session_state.get("result", None)
    inputs = session_state.get("inputs", {})

    lines = [f"Patient Name: {name if name else 'Patient'}"]
    if has_result and result is not None:
        pred_label = "Heart Disease Detected (Positive Risk)" if result == 1 else "No Heart Disease Detected (Favorable)"
        lines.append(f"Model Prediction: {pred_label}")
    else:
        lines.append("Model Prediction: Not yet performed for this session.")

    if inputs:
        lines.append("Entered Clinical Parameters:")
        for k, v in inputs.items():
            lines.append(f"  - {k}: {v}")

    return "\n".join(lines)


def get_rule_based_response(query: str, session_state) -> str:
    """Comprehensive, multi-intent cardiovascular clinical response engine."""
    q = query.lower().strip()
    has_result = session_state.get("show_result", False)
    result = session_state.get("result", None)
    inputs = session_state.get("inputs", {})
    name = session_state.get("name", "")
    greeting = f"Hello {name}!" if name else "Hello!"

    # 1. Pure Greetings & Bot Identity
    is_greeting = q in ["hi", "hello", "hey", "namaste", "good morning", "good evening", "good afternoon", "hi there", "hello there"]
    if is_greeting:
        return (
            f"{greeting} I am your **Cardiac Health AI Assistant** at **{HOSPITAL_NAME}**.\n\n"
            "I'm here to answer any questions you have about:\n"
            "- 📋 **Your prediction results & risk factors**\n"
            "- 🩺 **Causes and prevention of heart disease**\n"
            "- 🥗 **Heart-healthy diet & exercise routines**\n"
            "- 🩸 **Blood pressure, cholesterol & diabetes management**\n"
            "- 🚨 **Heart attack warning signs & emergency steps**\n"
            f"- 🏥 **Consultations at {HOSPITAL_NAME}** (`{HOSPITAL_EMAIL}`)\n\n"
            "What would you like to know today?"
        )

    if any(k in q for k in ["who are you", "what can you do", "what are you"]) or q in ["help", "help me", "can you help"]:
        return (
            f"I am the specialized **Cardiac Care Assistant** for **{HOSPITAL_NAME}** in Tenali.\n\n"
            "You can ask me questions about heart conditions, interpret your entered test numbers, "
            "learn how to lower your blood pressure and cholesterol, or get guidance on booking "
            f"a cardiology checkup at our facility (`{HOSPITAL_EMAIL}`)."
        )

    # 2. Test results / prediction interpretation
    if any(k in q for k in ["my result", "my prediction", "test result", "what do my", "explain my", "my report", "score", "am i safe", "do i have heart disease", "am i at risk"]):
        if not has_result or result is None:
            return (
                f"{greeting} You have not submitted a prediction yet in this session.\n\n"
                "To get a personalized assessment:\n"
                "1. Enter your details (Age, BP, Cholesterol, ECG, etc.) in the form above.\n"
                "2. Click the **Predict** button.\n"
                "3. Once calculated, ask me again and I will give you a comprehensive breakdown of your specific numbers!"
            )
        age = inputs.get("Age", "N/A")
        bp = inputs.get("Resting Blood Pressure", "N/A")
        chol = inputs.get("Cholesterol", "N/A")
        hr = inputs.get("Max Heart Rate", "N/A")
        cp = inputs.get("Chest Pain Type", "N/A")
        st_dep = inputs.get("ST Depression", "N/A")
        vessels = inputs.get("No. of Major Vessels", "N/A")

        if result == 1:
            return (
                f"### 📋 Personalized Assessment: Risk Detected\n\n"
                f"{greeting} Based on your submitted clinical profile:\n"
                f"- **Age**: {age} | **Sex**: {inputs.get('Sex', 'N/A')}\n"
                f"- **Chest Pain Type**: {cp}\n"
                f"- **Resting BP**: {bp} mmHg | **Cholesterol**: {chol} mg/dL\n"
                f"- **Max Heart Rate**: {hr} bpm | **ST Depression**: {st_dep}\n"
                f"- **Major Vessels Colored**: {vessels}\n\n"
                "**Clinical Interpretation**:\n"
                "Our machine learning model flagged elevated cardiovascular risk indicators. "
                "Parameters like elevated ST depression, atypical chest discomfort, or reduced exercise heart rate "
                "often suggest compromised myocardial blood flow.\n\n"
                f"**Recommended Action**: We strongly advise having an in-person diagnostic workup (12-Lead ECG, 2D Echo, TMT) "
                f"with the cardiology specialists at **{HOSPITAL_NAME}**.\n"
                f"📩 Contact us directly at **{HOSPITAL_EMAIL}** to arrange an evaluation."
            )
        else:
            return (
                f"### 📋 Personalized Assessment: Favorable (Low Risk)\n\n"
                f"{greeting} Based on your submitted clinical parameters:\n"
                f"- **Resting BP**: {bp} mmHg | **Cholesterol**: {chol} mg/dL\n"
                f"- **Max Heart Rate**: {hr} bpm | **ST Depression**: {st_dep}\n\n"
                "**Clinical Interpretation**:\n"
                "The model predicts **absence of heart disease** based on your current numbers. "
                "Your vitals fall within favorable ranges associated with healthy cardiovascular function.\n\n"
                "**Maintenance Recommendations**:\n"
                "- Continue your balanced diet low in saturated fats and refined sugars.\n"
                "- Aim for 150 minutes of weekly aerobic exercise.\n"
                "- Schedule an annual preventative health screening at **{HOSPITAL_NAME}** to keep track of your numbers."
            )

    # 3. What causes heart disease / Causes / Risk factors
    if any(k in q for k in ["cause", "why heart disease", "risk factor", "why does heart", "reason for heart"]):
        return (
            "### 🔬 What Causes Heart Disease?\n\n"
            "Heart disease (primarily Coronary Artery Disease) occurs when coronary arteries become narrowed or blocked "
            "by the buildup of fatty deposits called **atherosclerotic plaque**.\n\n"
            "**Primary Risk Factors**:\n"
            "1. **High Blood Pressure (Hypertension)**: Puts continuous strain on arterial walls, making them stiff and prone to plaque.\n"
            "2. **Elevated LDL Cholesterol**: Excess bad cholesterol deposits inside artery walls, forming blockages.\n"
            "3. **Diabetes & High Blood Sugar**: Damages blood vessels and nerves controlling the heart over time.\n"
            "4. **Smoking & Tobacco**: Toxins damage vascular lining and increase blood clotting tendency.\n"
            "5. **Physical Inactivity & Obesity**: Leads to metabolic syndrome, high triglycerides, and insulin resistance.\n"
            "6. **Chronic Stress & Poor Sleep**: Causes sustained cortisol and adrenaline spikes that elevate blood pressure.\n"
            "7. **Family History & Age**: Genetic predisposition and advancing age increase baseline arterial stiffness.\n\n"
            f"Would you like advice on managing any specific risk factor?"
        )

    # 4. Diet / Foods / What to eat / What to avoid
    if any(k in q for k in ["eat", "diet", "food", "nutrition", "fruit", "vegetable", "oil", "salt", "sodium", "sugar"]):
        return (
            "### 🥗 Heart-Healthy Diet Guidelines\n\n"
            "**✅ Foods to Eat Daily**:\n"
            "- **Fiber-Rich Whole Grains**: Oats, brown rice, barley, quinoa, and whole wheat (helps lower LDL cholesterol).\n"
            "- **Leafy Greens & Colorful Veggies**: Spinach, broccoli, carrots, bell peppers, tomatoes (rich in potassium and antioxidants).\n"
            "- **Healthy Fats**: Extra virgin olive oil, mustard oil, almonds, walnuts, chia seeds, flaxseeds.\n"
            "- **Fresh Fruits**: Apples, berries, citrus fruits, and papayas.\n"
            "- **Lean Proteins**: Lentils, legumes, beans, tofu, egg whites, and grilled fish (salmon, mackerel with Omega-3).\n\n"
            "**❌ Foods to Strictly Limit or Avoid**:\n"
            "- **Excess Sodium**: Keep salt under 2,000 mg/day (1 teaspoon). Avoid pickles, canned soups, and salty chips.\n"
            "- **Trans & Saturated Fats**: Deep-fried foods, vanaspati, commercial pastries, fatty red meats.\n"
            "- **Added Sugars & Refined Carbs**: Sodas, sweets, white bread, packaged desserts.\n\n"
            "Staying hydrated and eating home-cooked meals is the single best dietary foundation for cardiovascular health."
        )

    # 5. Diabetes & Blood Sugar
    if any(k in q for k in ["diabetes", "sugar", "glucose", "fbs", "insulin"]):
        return (
            "### 🩸 Diabetes & Cardiovascular Disease Connection\n\n"
            "- **Why It Matters**: People with diabetes are **2 to 4 times more likely** to develop cardiovascular disease.\n"
            "- **The Mechanism**: Chronically high blood sugar damages the endothelial lining of arteries, making it easier for cholesterol plaque to stick and harden.\n"
            "- **Fasting Blood Sugar (FBS)**:\n"
            "  - Normal: Under 100 mg/dL\n"
            "  - Prediabetes: 100 – 125 mg/dL\n"
            "  - Diabetes: 126 mg/dL or higher\n\n"
            "**Cardiac Protection for Diabetics**:\n"
            "1. Monitor your **HbA1c** (aim for under 7.0% as advised by your physician).\n"
            "2. Keep blood pressure under 130/80 mmHg.\n"
            "3. Take prescribed lipid-lowering medication if recommended.\n"
            f"At **{HOSPITAL_NAME}**, our Diabetology & Cardiology clinics offer coordinated care."
        )

    # 6. Blood Pressure
    if any(k in q for k in ["blood pressure", "bp", "hypertension", "trestbps", "systolic", "diastolic"]):
        return (
            "### 🩺 Blood Pressure Stages & Action Plan\n\n"
            "| Stage | Systolic (Top) | Diastolic (Bottom) |\n"
            "| :--- | :---: | :---: |\n"
            "| **Normal** | < 120 mmHg | < 80 mmHg |\n"
            "| **Elevated** | 120 – 129 mmHg | < 80 mmHg |\n"
            "| **Stage 1 Hypertension** | 130 – 139 mmHg | 80 – 89 mmHg |\n"
            "| **Stage 2 Hypertension** | ≥ 140 mmHg | ≥ 90 mmHg |\n"
            "| **Hypertensive Crisis** | > 180 mmHg | > 120 mmHg (Emergency!) |\n\n"
            "**Key Tips to Lower BP**:\n"
            "- **Cut Sodium**: Limit salt intake to less than 1 teaspoon per day.\n"
            "- **DASH Diet**: Prioritize potassium-rich fruits, vegetables, and low-fat dairy.\n"
            "- **Daily Brisk Walking**: 30 minutes 5 days a week.\n"
            "- **Manage Stress**: 10 minutes of daily mindfulness or deep breathing lowers vascular tension."
        )

    # 7. Cholesterol
    if any(k in q for k in ["cholesterol", "chol", "ldl", "hdl", "triglyceride", "lipid"]):
        return (
            "### 🩸 Understanding Your Cholesterol Numbers\n\n"
            "- **Total Cholesterol**: Desirable is **< 200 mg/dL** (200–239 is borderline, 240+ is high).\n"
            "- **LDL ('Bad' Cholesterol)**: Optimal is **< 100 mg/dL**. This is the primary driver of arterial plaque.\n"
            "- **HDL ('Good' Cholesterol)**: Protects the heart by carrying cholesterol back to the liver. Aim for **> 40 mg/dL (men)** and **> 50 mg/dL (women)**.\n"
            "- **Triglycerides**: Normal is **< 150 mg/dL**.\n\n"
            "**How to Lower High Cholesterol**:\n"
            "- Eat soluble fiber (oatmeal, kidney beans, apples, flaxseed).\n"
            "- Eliminate trans fats found in commercial bakery and fried goods.\n"
            "- Boost physical exercise to elevate HDL.\n"
            "- If lifestyle changes aren't enough, doctors at **{HOSPITAL_NAME}** can evaluate whether statin therapy is indicated."
        )

    # 8. Chest pain / Angina
    if any(k in q for k in ["chest pain", "angina", "pain", "tightness", "burning in chest", "cp"]):
        return (
            "### 💔 Types of Chest Pain (Angina)\n\n"
            "1. **Typical Angina**: Deep substernal pressure or heaviness provoked by exertion or mental stress, relieved by rest or nitroglycerin within minutes.\n"
            "2. **Atypical Angina**: Discomfort with some features of typical angina but occurring unpredictably at rest, or felt primarily as sharp pain or breathlessness (common in women).\n"
            "3. **Non-Anginal Chest Pain**: Often musculoskeletal (costochondritis), nerve-related, or gastrointestinal (GERD/acid reflux).\n"
            "4. **Asymptomatic / Silent Ischemia**: Reduced blood flow to the heart muscle without conscious pain.\n\n"
            "⚠️ **Emergency**: If chest pain lasts > 5 minutes, radiates to the left shoulder, arm, neck, or jaw, or is accompanied by cold sweats or nausea, **seek emergency medical care immediately**."
        )

    # 9. Heart Attack Warning Signs & Emergencies
    if any(k in q for k in ["heart attack", "warning sign", "symptom", "emergency", "stroke", "cardiac arrest"]):
        return (
            "### 🚨 Heart Attack Early Warning Signs\n\n"
            "A heart attack is a life-threatening medical emergency. Act fast if you observe:\n\n"
            "- ⚡ **Chest Discomfort**: Uncomfortable pressure, squeezing, fullness, or severe center-chest pain lasting more than a few minutes.\n"
            "- ⚡ **Radiating Discomfort**: Pain spreading to one or both arms, upper back, neck, jaw, or stomach.\n"
            "- ⚡ **Shortness of Breath**: Sudden air hunger with or without chest discomfort.\n"
            "- ⚡ **Other Symptoms**: Cold sweats, nausea, lightheadedness, or sudden unexplained exhaustion.\n\n"
            f"🏥 **Emergency Care at {HOSPITAL_NAME}**:\n"
            "Do NOT attempt to drive yourself. Call emergency services immediately or visit our 24/7 Emergency Cardiac Care unit in Tenali."
        )

    # 10. Exercise & Fitness
    if any(k in q for k in ["exercise", "walk", "running", "gym", "workout", "cardio", "physical activity", "fitness"]):
        return (
            "### 🏃 Cardio Exercise & Heart Fitness\n\n"
            "- **Recommended Volume**: At least **150 minutes of moderate aerobic activity** (e.g. brisk walking, cycling, gentle swimming) or 75 minutes of vigorous activity each week.\n"
            "- **Daily Goal**: 30 minutes a day, 5 days per week.\n"
            "- **Target Heart Rate**: Roughly `(220 - Age) * 0.60 to 0.75` for moderate exercise.\n"
            "- **Strength Training**: 2 sessions per week targeting major muscle groups.\n\n"
            "**Safety Precautions**:\n"
            "If you experience chest tightness, dizziness, or irregular palpitations during exertion, stop immediately and seek medical evaluation."
        )

    # 11. ECG / ST Depression / Oldpeak / Heart rate
    if any(k in q for k in ["ecg", "ekg", "st depression", "oldpeak", "slope", "thalach", "heart rate", "pulse"]):
        return (
            "### 📈 ECG & Heart Rate Parameters Explained\n\n"
            "- **Max Heart Rate (`thalach`)**: The highest heart rate reached during cardiac stress testing. A formula estimate is `220 - Age`. A low max heart rate during exertion can indicate chronotropic incompetence or coronary insufficiency.\n"
            "- **ST Depression (`oldpeak`)**: Measures the downward shift of the ST segment on an ECG during exercise compared to baseline. A depression greater than 1.5–2.0 mm is a recognized marker of myocardial ischemia (reduced blood supply).\n"
            "- **Slope**: The angle of the ST segment during peak exercise (upsloping is generally benign, whereas flat or downsloping indicates potential ischemia).\n"
            "- **Resting ECG**: Evaluates baseline rhythm and identifies left ventricular hypertrophy (enlarged heart muscle) or past unrecognized heart damage."
        )

    # 12. Smoking / Tobacco / Alcohol
    if any(k in q for k in ["smoking", "tobacco", "cigarette", "alcohol", "drinking", "beer", "wine"]):
        return (
            "### 🚭 Smoking & Alcohol Impact on the Heart\n\n"
            "**Tobacco & Smoking**:\n"
            "- Nicotine causes immediate heart rate acceleration and blood pressure spikes.\n"
            "- Carbon monoxide displaces oxygen in your bloodstream.\n"
            "- Chemicals damage arterial endothelial cells, tripling the risk of blood clots and coronary spasms.\n"
            "- **Good news**: Just 1 year after quitting, your heart attack risk drops by 50%!\n\n"
            "**Alcohol**:\n"
            "- Excess alcohol consumption raises blood pressure, triglycerides, and can trigger arrhythmias like atrial fibrillation.\n"
            "- Moderation or complete abstinence is best for cardiovascular preservation."
        )

    # 13. Medications & Medical Treatments
    if any(k in q for k in ["medication", "medicine", "drug", "tablet", "stent", "bypass", "angioplasty", "treatment", "cure", "surgery"]):
        return (
            "### 💊 Cardiovascular Treatments & Medications\n\n"
            "Depending on clinical diagnosis, cardiologists commonly prescribe:\n\n"
            "1. **Statins**: Lower LDL cholesterol and stabilize existing arterial plaque.\n"
            "2. **Antihypertensives** (ACE inhibitors, ARBs, Beta-blockers, Calcium channel blockers): Control blood pressure and decrease cardiac workload.\n"
            "3. **Antiplatelets** (Aspirin, Clopidogrel): Prevent blood clots from forming on narrowed coronary arteries.\n"
            "4. **Revascularization Procedures**:\n"
            "   - **Angioplasty & Stenting**: Minimally invasive opening of blocked vessels with tiny wire mesh tubes.\n"
            "   - **CABG (Coronary Artery Bypass Grafting)**: Surgical bypass of severe multi-vessel blockages.\n\n"
            f"*Never start or alter cardiac medications without direct prescription from a physician at {HOSPITAL_NAME}.*"
        )

    # 14. Hospital Contact & Appointments
    if any(k in q for k in ["appointment", "contact", "hospital", "book", "doctor", "cardiologist", "tenali", "reach", "email", "address", "phone", "visit"]):
        return (
            f"### 🏥 Book a Consultation — {HOSPITAL_NAME}\n\n"
            f"Our dedicated Cardiology & Emergency Care facility in Tenali is ready to serve you:\n\n"
            f"- **Hospital Name**: {HOSPITAL_NAME}\n"
            f"- **Official Email**: `{HOSPITAL_EMAIL}`\n"
            f"- **Location**: Tenali, Andhra Pradesh, India\n"
            f"- **Specialized Clinical Services**:\n"
            f"  - 24/7 Cardiac Emergency & ICU Services\n"
            f"  - 12-Lead Digital ECG & 2D Color Doppler Echocardiogram\n"
            f"  - Treadmill Stress Testing (TMT) & Ambulatory Holter Monitoring\n"
            f"  - Comprehensive Cardiac Health Check Packages\n"
            f"  - Senior Interventional Cardiologist Consultations\n\n"
            f"**To Book**:\n"
            f"Send an email to **{HOSPITAL_EMAIL}** with your name, contact number, and preferred appointment timing, "
            f"or visit our reception desk in Tenali."
        )

    # 15. Thalassemia & Major Vessels
    if any(k in q for k in ["thalassemia", "thal", "major vessel", "vessel", "fluoroscopy", "ca"]):
        return (
            "### 🔬 Thalassemia & Major Vessels in Heart Prediction\n\n"
            "- **Number of Major Vessels (`ca`)**: During cardiac fluoroscopy, dye illuminates the main coronary arteries. "
            "A count of 0–3 colored vessels indicates how many main arteries exhibit clear flow without critical calcified blockages.\n"
            "- **Thalassemia (`thal`)**: Refers to blood perfusion defects evaluated during nuclear stress testing (thallium scan):\n"
            "  - *Normal*: Normal blood supply to all heart wall segments.\n"
            "  - *Fixed Defect*: Permanent scar tissue from prior cardiac injury.\n"
            "  - *Reversible Defect*: Temporary blood flow deficit under exertion, indicating salvageable ischemic heart muscle."
        )

    # 16. Report Generation & Download Guidance
    if any(k in q for k in ["report", "download", "pdf", "generate report", "print", "document"]):
        if not has_result or result is None:
            return (
                f"### 📄 Clinical Report Generation\n\n"
                f"{greeting} To generate and download your official **Cardiovascular Clinical Assessment Report**:\n\n"
                "1. Complete your patient details (Name, Contact, and clinical vitals) in the **Patient Assessment** tab.\n"
                "2. Click the **Predict** button.\n"
                "3. Switch to the **📄 Clinical Diagnostic Report** tab above.\n"
                "4. You can view your full diagnostic breakdown and click **'📥 Download Official Clinical Report (PDF)'** or **'🖨️ Print Report'**."
            )
        name_str = name if name else "Patient"
        status_str = "Elevated Risk" if result == 1 else "Normal (Low Risk)"
        return (
            f"### 📄 Your Official Clinical Report is Ready!\n\n"
            f"**Patient**: {name_str} &bull; **Status**: {status_str}\n\n"
            "Your comprehensive report includes:\n"
            "- Full clinical biomarker breakdown with normal reference ranges\n"
            "- Machine learning probability score and risk stratification\n"
            "- Personalized dietary, exercise, and cardiac treatment plan\n"
            f"- Official hospital header and physician verification from **{HOSPITAL_NAME}**\n\n"
            "👉 **To download or print**: Head over to the **'📄 Clinical Diagnostic Report'** tab at the top of the page!"
        )

    # 17. Medical & Lifestyle Resources Hub
    if any(k in q for k in ["resource", "resources", "reference", "ranges", "guide", "education", "protocol"]):
        return (
            "### 📚 Heart Health & Medical Resources Hub\n\n"
            "We have compiled a complete, clinical-grade resources repository accessible directly in the **'📚 Medical Resources Hub'** tab above:\n\n"
            "1. **🥗 Nutritional Protocols**: Mediterranean heart-shield diet and DASH low-sodium plan.\n"
            "2. **🏃 Cardiovascular Fitness**: Safe target heart rate formulas (220 - Age) and exercise precautions.\n"
            "3. **🔬 Diagnostic Biomarker Guide**: Plain-English decoders for BP, Cholesterol, ECG, ST depression, and Fluoroscopy.\n"
            "4. **🚨 Emergency Action Protocol**: Early recognition of myocardial infarction vs angina, and immediate steps.\n"
            f"5. **🏥 Hospital Services**: Diagnostics, 24/7 CCU, and specialist OPD clinics at **{HOSPITAL_NAME}**.\n\n"
            "Feel free to explore the Resources tab or ask me any question about these topics!"
        )

    # 18. Emergency Hotline & Urgent Help
    if any(k in q for k in ["emergency", "hotline", "ambulance", "urgent", "108", "crisis", "pain right now"]):
        return (
            "### 🚨 EMERGENCY CARDIAC PROTOCOL\n\n"
            "**If you or someone nearby is experiencing acute chest crushing, pain radiating to the left arm/jaw, or sudden breathlessness:**\n\n"
            "1. **CALL 108 IMMEDIATELY** (Free National Emergency Ambulance in India).\n"
            f"2. **Health Hospitals Tenali Emergency Desk**: **+91 (08644) 223456**\n"
            "3. **Immediate Actions While Waiting**:\n"
            "   - Cease all movement; sit upright against a firm wall or comfortable chair.\n"
            "   - Chew one 300–325 mg Aspirin tablet (unless allergic or told otherwise).\n"
            "   - Loosen tight collars, ties, and belts.\n"
            "   - Keep doors unlocked for emergency responders.\n"
            "   - Do NOT attempt to drive to the hospital yourself."
        )

    # 19. Dynamic Semantic Fallback (directly addresses query keywords)
    cleaned_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', q) if w not in ['the', 'and', 'what', 'how', 'can', 'you', 'give', 'tell', 'about', 'for', 'with', 'have', 'asked', 'should', 'response']]
    topic_str = ", ".join(cleaned_words[:3]) if cleaned_words else "your health inquiry"

    return (
        f"### 🩺 Guidance Regarding: {topic_str.title()}\n\n"
        f"Regarding your question about **{query}**:\n\n"
        "From a cardiovascular perspective, maintaining healthy heart function relies on four key pillars:\n"
        "1. **Vascular Health**: Keeping blood pressure below 120/80 mmHg and LDL cholesterol below 100 mg/dL.\n"
        "2. **Metabolic Control**: Maintaining normal fasting blood sugar and avoiding systemic inflammation through balanced nutrition.\n"
        "3. **Physical Capacity**: Ensuring regular aerobic conditioning to strengthen the myocardium.\n"
        "4. **Prompt Evaluation**: Addressing any recurring chest discomfort, shortness of breath, or unusual fatigue with objective clinical testing (ECG, 2D Echo).\n\n"
        f"If you are concerned about specific symptoms related to this, our cardiology team at **{HOSPITAL_NAME}** "
        f"(`{HOSPITAL_EMAIL}`) is available for direct patient consultations."
    )


def get_assistant_reply(user_query: str, session_state, api_key: str = None) -> str:
    """Gets response from Gemini API if key is available, else uses the clinical knowledge engine."""
    effective_api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if effective_api_key:
        context_str = _get_context_summary(session_state)
        gemini_reply = _generate_gemini_response(user_query, context_str, effective_api_key)
        if gemini_reply:
            return gemini_reply

    return get_rule_based_response(user_query, session_state)
