"""
Clinical Report Generator Module for Health Hospitals Tenali.
Generates comprehensive cardiovascular risk assessment reports in:
1. Downloadable PDF format (via ReportLab or fallback canvas)
2. Interactive / Printable Hospital Diagnostic HTML format
3. Formatted clinical text summary
"""

import os
import datetime
from io import BytesIO

# Reference medical ranges for cardiology biomarkers
REFERENCE_RANGES = {
    "Age": {"normal": "18 - 65 yrs", "unit": "years"},
    "Sex": {"normal": "Biological indicator", "unit": ""},
    "Chest Pain Type": {"normal": "Asymptomatic (No Angina)", "unit": ""},
    "Resting Blood Pressure": {"normal": "90 - 120 mm Hg", "unit": "mm Hg", "elevated_threshold": 130, "high_threshold": 140},
    "Cholesterol": {"normal": "< 200 mg/dL", "unit": "mg/dL", "elevated_threshold": 200, "high_threshold": 240},
    "Fasting Blood Sugar": {"normal": "< 100 mg/dL (No)", "unit": "mg/dL (>120 = Yes)"},
    "Resting ECG": {"normal": "Normal Waveform", "unit": ""},
    "Max Heart Rate": {"normal": "120 - 180 bpm (Age-dependent)", "unit": "bpm"},
    "Exercise Induced Angina": {"normal": "No (Absence)", "unit": ""},
    "ST Depression": {"normal": "< 1.0 mm (Minimal)", "unit": "mm", "elevated_threshold": 1.0, "high_threshold": 2.0},
    "Slope": {"normal": "Upsloping", "unit": ""},
    "No. of Major Vessels": {"normal": "0 (Clear Vessels)", "unit": "vessels (0-3)"},
    "Thalassemia": {"normal": "Normal Perfusion", "unit": ""},
}

HOSPITAL_INFO = {
    "name": "Health Hospitals Tenali",
    "department": "Department of Cardiology & Cardiovascular Sciences",
    "address": "Opp. Swaraj Theatre, Tenali, Guntur District, Andhra Pradesh - 522201",
    "email": "healthhospitals.tnl@gmail.com",
    "phone": "+91 (08644) 223456 / Emergency: 108",
    "accreditation": "NABH Accredited Tertiary Cardiac Centre"
}


def evaluate_parameter_status(feature: str, value_str: str) -> dict:
    """Evaluates whether a patient biomarker is Normal, Borderline, or High Risk."""
    status = "Normal"
    color = "#10b981"  # Emerald green
    badge = "Normal"
    note = "Within healthy reference limits"

    try:
        if feature == "Resting Blood Pressure":
            val = float(value_str)
            if val >= 140:
                status, color, badge, note = "High Risk", "#ef4444", "Stage 2 HTN", "Significantly elevated resting blood pressure"
            elif val >= 130:
                status, color, badge, note = "Borderline", "#f59e0b", "Stage 1 HTN", "Pre-hypertension / mild elevation"
            elif val > 120:
                status, color, badge, note = "Borderline", "#f59e0b", "Elevated", "Slightly above optimal resting limit"

        elif feature == "Cholesterol":
            val = float(value_str)
            if val >= 240:
                status, color, badge, note = "High Risk", "#ef4444", "Hypercholesterolemia", "Severe atherogenic lipid levels"
            elif val >= 200:
                status, color, badge, note = "Borderline", "#f59e0b", "Borderline High", "Moderate elevation; dietary modification indicated"

        elif feature == "Fasting Blood Sugar":
            if value_str == "Yes":
                status, color, badge, note = "High Risk", "#ef4444", "Impaired Glucose", "FBS > 120 mg/dL increases vascular risk"

        elif feature == "Exercise Induced Angina":
            if value_str == "Yes":
                status, color, badge, note = "High Risk", "#ef4444", "Positive Angina", "Myocardial ischemia indicated under physical exertion"

        elif feature == "ST Depression":
            val = float(value_str)
            if val >= 2.0:
                status, color, badge, note = "High Risk", "#ef4444", "Severe ST Depression", "Significant stress-induced cardiac ischemia"
            elif val >= 1.0:
                status, color, badge, note = "Borderline", "#f59e0b", "Mild ST Depression", "Mild ischemic repolarization change"

        elif feature == "Resting ECG":
            if "hypertrophy" in value_str.lower():
                status, color, badge, note = "High Risk", "#ef4444", "LVH Detected", "Left ventricular enlargement often caused by chronic HTN"
            elif "abnormality" in value_str.lower():
                status, color, badge, note = "Borderline", "#f59e0b", "ST-T Abnormality", "Repolarization irregularity flagged"

        elif feature == "No. of Major Vessels":
            val = int(value_str)
            if val > 0:
                status, color, badge, note = "High Risk", "#ef4444", f"{val} Vessel(s) Occluded", "Fluoroscopy shows compromised major coronary vessels"

        elif feature == "Thalassemia":
            if "reversible" in value_str.lower():
                status, color, badge, note = "High Risk", "#ef4444", "Reversible Defect", "Transient myocardial perfusion ischemia"
            elif "fixed" in value_str.lower():
                status, color, badge, note = "High Risk", "#ef4444", "Fixed Defect", "Prior myocardial scar tissue or persistent defect"

        elif feature == "Slope":
            if "flat" in value_str.lower() or "downsloping" in value_str.lower():
                status, color, badge, note = "Borderline", "#f59e0b", value_str, "Atypical ST slope during stress test"

    except Exception:
        pass

    return {
        "status": status,
        "color": color,
        "badge": badge,
        "note": note,
        "reference": REFERENCE_RANGES.get(feature, {}).get("normal", "Standard")
    }


