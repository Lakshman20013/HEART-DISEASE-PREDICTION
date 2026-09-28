import streamlit as st
import numpy as np
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import os
import chatbot
import report_generator

# --- Responsive Page Setup and Theme Colors ---
st.set_page_config(
    page_title="Demo Health Heart Disease Prediction & Report Generation",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Modern, Clean UI, Animations & Accessibility ---
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
  
  html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  }
  
  .app-title {
    text-align: center;
    font-size: clamp(2.0rem, 5vw, 3.0rem);
    font-weight: 800;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #c02433 0%, #7d2131 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .app-subtitle {
    text-align: center;
    font-size: clamp(1.0rem, 2.5vw, 1.25rem);
    color: #64748b;
    margin-bottom: 24px;
    font-weight: 500;
  }
  
  .metric-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    text-align: center;
    transition: transform 0.2s ease;
  }
  .metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
  }
  
  .resource-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e2e8f0;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  }
  .resource-card h4 {
    color: #c02433;
    margin-top: 0;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .status-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.05em;
  }
  
  div.stForm button[kind="primary"] {
    background: linear-gradient(90deg, #c02433 0%, #7d2131 100%) !important;
    color: white !important;
    font-weight: 800 !important;
    font-size: 1.1rem !important;
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(192, 36, 51, 0.35);
    transition: all 0.2s;
  }
  div.stForm button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(192, 36, 51, 0.5);
  }
  
  .download-btn-container {
    text-align: center;
    margin: 20px 0;
  }
  
  .caption-custom {
    text-align: center;
    font-size: 0.95rem;
    color: #64748b;
    margin-top: 3rem;
    line-height: 1.8;
  }
</style>
""", unsafe_allow_html=True)

# --- Hero Header Section ---
st.markdown("""
<div class="app-title">DEMO HEALTH HEART DISEASE PREDICTION & REPORT GENERATION</div>
<div class="app-subtitle">Health Hospitals Tenali &bull; Clinical AI Screening & Diagnostic Reporting Demo</div>
<div style='text-align:center;'>
  <img src='https://img.icons8.com/color/96/heart-with-pulse--v2.png'
       width='64' style='margin-bottom:15px; animation: heartBeat 1.5s infinite; filter: drop-shadow(0 2px 12px rgba(215, 38, 61, 0.4));'/>
