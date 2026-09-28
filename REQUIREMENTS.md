# Project Requirements & Technical Specifications
## Heart Disease Prediction & Clinical Report Generation System
**Health Hospitals Tenali &bull; Centre for Excellence in Cardiology**

This document provides a comprehensive breakdown of all software, system, hardware, network, and dependency requirements for running the Heart Disease Prediction & Clinical Report Generation application.

---

## 1. System & Hardware Requirements

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | macOS 11+, Windows 10/11 (64-bit), or Linux (Ubuntu 20.04+) | macOS 13+ / Windows 11 / Ubuntu 22.04 LTS |
| **Processor (CPU)** | Dual-core 2.0 GHz Intel/AMD or Apple Silicon (M1/M2/M3) | Quad-core 2.5 GHz+ or Apple Silicon |
| **System Memory (RAM)** | 4 GB RAM | 8 GB RAM or higher |
| **Disk Storage** | 1.5 GB free disk space (includes virtualenv and datasets) | 3 GB free disk space |
| **Display Resolution** | 1280 x 720 (HD) | 1920 x 1080 (Full HD) or higher |
| **Internet Connection** | Required for initial package installation & Cloudflare tunnel | High-speed broadband (>5 Mbps) |

---

## 2. Python Environment Requirements

- **Python Runtime:** Python **3.9**, **3.10**, or **3.11** (64-bit).
- **Package Manager:** `pip` version 22.0 or higher.
- **Virtual Environment:** Strongly recommended (`.venv`).

### Python Dependency Breakdown (`requirements.txt`)

| Package | Version Requirement | Purpose / Module Usage |
| :--- | :--- | :--- |
| `pandas` | `>=1.5.3` | Dataset manipulation, CSV reading, biomarker tabular structuring, and Excel export. |
| `numpy` | `>=1.24.0, <2.0.0` | Numerical arrays, probability transformations, and feature vector operations. |
| `scikit-learn` | `>=1.2.2` | Random Forest Classifier, StandardScaler, train/test splitting, and evaluation metrics. |
| `joblib` | `>=1.2.0` | Serialization and deserialization of the trained ML model (`rf_heart_model.pkl`) and scaler (`scaler.pkl`). |
| `scipy` | `>=1.10.0` | Scientific computing support for scikit-learn models and statistical distributions. |
| `matplotlib` | `>=3.7.1` | Feature importance bar charts, cardiovascular risk plotting, and visualization. |
| `seaborn` | `>=0.12.2` | Statistical data visualizations and correlation heatmaps in EDA notebooks. |
| `jupyter` | `>=1.0.0` | Interactive exploratory data analysis notebooks (`notebooks/01_eda.ipynb` & `02_model_training.ipynb`). |
| `streamlit` | `>=1.30.0` | Interactive web application framework, input form, real-time UI, and audio/visual presentation. |
| `openpyxl` | `>=3.1.0` | Reading and writing patient records to Microsoft Excel files (`outputs/patient_details.xlsx`). |
| `reportlab` | `>=4.0.0` | Automated generation of official, downloadable, styled Clinical Cardiology Assessment PDF reports. |
| `requests` | `>=2.31.0` | Network diagnostics, connection validation, and tunnel status verification. |
| `python-dotenv` | `>=1.0.0` | Secure environment variable configuration (e.g. `GEMINI_API_KEY`). |
| `google-genai` | `>=1.0.0` | (Optional) Google Gemini Flash API integration for generative conversational cardiology intelligence. |

---

## 3. Network & Tunnel Requirements (Cloudflare Tunnel)

To access the application over the public internet from any device (phone, laptop, tablet):

- **Local Port:** Port `8501` (default Streamlit port; fallback to `8502-8510` if occupied).
- **Outbound Network Traffic:** Outbound HTTPS traffic on port `443` to Cloudflare edge networks (`*.trycloudflare.com`).
- **Binary Tool:** `cloudflared` (pre-packaged binary included in project root for macOS; automatic detection and download for Linux/Windows).
- **Public Ephemeral Link:** When using `cloudflared tunnel --url http://localhost:8501`, Cloudflare generates an ephemeral URL (e.g. `https://xxx.trycloudflare.com`).
  > **Note on Free Tunnels:** Ephemeral Cloudflare links expire when the tunnel process stops. The automated launcher (`start_app.py` / `run.sh`) continuously monitors and displays the active link, saving it to `outputs/LIVE_URL.txt` and `outputs/OPEN_APP.html` for single-click access.

---

## 4. Dataset & Clinical Parameters Schema

The predictive model is trained on the Cleveland Heart Disease Dataset (`data/heart.csv`):
- **Records:** 1,025 patient instances.
- **Attributes:** 13 input clinical features + 1 target variable (`target` = 1 heart disease present, 0 absence).

| Feature Name | Clinical Description | Value Range / Categories | Normal Reference Range |
| :--- | :--- | :--- | :--- |
| `age` | Patient age | 29 to 77 years | Adult demographic |
| `sex` | Biological sex | 0 = Female, 1 = Male | N/A |
| `cp` | Chest pain type | 0: Typical angina<br>1: Atypical angina<br>2: Non-anginal pain<br>3: Asymptomatic | 0 (Asymptomatic / No Angina) |
| `trestbps` | Resting blood pressure | 90 to 200 mm Hg | 90 - 120 mm Hg (< 120/80) |
| `chol` | Serum cholesterol | 126 to 564 mg/dL | < 200 mg/dL |
| `fbs` | Fasting blood sugar > 120 mg/dL | 0 = False (<=120), 1 = True (>120) | 0 (Fasting glucose < 100 mg/dL) |
| `restecg` | Resting electrocardiographic results | 0: Normal<br>1: ST-T wave abnormality<br>2: Left ventricular hypertrophy | 0 (Normal sinus rhythm) |
| `thalach` | Maximum heart rate achieved | 71 to 202 bpm | 120 - 180 bpm (Age-adjusted) |
| `exang` | Exercise induced angina | 0 = No, 1 = Yes | 0 (Absence of angina) |
| `oldpeak` | ST depression induced by exercise | 0.0 to 6.2 mm | < 1.0 mm |
| `slope` | Slope of peak exercise ST segment | 0: Upsloping<br>1: Flat<br>2: Downsloping | 0 (Upsloping) |
| `ca` | Number of major vessels colored by fluoroscopy | 0 to 3 vessels | 0 (No arterial obstruction) |
| `thal` | Thallium stress scintigraphy | 1: Normal<br>2: Fixed defect<br>3: Reversible defect | 1 (Normal myocardial perfusion) |

---

## 5. Automated Execution Requirements

The project includes zero-configuration automated runners:
- **macOS / Linux:** Run `./run.sh` or `python3 start_app.py`
- **Windows:** Run `run.bat` or `python start_app.py`

The runner automatically:
1. Detects Python 3 and activates/creates `.venv`.
2. Installs and updates all missing dependencies from `requirements.txt`.
3. Verifies trained model files (`models/rf_heart_model.pkl` and `models/scaler.pkl`).
4. Launches the Streamlit UI on local port 8501.
5. Launches the Cloudflare tunnel and streams the public link to the terminal.
6. Generates `outputs/OPEN_APP.html` for instant browser launch.