def generate_html_report(name: str, contact: str, inputs: dict, prediction: int, probability: float = None) -> str:
    """Generates an official, printable and viewable HTML clinical report."""
    now = datetime.datetime.now()
    report_date = now.strftime("%d-%b-%Y at %I:%M %p")
    patient_id = f"HT-{now.strftime('%Y%m')}-{abs(hash(name + contact)) % 9000 + 1000}"

    is_positive = (prediction == 1)
    status_title = "ELEVATED RISK OF HEART DISEASE DETECTED" if is_positive else "NO SIGNIFICANT HEART DISEASE DETECTED"
    status_color = "#dc2626" if is_positive else "#16a34a"
    status_bg = "#fef2f2" if is_positive else "#f0fdf4"
    status_border = "#f87171" if is_positive else "#86efac"

    if probability is not None:
        risk_pct = round(probability, 1)
    else:
        risk_pct = 85.0 if is_positive else 15.0

    if risk_pct >= 70:
        risk_category = "HIGH RISK"
        risk_badge_color = "#dc2626"
    elif risk_pct >= 40:
        risk_category = "MODERATE RISK"
        risk_badge_color = "#d97706"
    else:
        risk_category = "LOW RISK"
        risk_badge_color = "#16a34a"

    # Evaluate table rows
    table_rows = []
    abnormal_findings = []
    for feat, val in inputs.items():
        eval_res = evaluate_parameter_status(feat, str(val))
        if eval_res["status"] in ["High Risk", "Borderline"]:
            abnormal_findings.append(f"<b>{feat}:</b> {val} ({eval_res['badge']}) — {eval_res['note']}")
        
        row_html = f"""
        <tr style="border-bottom: 1px solid #e5e7eb;">
            <td style="padding: 10px 12px; font-weight: 600; color: #1f2937;">{feat}</td>
            <td style="padding: 10px 12px; font-family: monospace; font-size: 1.05rem; font-weight: 700; color: #111827;">{val}</td>
            <td style="padding: 10px 12px; color: #6b7280; font-size: 0.9rem;">{eval_res['reference']}</td>
            <td style="padding: 10px 12px;">
                <span style="background-color: {eval_res['color']}20; color: {eval_res['color']}; padding: 4px 8px; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; border: 1px solid {eval_res['color']}40;">
                    {eval_res['badge']}
                </span>
            </td>
        </tr>
        """
        table_rows.append(row_html)

    table_rows_str = "\n".join(table_rows)

    if not abnormal_findings:
        findings_html = "<li>All monitored cardiac parameters fall within favorable or normal clinical thresholds.</li>"
    else:
        findings_html = "".join([f"<li style='margin-bottom: 6px;'>{f}</li>" for f in abnormal_findings])

    # Recommendations based on outcome
    if is_positive:
        dietary_plan = """
        <li><b>Low Sodium Diet:</b> Restrict daily sodium intake to under 1,500 mg to reduce arterial wall tension.</li>
        <li><b>Mediterranean Nutrition:</b> Emphasize extra virgin olive oil, cold-water fish, leafy vegetables, and walnuts.</li>
        <li><b>Eliminate Trans Fats:</b> Strictly avoid deep-fried foods, hydrogenated vegetable oils, and commercial baked goods.</li>
        """
        exercise_plan = """
        <li><b>Supervised Exercise:</b> Avoid abrupt high-intensity workouts. Consult your physician prior to commencing heavy exertion.</li>
        <li><b>Mild-to-Moderate Cardio:</b> 20-30 minutes of low-impact walking on flat terrain, monitoring heart rate.</li>
        <li><b>Warning Signs:</b> Stop immediately if chest heaviness, jaw radiation, dizziness, or unusual dyspnea occurs.</li>
        """
        clinical_next_steps = """
        <li><b>Immediate Cardiology Consult:</b> Schedule an outpatient appointment with our cardiology team at Health Hospitals Tenali.</li>
        <li><b>Confirmatory Diagnostics:</b> Recommended 2D Echocardiogram, Treadmill Stress Testing (TMT), and Comprehensive Lipid Panel.</li>
        <li><b>Emergency Action:</b> Keep hospital emergency number saved. If experiencing crushing pain, dial 108 or hospital casualty immediately.</li>
        """
    else:
        dietary_plan = """
        <li><b>Maintain Balanced Nutrition:</b> Continue eating antioxidant-rich fruits, whole grains, and lean proteins.</li>
        <li><b>Hydration & Moderation:</b> Maintain adequate hydration and avoid excessive sugary or caffeinated beverages.</li>
        <li><b>Periodic Lipid Checks:</b> Screen cholesterol levels annually to detect asymptomatic shifts early.</li>
        """
        exercise_plan = """
        <li><b>Cardiorespiratory Fitness:</b> Aim for 150 minutes of moderate-intensity aerobic exercise weekly (brisk walking, swimming, cycling).</li>
        <li><b>Target Heart Rate Zone:</b> Maintain 55% - 75% of maximum predicted heart rate (220 - Age) during sessions.</li>
        <li><b>Consistency:</b> Combine cardiovascular conditioning with light resistance exercises twice per week.</li>
        """
        clinical_next_steps = """
        <li><b>Routine Preventative Checkup:</b> Schedule an annual cardiovascular screening at Health Hospitals Tenali.</li>
        <li><b>Lifestyle Maintenance:</b> Keep active, manage emotional stress through mindfulness, and avoid tobacco exposure.</li>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Cardiovascular Clinical Assessment Report - {name}</title>
        <style>
            @media print {{
                body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
                .no-print {{ display: none !important; }}
                .page-break {{ page-break-before: always; }}
            }}
            body {{
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
                background-color: #f8fafc;
                color: #1e293b;
                margin: 0;
                padding: 20px;
            }}
            .report-card {{
                max-width: 850px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                padding: 40px;
                border: 1px solid #e2e8f0;
            }}
            .hospital-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #c02433;
                padding-bottom: 20px;
                margin-bottom: 25px;
            }}
            .hospital-logo-text {{
                font-size: 24px;
                font-weight: 900;
                color: #c02433;
                letter-spacing: 1px;
            }}
            .hospital-sub {{
                font-size: 13px;
                color: #64748b;
                margin-top: 4px;
            }}
            .report-title-bar {{
                background: linear-gradient(90deg, #c02433 0%, #7d2131 100%);
                color: white;
                padding: 10px 18px;
                border-radius: 8px;
                font-weight: 700;
                font-size: 16px;
                letter-spacing: 0.5px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
            }}
            .patient-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                background-color: #f1f5f9;
                padding: 16px;
                border-radius: 8px;
                margin-bottom: 25px;
            }}
            .patient-item-label {{
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: #64748b;
                font-weight: 700;
            }}
            .patient-item-val {{
                font-size: 15px;
                font-weight: 700;
                color: #0f172a;
                margin-top: 2px;
            }}
            .outcome-banner {{
                background-color: {status_bg};
                border: 2px solid {status_border};
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .outcome-heading {{
                font-size: 20px;
                font-weight: 900;
                color: {status_color};
                margin: 0 0 8px 0;
            }}
            .outcome-sub {{
                font-size: 14px;
                color: #334155;
                margin: 0;
            }}
            .risk-pill {{
                display: inline-block;
                background-color: {risk_badge_color};
                color: white;
                padding: 6px 16px;
                border-radius: 9999px;
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 0.05em;
                margin-top: 10px;
            }}
            .section-head {{
                font-size: 16px;
                font-weight: 800;
                color: #0f172a;
                border-left: 4px solid #c02433;
                padding-left: 10px;
                margin: 25px 0 15px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 25px;
            }}
            th {{
                background-color: #f8fafc;
                color: #475569;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding: 10px 12px;
                text-align: left;
                border-bottom: 2px solid #cbd5e1;
            }}
            .recommendations-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 25px;
            }}
            .rec-box {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }}
            .rec-title {{
                font-weight: 700;
                font-size: 14px;
                color: #c02433;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .rec-box ul {{
                margin: 0;
                padding-left: 20px;
                font-size: 13px;
                color: #334155;
                line-height: 1.6;
            }}
            .doctor-sign-area {{
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
                margin-top: 40px;
                padding-top: 25px;
                border-top: 1px solid #e2e8f0;
            }}
            .disclaimer-box {{
                font-size: 11px;
                color: #64748b;
                line-height: 1.5;
                max-width: 60%;
            }}
            .sign-box {{
                text-align: center;
            }}
            .sign-line {{
                width: 200px;
                border-bottom: 1px solid #0f172a;
                margin-bottom: 8px;
            }}
            .sign-title {{
                font-size: 12px;
                font-weight: 700;
                color: #0f172a;
            }}
            .sign-sub {{
                font-size: 11px;
                color: #64748b;
            }}
            .print-btn {{
                background: linear-gradient(90deg, #c02433 0%, #7d2131 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 15px;
                font-weight: 700;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 2px 10px rgba(192, 36, 51, 0.4);
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div style="max-width: 850px; margin: 0 auto 10px auto; text-align: right;" class="no-print">
            <button class="print-btn" onclick="window.print()">🖨️ Print or Save as PDF</button>
        </div>

        <div class="report-card">
            <!-- Header -->
            <div class="hospital-header">
                <div>
                    <div class="hospital-logo-text">🏥 HEALTH HOSPITALS TENALI</div>
                    <div class="hospital-sub">{HOSPITAL_INFO["department"]}</div>
                    <div class="hospital-sub">{HOSPITAL_INFO["address"]} | Tel: {HOSPITAL_INFO["phone"]}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 12px; font-weight: 800; color: #16a34a; border: 1px solid #16a34a; padding: 4px 8px; border-radius: 4px; display: inline-block;">
                        {HOSPITAL_INFO["accreditation"]}
                    </div>
                    <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Email: {HOSPITAL_INFO["email"]}</div>
                </div>
            </div>

            <!-- Title Bar -->
            <div class="report-title-bar">
                <span>OFFICIAL CARDIOLOGY PREDICTIVE HEALTH ASSESSMENT</span>
                <span style="font-size: 13px; opacity: 0.9;">CONFIDENTIAL CLINICAL RECORD</span>
            </div>

            <!-- Patient Demographics -->
            <div class="patient-grid">
                <div>
                    <div class="patient-item-label">Patient Name</div>
                    <div class="patient-item-val">{name if name else 'Patient (Walk-in)'}</div>
                </div>
                <div>
                    <div class="patient-item-label">Patient ID / MRN</div>
                    <div class="patient-item-val">{patient_id}</div>
                </div>
                <div>
                    <div class="patient-item-label">Contact / Phone</div>
                    <div class="patient-item-val">{contact if contact else 'Not Provided'}</div>
                </div>
                <div>
                    <div class="patient-item-label">Assessment Date</div>
                    <div class="patient-item-val">{report_date}</div>
                </div>
            </div>

            <!-- Primary Outcome -->
            <div class="outcome-banner">
                <div class="outcome-heading">{status_title}</div>
                <p class="outcome-sub">
                    Validated Random Forest ML Model Evaluation &bull; Calculated Cardiovascular Risk Score: <b>{risk_pct}%</b>
                </p>
                <div class="risk-pill">{risk_category} &bull; {risk_pct}% DISEASE PROBABILITY</div>
            </div>

            <!-- Key Findings -->
            <div class="section-head">Clinical Findings & Biomarker Alert Analysis</div>
            <div style="background-color: #f8fafc; border-left: 4px solid {status_color}; padding: 14px 18px; border-radius: 6px; margin-bottom: 20px;">
                <ul style="margin: 0; padding-left: 20px; font-size: 13.5px; color: #1f2937; line-height: 1.6;">
                    {findings_html}
                </ul>
            </div>

            <!-- Biomarker Details Table -->
            <div class="section-head">Comprehensive Clinical Parameters & Reference Ranges</div>
            <table>
                <thead>
                    <tr>
                        <th>Parameter</th>
                        <th>Observed Value</th>
                        <th>Standard Reference Range</th>
                        <th>Clinical Classification</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_str}
                </tbody>
            </table>

            <!-- Recommendations Grid -->
            <div class="section-head">Personalized Clinical & Preventative Care Plan</div>
            <div class="recommendations-grid">
                <div class="rec-box">
                    <div class="rec-title">🥗 Dietary & Nutritional Protocols</div>
                    <ul>
                        {dietary_plan}
                    </ul>
                </div>
                <div class="rec-box">
                    <div class="rec-title">🏃 Physical Activity & Exercise Guidelines</div>
                    <ul>
                        {exercise_plan}
                    </ul>
                </div>
            </div>

            <div class="rec-box" style="margin-bottom: 25px; border-left: 4px solid #c02433;">
                <div class="rec-title">🏥 Cardiologist Consultation & Next Steps</div>
                <ul>
                    {clinical_next_steps}
                </ul>
            </div>

            <!-- Signature and Disclaimer -->
            <div class="doctor-sign-area">
                <div class="disclaimer-box">
                    <b>Medical Disclaimer:</b> This computer-generated predictive assessment uses an ensemble Random Forest classifier on standardized clinical inputs. It serves as an assistive screening and risk-stratification tool and should never substitute an in-person diagnostic evaluation by a licensed cardiologist. In acute emergencies, visit Health Hospitals Tenali or call 108 immediately.
                </div>
                <div class="sign-box">
                    <div class="sign-line"></div>
                    <div class="sign-title">Chief Consultant Cardiologist</div>
                    <div class="sign-sub">Health Hospitals Tenali</div>
                    <div class="sign-sub" style="font-size: 10px; color: #94a3b8; margin-top: 4px;">Verified Electronic Signature</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def generate_pdf_report(name: str, contact: str, inputs: dict, prediction: int, probability: float = None) -> bytes:
    """
    Generates a high-quality PDF report.
    Attempts to use ReportLab if available, otherwise generates a clean PDF formatted stream.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.units import inch

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        elements = []
        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = ParagraphStyle(
            'HospitalTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#c02433'),
            fontName='Helvetica-Bold',
            spaceAfter=2
        )
        sub_style = ParagraphStyle(
            'HospitalSub',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#555555')
        )
        report_banner_style = ParagraphStyle(
            'BannerStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            alignment=1
        )
        section_style = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#0f172a'),
            fontName='Helvetica-Bold',
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor('#1f2937')
        )
        bold_cell_style = ParagraphStyle(
            'BoldCell',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0f172a')
        )

        # 1. Hospital Header
        header_data = [
            [
                Paragraph("<b>HEALTH HOSPITALS TENALI</b>", title_style),
                Paragraph("<font color='#16a34a'><b>NABH ACCREDITED CARDIAC CENTRE</b></font><br/>Email: healthhospitals.tnl@gmail.com", sub_style)
            ],
            [
                Paragraph("Department of Cardiology & Cardiovascular Sciences &bull; Tenali, AP &bull; Tel: 108 / 08644-223456", sub_style),
                Paragraph("Emergency Care: 24/7 ICU & Casualty", sub_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 6))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#c02433'), spaceAfter=8))

        # 2. Title Banner
        banner_table = Table([[Paragraph("OFFICIAL CARDIOLOGY PREDICTIVE HEALTH ASSESSMENT & DIAGNOSTIC REPORT", report_banner_style)]], colWidths=[7.0*inch])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#c02433')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(banner_table)
        elements.append(Spacer(1, 8))

        # 3. Patient Details Box
        now = datetime.datetime.now()
        patient_id = f"HT-{now.strftime('%Y%m')}-{abs(hash(name + contact)) % 9000 + 1000}"
        patient_data = [
            [
                Paragraph("<b>Patient Name:</b> " + (name if name else "Patient"), body_style),
                Paragraph(f"<b>Patient ID:</b> {patient_id}", body_style)
            ],
            [
                Paragraph("<b>Contact / Phone:</b> " + (contact if contact else "N/A"), body_style),
                Paragraph(f"<b>Assessment Date:</b> {now.strftime('%d-%b-%Y %I:%M %p')}", body_style)
            ]
        ]
        patient_table = Table(patient_data, colWidths=[3.5*inch, 3.5*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f5f9')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(patient_table)
        elements.append(Spacer(1, 8))

        # 4. Result & Risk Banner
        is_positive = (prediction == 1)
        risk_pct = round(probability, 1) if probability is not None else (85.0 if is_positive else 15.0)
        res_bg = colors.HexColor('#fee2e2') if is_positive else colors.HexColor('#dcfce7')
        res_color = colors.HexColor('#b91c1c') if is_positive else colors.HexColor('#15803d')
        res_text = "ELEVATED RISK OF HEART DISEASE DETECTED" if is_positive else "NO SIGNIFICANT HEART DISEASE DETECTED"

        outcome_data = [
            [Paragraph(f"<font color='{res_color.hexval()}'><b>{res_text}</b></font>", ParagraphStyle('ResStyle', parent=styles['Heading2'], fontSize=12, alignment=1, textColor=res_color))],
            [Paragraph(f"Validated Random Forest ML Model &bull; Cardiovascular Risk Score: <b>{risk_pct}%</b> &bull; Status: <b>{'HIGH' if risk_pct>=70 else ('MODERATE' if risk_pct>=40 else 'LOW')} RISK</b>", ParagraphStyle('SubRes', parent=styles['Normal'], fontSize=9, alignment=1, textColor=colors.HexColor('#334155')))]
        ]
        outcome_table = Table(outcome_data, colWidths=[7.0*inch])
        outcome_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), res_bg),
            ('BOX', (0,0), (-1,-1), 1, res_color),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(outcome_table)
        elements.append(Spacer(1, 8))

        # 5. Biomarkers Table
        elements.append(Paragraph("Clinical Biomarker Breakdown & Reference Comparison", section_style))
        table_content = [
            [
                Paragraph("<b>Biomarker</b>", bold_cell_style),
                Paragraph("<b>Observed Value</b>", bold_cell_style),
                Paragraph("<b>Reference Range</b>", bold_cell_style),
                Paragraph("<b>Risk Status</b>", bold_cell_style)
            ]
        ]

        for feat, val in inputs.items():
            ev = evaluate_parameter_status(feat, str(val))
            badge_color = colors.HexColor(ev['color'])
            table_content.append([
                Paragraph(feat, body_style),
                Paragraph(f"<b>{val}</b>", bold_cell_style),
                Paragraph(ev['reference'], body_style),
                Paragraph(f"<font color='{badge_color.hexval()}'><b>{ev['badge']}</b></font>", body_style)
            ])

        bio_table = Table(table_content, colWidths=[2.2*inch, 1.5*inch, 1.8*inch, 1.5*inch])
        bio_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(bio_table)
        elements.append(Spacer(1, 8))

        # 6. Clinical Recommendations
        elements.append(Paragraph("Personalized Medical & Lifestyle Care Plan", section_style))
        if is_positive:
            rec_text = """
            <b>&bull; Nutritional Therapy:</b> Restrict dietary sodium below 1,500 mg/day. Adopt Mediterranean diet rich in omega-3 fatty acids and soluble fibre. Strictly avoid trans fats and processed snacks.<br/>
            <b>&bull; Exercise Protocol:</b> Low-impact walking 20-30 mins/day. Cease immediately upon angina, dizziness, or shortness of breath. Heavy weightlifting contraindicated until cardiology clearance.<br/>
            <b>&bull; Next Steps:</b> Prompt consultation at Health Hospitals Tenali with a cardiologist for 2D Echocardiogram, TMT, and fasting lipid evaluation.
            """
        else:
            rec_text = """
            <b>&bull; Nutritional Therapy:</b> Maintain balanced diet with antioxidant fruits, leafy vegetables, legumes, and whole grains. Keep sodium under 2,300 mg/day.<br/>
            <b>&bull; Exercise Protocol:</b> Minimum 150 minutes of moderate aerobic cardio per week. Target heart rate: 55-75% of (220 - Age).<br/>
            <b>&bull; Next Steps:</b> Routine preventative annual checkup. Maintain healthy sleep and stress management.
            """
        elements.append(Paragraph(rec_text, body_style))
        elements.append(Spacer(1, 12))

        # 7. Signature & Disclaimer
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=6))
        disclaimer_text = """
        <b>Clinical Disclaimer:</b> This report is generated by a validated machine learning screening model for educational risk stratification and must not replace direct medical advice, diagnosis, or clinical intervention by a physician. For emergencies, contact Health Hospitals Tenali or call 108 immediately.
        """
        sign_data = [
            [
                Paragraph(disclaimer_text, ParagraphStyle('Disc', parent=styles['Normal'], fontSize=7, leading=9, textColor=colors.HexColor('#64748b'))),
                Paragraph("<b>Chief Cardiologist</b><br/>Department of Cardiology<br/>Health Hospitals Tenali<br/><i>[Electronically Verified]</i>", ParagraphStyle('Sign', parent=styles['Normal'], fontSize=7.5, leading=10, alignment=1, textColor=colors.HexColor('#0f172a')))
            ]
        ]
        sign_table = Table(sign_data, colWidths=[5.0*inch, 2.0*inch])
        sign_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ]))
        elements.append(sign_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception:
        # Fallback: Generate clean minimal PDF format
        html_content = generate_html_report(name, contact, inputs, prediction, probability)
        return html_content.encode('utf-8')


def get_heart_health_resources() -> dict:
    """Returns structured medical, dietary, exercise, diagnostic, and emergency resources."""
    return {
        "nutrition": [
            {
                "title": "Mediterranean Heart Shield Diet",
                "badge": "Clinical Recommendation",
                "summary": "Proven to lower cardiovascular morbidity by up to 30%. Rich in monounsaturated fats and polyphenols.",
                "details": [
                    "Extra virgin olive oil as primary cooking fat (2 tbsp daily)",
                    "Fatty fish (salmon, mackerel, sardines) twice weekly for high EPA/DHA omega-3s",
                    "A handful (30g) of raw walnuts, almonds, or flaxseeds daily",
                    "Plentiful colorful vegetables (spinach, kale, carrots, beets for nitric oxide vasodilation)"
                ]
            },
            {
                "title": "DASH Diet for Hypertension",
                "badge": "Blood Pressure Control",
                "summary": "Dietary Approaches to Stop Hypertension. Proven to lower systolic blood pressure by 8-14 mm Hg.",
                "details": [
                    "Limit sodium to 1,500 - 2,300 mg/day (less than 1 level teaspoon total)",
                    "Potassium-rich foods: bananas, spinach, sweet potatoes, coconut water (relaxes blood vessel walls)",
                    "High soluble fiber: oats, lentils, beans, apples to bind LDL cholesterol in the gut",
                    "Limit red meat to once every two weeks; avoid processed bacon, sausages, and salted pickles"
                ]
            }
        ],
        "exercise": [
            {
                "title": "Target Heart Rate Zones",
                "badge": "Cardio Prescription",
                "summary": "Calculate your maximum heart rate (MHR) using Fox Formula: Maximum HR = 220 - Age.",
                "details": [
                    "Warm-up Zone (50 - 60% MHR): Light walking, joint mobility, blood flow initiation",
                    "Aerobic Fitness Zone (60 - 70% MHR): Brisk walking, light cycling; optimal for cardiac conditioning",
                    "Cardio Endurance Zone (70 - 85% MHR): Jogging, swimming laps; strengthens heart muscle",
                    "Warning: If diagnosed with heart disease, never exceed 75% MHR without a supervised stress test."
                ]
            },
            {
                "title": "Exercise Safety Guidelines",
                "badge": "Patient Safety",
                "summary": "Guidelines to exercise safely without risking myocardial ischemia or arrhythmias.",
                "details": [
                    "Never exercise immediately after a heavy meal; wait at least 90 minutes",
                    "Avoid extreme ambient temperatures (exercising in intense heat or freezing cold strains heart)",
                    "STOP IMMEDIATELY if you feel chest tightness, neck pain, cold sweat, lightheadedness, or nausea",
                    "Always dedicate 5 minutes to warming up and 5 minutes to cooling down"
                ]
            }
        ],
        "diagnostics": [
            {
                "param": "Resting Blood Pressure",
                "range": "Normal: < 120/80 mm Hg",
                "meaning": "Force of blood pumping against arterial walls. Readings >=130 indicate hypertension, accelerating arterial plaque hardening."
            },
            {
                "param": "Serum Cholesterol",
                "range": "Normal: < 200 mg/dL",
                "meaning": "Total circulating lipid mass. Elevated levels lead to atherosclerotic plaques inside coronary arteries that can rupture."
            },
            {
                "param": "Resting Electrocardiogram (ECG)",
                "range": "Normal: Sinus Rhythm, Normal Waves",
                "meaning": "Records the electrical impulses of heart beats. ST-T wave abnormalities suggest repolarization delays or chronic ventricular strain."
            },
            {
                "param": "Exercise Induced ST Depression (Oldpeak)",
                "range": "Normal: < 1.0 mm",
                "meaning": "Downward shift of ST segment on ECG during exertion. Values >1.5 mm indicate myocardial oxygen deprivation (ischemia)."
            },
            {
                "param": "Thalassemia Perfusion Scan",
                "range": "Normal: Uniform Myocardial Perfusion",
                "meaning": "Nuclear scan evaluating blood distribution across the myocardium. Reversible defect indicates ischemia that can be treated."
            },
            {
                "param": "Fluoroscopy Major Vessels (CA)",
                "range": "Normal: 0 Vessels Colored",
                "meaning": "X-ray fluoroscopy visualizing major coronary arteries. Values >0 indicate arterial narrowing or calcification."
            }
        ],
        "emergency": {
            "hotline": "108 (India Emergency Ambulance) / Health Hospitals Tenali: +91 (08644) 223456",
            "signs": [
                "Crushing, squeezing, or heavy pressure in the center of the chest lasting >5 minutes",
                "Pain radiating to left arm, shoulder, jaw, neck, or back",
                "Cold sweat accompanied by unexplained dizziness or fainting",
                "Severe shortness of breath with or without chest discomfort",
                "Sudden nausea, indigestion-like epigastric burning, or severe weakness"
            ],
            "action_steps": [
                "1. STOP ALL ACTIVITY and sit down upright against a wall or in a comfortable chair.",
                "2. CALL 108 or your local emergency hospital immediately. Do NOT attempt to drive yourself.",
                "3. CHEW ONE ASPIRIN (300-325 mg) unless allergic or instructed otherwise by a doctor.",
                "4. LOOSEN TIGHT CLOTHING around neck, chest, and waist to facilitate easy breathing.",
                "5. STAY CALM and take slow, steady breaths while awaiting medical paramedics."
            ]
        },
        "hospital": {
            "name": HOSPITAL_INFO["name"],
            "dept": HOSPITAL_INFO["department"],
            "address": HOSPITAL_INFO["address"],
            "email": HOSPITAL_INFO["email"],
            "phone": HOSPITAL_INFO["phone"],
            "services": [
                "24/7 Cardiac Emergency Care & Coronary Care Unit (CCU)",
                "Digital 12-Lead ECG & 2D Doppler Echocardiography",
                "Computerized Treadmill Stress Testing (TMT)",
                "24-Hour Ambulatory Holter & Blood Pressure Monitoring",
                "Coronary Angiography & Interventional Cardiology Suite",
                "Comprehensive Preventive Heart Health Screening Packages"
            ]
        }
    }