</div>
""", unsafe_allow_html=True)

# --- Dropdown options for user inputs with friendly strings ---
dropdown_options = {
    "Age": [str(i) for i in range(29, 81)],
    "Sex": ["Female", "Male"],
    "Chest Pain Type": ["Typical angina", "Atypical angina", "Non-anginal", "Asymptomatic"],
    "Resting Blood Pressure": [str(i) for i in range(80, 201)],
    "Cholesterol": [str(i) for i in range(126, 565)],
    "Fasting Blood Sugar": ["No", "Yes"],
    "Resting ECG": ["Normal", "ST-T abnormality", "Left ventricular hypertrophy"],
    "Max Heart Rate": [str(i) for i in range(71, 203)],
    "Exercise Induced Angina": ["No", "Yes"],
    "ST Depression": [f"{x/10:.1f}" for x in range(0, 63)],
    "Slope": ["Upsloping", "Flat", "Downsloping"],
    "No. of Major Vessels": [str(i) for i in range(0, 4)],
    "Thalassemia": ["Normal", "Fixed defect", "Reversible defect"],
}

mapping_dict = {
    "Sex": {"Female": 0, "Male": 1},
    "Chest Pain Type": {"Typical angina": 0, "Atypical angina": 1, "Non-anginal": 2, "Asymptomatic": 3},
    "Fasting Blood Sugar": {"No": 0, "Yes": 1},
    "Resting ECG": {"Normal": 0, "ST-T abnormality": 1, "Left ventricular hypertrophy": 2},
    "Exercise Induced Angina": {"No": 0, "Yes": 1},
    "Slope": {"Upsloping": 0, "Flat": 1, "Downsloping": 2},
    "Thalassemia": {"Normal": 1, "Fixed defect": 2, "Reversible defect": 3},
}

features_left = [
    "Age",
    "Sex",
    "Chest Pain Type",
    "Resting Blood Pressure",
    "Cholesterol",
    "Fasting Blood Sugar",
    "Resting ECG",
]
features_right = [
    "Max Heart Rate",
    "Exercise Induced Angina",
    "ST Depression",
    "Slope",
    "No. of Major Vessels",
    "Thalassemia",
]

def convert_selection(feature, selection):
    if feature in mapping_dict:
        return mapping_dict[feature][selection]
    else:
        try:
            return float(selection) if '.' in selection else int(selection)
        except Exception:
            return 0

# --- Save Patient Details Function ---
def save_patient_details(data_dict, filename="outputs/patient_details.xlsx"):
    ordered_keys = ['Name', 'Contact'] + [k for k in data_dict.keys() if k not in ['Name', 'Contact']]
    df = pd.DataFrame([[data_dict.get(k, "") for k in ordered_keys]], columns=ordered_keys)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if os.path.exists(filename):
        try:
            df_existing = pd.read_excel(filename)
            for col in ordered_keys:
                if col not in df_existing.columns:
                    df_existing[col] = ""
            df_existing = df_existing[ordered_keys]
            df = pd.concat([df_existing, df], ignore_index=True)
        except Exception:
            pass
    df.to_excel(filename, index=False)

# Check for public link file
public_link = None
live_link_file = os.path.join("outputs", "LIVE_URL.txt")
if os.path.exists(live_link_file):
    try:
        with open(live_link_file, "r") as f:
            content = f.read().strip()
            if content.startswith("http"):
                public_link = content
    except Exception:
        pass

# --- Sidebar Hospital & AI Settings ---
with st.sidebar:
    st.markdown("## 🏥 Health Hospitals Tenali")
    st.markdown("**Centre for Excellence in Cardiology**")
    st.info(f"📧 **Contact:**\n{chatbot.HOSPITAL_EMAIL}\n\n📍 **Location:**\nTenali, Andhra Pradesh\n\n🚨 **Emergency Desk:**\n+91 (08644) 223456 / 108")
    
    st.markdown("---")
    st.markdown("### 🌐 System & Tunnel Status")
    if public_link:
        st.success(f"🟢 **Cloudflare Public Tunnel:**\n[Open Shared Link]({public_link})")
    else:
        st.info("🏠 **Local Mode:** `http://localhost:8501`\n\n*Run `./run.sh` to generate a live public Cloudflare link.*")

    st.markdown("---")
    st.markdown("### 🤖 Cardiac AI Assistant")
    st.success("🟢 **AI Engine: Active**\nClinical knowledge engine ready!")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
        
    st.markdown("---")
    st.caption("🩺 *Medical Disclaimer: AI predictions and reports are assistive screening tools for educational purposes. Consult a cardiologist for clinical diagnosis.*")

# --- Session State Initialization ---
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "inputs" not in st.session_state:
    st.session_state.inputs = {k: dropdown_options[k][0] for k in dropdown_options}
if "result" not in st.session_state:
    st.session_state.result = None
if "probability" not in st.session_state:
    st.session_state.probability = None
if "name" not in st.session_state:
    st.session_state.name = ""
if "contact" not in st.session_state:
    st.session_state.contact = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                f"👋 **Welcome! I am 'Pulse', your Cardiac Health AI Assistant from {chatbot.HOSPITAL_NAME}.**\n\n"
                "I can interpret your prediction numbers, explain diagnostic parameters (ECG, cholesterol, blood pressure), "
                "guide you through personalized diet and exercise plans, or assist with consultation appointments.\n\n"
                "How can I assist your cardiovascular wellness today?"
            )
        }
    ]

# --- Main App Navigation Tabs ---
tab_assessment, tab_report, tab_resources, tab_assistant = st.tabs([
    "🩺 Patient Assessment",
    "📄 Clinical Diagnostic Report",
    "📚 Medical Resources Hub",
    "💬 Cardiac AI Assistant"
])

# =========================================================================
# TAB 1: PATIENT ASSESSMENT & PREDICTION
# =========================================================================
with tab_assessment:
    st.markdown("### 📋 Enter Patient Information & Clinical Biomarkers")
    st.caption("Fill in the patient's vitals and laboratory results below, then click **Predict**.")

    with st.form("input_form", clear_on_submit=False):
        col_name, col_phone = st.columns(2)
        with col_name:
            name_val = st.text_input("Patient Full Name", value=st.session_state.name, placeholder="e.g. John Doe")
        with col_phone:
            contact_val = st.text_input("Contact Phone Number / Email", value=st.session_state.contact, placeholder="e.g. +91 98765 43210")
        
        st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        col_left, col_right = st.columns(2)
        user_input = []
        changed = False

        with col_left:
            for feature in features_left:
                val = st.selectbox(
                    feature, dropdown_options[feature],
                    key=f"left_{feature}",
                    index=dropdown_options[feature].index(st.session_state.inputs.get(feature, dropdown_options[feature][0]))
                )
                if val != st.session_state.inputs.get(feature, dropdown_options[feature][0]):
                    changed = True
                user_input.append((feature, val))

        with col_right:
            for feature in features_right:
                val = st.selectbox(
                    feature, dropdown_options[feature],
                    key=f"right_{feature}",
                    index=dropdown_options[feature].index(st.session_state.inputs.get(feature, dropdown_options[feature][0]))
                )
                if val != st.session_state.inputs.get(feature, dropdown_options[feature][0]):
                    changed = True
                user_input.append((feature, val))

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            predict_btn = st.form_submit_button("🚀 Run Cardiac Prediction", help="Run machine learning diagnostic assessment", use_container_width=True)
        with col_btn2:
            save_btn = st.form_submit_button("💾 Save Patient Record to Excel", help="Save entered details to outputs/patient_details.xlsx", use_container_width=True)

    if changed:
        st.components.v1.html("""
            <script>
            var msg = window.speechSynthesis;
            var utter = new SpeechSynthesisUtterance("Input changed");
            utter.rate = 1.0;
            if (msg.speaking) msg.cancel();
            msg.speak(utter);
            </script>
        """, height=0)

    if predict_btn:
        features_vals = [convert_selection(k, v) for k, v in user_input]
        X_new = np.array(features_vals).reshape(1, -1)
        
        scaler = joblib.load('models/scaler.pkl')
        model = joblib.load('models/rf_heart_model.pkl')
        X_scaled = scaler.transform(X_new)
        
        pred = model.predict(X_scaled)[0]
        
        # Calculate disease probability
        try:
            prob = float(model.predict_proba(X_scaled)[0][1] * 100)
        except Exception:
            prob = 85.0 if pred == 1 else 15.0

        st.session_state.result = int(pred)
        st.session_state.probability = prob
        st.session_state.show_result = True
        st.session_state.inputs = {k: v for k, v in user_input}
        st.session_state.name = name_val
        st.session_state.contact = contact_val

        result_text = "Heart Disease Detected" if pred == 1 else "No Heart Disease Detected"
        st.components.v1.html(f"""
            <script>
            var msg = window.speechSynthesis;
            var utter = new SpeechSynthesisUtterance("{result_text}");
            utter.rate = 0.9;
            if (msg.speaking) msg.cancel();
            msg.speak(utter);
            </script>
        """, height=0)
        st.rerun()

    if save_btn:
        patient_dict = {k: v for k, v in user_input}
        patient_dict["Name"] = name_val
        patient_dict["Contact"] = contact_val
        save_patient_details(patient_dict)
        st.success("✅ Patient details successfully saved to `outputs/patient_details.xlsx`.")
        st.components.v1.html("""
            <script>
            var msg = window.speechSynthesis;
            var utter = new SpeechSynthesisUtterance("Details saved");
            utter.rate = 1.0;
            if (msg.speaking) msg.cancel();
            msg.speak(utter);
            </script>
        """, height=0)

    # Show Results Banner if calculation completed
    if st.session_state.show_result and st.session_state.result is not None:
        st.markdown("---")
        is_pos = (st.session_state.result == 1)
        prob_val = st.session_state.probability if st.session_state.probability is not None else (85.0 if is_pos else 15.0)
        
        banner_bg = "#fef2f2" if is_pos else "#f0fdf4"
        banner_border = "#f87171" if is_pos else "#86efac"
        banner_color = "#dc2626" if is_pos else "#16a34a"
        title_text = "ELEVATED RISK OF HEART DISEASE DETECTED" if is_pos else "NO SIGNIFICANT HEART DISEASE DETECTED"
        icon = "🚨" if is_pos else "✅"

        st.markdown(f"""
        <div style="background-color: {banner_bg}; border: 2px solid {banner_border}; border-radius: 12px; padding: 25px; text-align: center; margin: 20px 0;">
            <h2 style="color: {banner_color}; margin: 0 0 10px 0;">{icon} {title_text}</h2>
            <p style="font-size: 1.15rem; color: #334155; margin-bottom: 12px;">
                Calculated Cardiovascular Disease Probability: <b style="color: {banner_color}; font-size: 1.3rem;">{prob_val:.1f}%</b>
            </p>
            <p style="color: #64748b; margin: 0;">
                <b>Patient:</b> {st.session_state.name if st.session_state.name else 'Walk-in Patient'} &bull;
                <b>Contact:</b> {st.session_state.contact if st.session_state.contact else 'N/A'}
            </p>
            <div style="margin-top: 15px;">
                <span style="background-color: {banner_color}; color: white; padding: 6px 16px; border-radius: 9999px; font-weight: 700; font-size: 0.9rem;">
                    {'HIGH RISK' if prob_val>=70 else ('MODERATE RISK' if prob_val>=40 else 'LOW RISK')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.info("💡 **Clinical Report Ready:** Switch to the **'📄 Clinical Diagnostic Report'** tab to preview or download the official printable PDF report!")

        # Dynamic Project Info Table
        feature_names = list(dropdown_options.keys())
        user_inputs_str = [st.session_state.inputs.get(f, "") for f in feature_names]
        table_data = []
        for attr, val_str in zip(feature_names, user_inputs_str):
            eval_res = report_generator.evaluate_parameter_status(attr, str(val_str))
            table_data.append({
                "Biomarker": attr,
                "Patient Value": val_str,
                "Normal Reference": eval_res["reference"],
                "Risk Classification": eval_res["badge"]
            })
        df_table = pd.DataFrame(table_data)

        st.markdown("#### 🔬 Entered Biomarkers & Clinical Classification")
        st.dataframe(df_table, use_container_width=True)

    # Feature Importance Chart
    st.markdown("---")
    st.markdown("### 📊 Clinical Feature Importance (Random Forest Impact)")
    st.caption("Shows which physiological parameters contribute most heavily to the machine learning diagnosis.")
    
    try:
        model = joblib.load('models/rf_heart_model.pkl')
        features = list(dropdown_options.keys())
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]

        fig, ax = plt.subplots(figsize=(8, 4.5))
        bar_colors = plt.cm.RdPu(np.linspace(0.4, 0.95, len(indices)))
        ax.barh([features[i] for i in indices], importances[indices], color=bar_colors, edgecolor='#7d2131', height=0.6)
        ax.set_xlabel('Relative Model Contribution (Feature Weight)', fontsize=10, color='#7d2131', fontweight='bold')
        ax.set_title('Cardiovascular Risk Predictor Importance', fontsize=12, color='#c02433', fontweight='bold', pad=12)
        ax.invert_yaxis()
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Feature chart loading notice: {e}")

# =========================================================================
# TAB 2: CLINICAL DIAGNOSTIC REPORT GENERATION
# =========================================================================
with tab_report:
    st.markdown("### 📄 Official Cardiovascular Clinical Assessment Report")
    st.caption("Comprehensive medical report with patient vitals, diagnostic risk stratification, personalized lifestyle protocols, and physician signature block.")

    if not st.session_state.show_result or st.session_state.result is None:
        st.warning("⚠️ No prediction has been performed yet. Please enter patient vitals in the **'Patient Assessment'** tab and click **Predict** first.")
    else:
        # Generate PDF and HTML reports
        report_html = report_generator.generate_html_report(
            name=st.session_state.name,
            contact=st.session_state.contact,
            inputs=st.session_state.inputs,
            prediction=st.session_state.result,
            probability=st.session_state.probability
        )
        
        pdf_bytes = report_generator.generate_pdf_report(
            name=st.session_state.name,
            contact=st.session_state.contact,
            inputs=st.session_state.inputs,
            prediction=st.session_state.result,
            probability=st.session_state.probability
        )

        col_dl1, col_dl2 = st.columns([1, 1])
        patient_slug = (st.session_state.name.strip().replace(" ", "_")) if st.session_state.name else "Patient"
        pdf_filename = f"Cardiac_Assessment_Report_{patient_slug}.pdf"
        html_filename = f"Cardiac_Assessment_Report_{patient_slug}.html"

        with col_dl1:
            st.download_button(
                label="📥 Download Official Clinical Report (PDF)",
                data=pdf_bytes,
                file_name=pdf_filename,
                mime="application/pdf",
                use_container_width=True
            )
        with col_dl2:
            st.download_button(
                label="🌐 Download Standalone HTML Medical Report",
                data=report_html,
                file_name=html_filename,
                mime="text/html",
                use_container_width=True
            )

        st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
        st.markdown("#### 👁️ Interactive In-App Clinical Report Viewer")
        st.components.v1.html(report_html, height=800, scrolling=True)

# =========================================================================
# TAB 3: MEDICAL RESOURCES HUB
# =========================================================================
with tab_resources:
    st.markdown("### 📚 Comprehensive Heart Health & Medical Resources Hub")
    st.caption("Evidence-based cardiology guidelines, dietary protocols, fitness safety limits, diagnostic decoders, and emergency response actions.")

    resources = report_generator.get_heart_health_resources()

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("#### 🥗 Nutritional & Dietary Protocols")
        for item in resources["nutrition"]:
            with st.expander(f"🥗 {item['title']} — {item['badge']}", expanded=True):
                st.write(item["summary"])
                for pt in item["details"]:
                    st.markdown(f"- {pt}")

        st.markdown("#### 🏃 Cardiovascular Fitness & Exercise Guidelines")
        for item in resources["exercise"]:
            with st.expander(f"🏃 {item['title']} — {item['badge']}", expanded=False):
                st.write(item["summary"])
                for pt in item["details"]:
                    st.markdown(f"- {pt}")

    with col_r2:
        st.markdown("#### 🔬 Clinical Diagnostic Biomarker Decoder")
        for item in resources["diagnostics"]:
            with st.expander(f"🩺 {item['param']} ({item['range']})", expanded=False):
                st.write(item["meaning"])

        st.markdown("#### 🚨 Emergency Cardiac Protocol")
        with st.expander("🚨 Recognizing a Heart Attack & Immediate Steps", expanded=True):
            st.error(f"📞 **EMERGENCY HOTLINE:** {resources['emergency']['hotline']}")
            st.markdown("**Warning Signs:**")
            for s in resources['emergency']['signs']:
                st.markdown(f"- {s}")
            st.markdown("**5-Step Action Checklist:**")
            for a in resources['emergency']['action_steps']:
                st.markdown(f"**{a}**")

        st.markdown("#### 🏥 Health Hospitals Tenali Cardiology Services")
        with st.expander("🏥 Hospital Facilities & Diagnostics", expanded=False):
            st.markdown(f"**Facility:** {resources['hospital']['name']}\n\n**Department:** {resources['hospital']['dept']}")
            st.markdown(f"**Location:** {resources['hospital']['address']}\n\n**Email:** `{resources['hospital']['email']}`")
            st.markdown("**Specialized Services Available:**")
            for s in resources['hospital']['services']:
                st.markdown(f"- {s}")

# =========================================================================
# TAB 4: CARDIAC AI ASSISTANT ('PULSE')
# =========================================================================
with tab_assistant:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 15px;'>
        <h3 style='color: #c02433; margin-bottom: 4px;'>💬 Cardiac Health AI Assistant ('Pulse')</h3>
        <p style='color: #64748b;'>Ask questions about your risk factors, diet plans, report interpretation, or appointments at Health Hospitals Tenali</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Question Prompts
    st.markdown("##### 💡 Suggested Questions:")
    cq1, cq2, cq3, cq4 = st.columns(4)
    quick_prompt = None
    with cq1:
        if st.button("📋 Explain My Prediction", use_container_width=True, key="btn_explain"):
            quick_prompt = "Explain my test results"
    with cq2:
        if st.button("🥗 Lower BP & Cholesterol", use_container_width=True, key="btn_bp"):
            quick_prompt = "How can I lower blood pressure and cholesterol?"
    with cq3:
        if st.button("📄 How to Get My Report", use_container_width=True, key="btn_report"):
            quick_prompt = "How do I download my clinical report?"
    with cq4:
        if st.button("🏥 Book Doctor in Tenali", use_container_width=True, key="btn_tenali"):
            quick_prompt = "How do I book an appointment at Health Hospitals Tenali?"

    # Chat Display
    chat_box = st.container()
    with chat_box:
        for msg in st.session_state.chat_history:
            avatar = "🩺" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # Chat Input
    user_query = st.chat_input("Ask about your cardiovascular health, clinical numbers, diet, or reports...")
    chosen_prompt = quick_prompt or user_query

    if chosen_prompt:
        st.session_state.chat_history.append({"role": "user", "content": chosen_prompt})
        with st.spinner("Analyzing with Cardiac AI Assistant..."):
            reply = chatbot.get_assistant_reply(chosen_prompt, st.session_state, api_key=gemini_key)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.rerun()

# --- Footer Section ---
st.markdown("<hr style='margin-top: 40px; border: none; border-top: 1px dashed #cbd5e1;'>", unsafe_allow_html=True)
st.markdown("""
<div class="caption-custom">
  <b>HEALTH HOSPITALS TENALI &bull; CENTRE FOR EXCELLENCE IN CARDIOLOGY</b><br>
  Official Predictive Clinical Screening & Automated Report Generation System &bull; &copy; 2026<br>
  For clinical emergencies, dial <b>108</b> or visit our Emergency Cardiac Unit in Tenali.
</div>
""", unsafe_allow_html=True)
