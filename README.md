
<img width="1920" height="1000" alt="Screenshot 2025-12-02 231423" src="https://github.com/user-attachments/assets/ac4a76f2-7b05-43df-b2e2-349843c7814f" />
                ┌────────────────────────┐
                │   Document Upload UI   │
                └──────────┬─────────────┘
                           ↓
┌──────────────────────────────────────────────────┐
│ LAYER 1: DOCUMENT TRUST & COMPLIANCE (Per-Doc)   │
│                                                  │
│ OCR → Validation Rules → LLM Compliance Check    │
│ Output:                                          │
│  - is_valid_document                              │
│  - compliance_status                              │
│  - dss_score (0–100)                              │
│  - flags                                         │
└──────────┬───────────────────────────────────────┘
           ↓ (Aggregated)
┌──────────────────────────────────────────────────┐
│ LAYER 2: INSTITUTION COMPLIANCE SCORE (College)  │
│                                                  │
│ Aggregates all documents:                        │
│  - Missing mandatory docs?                       │
│  - Expired docs?                                 │
│  - Avg DSS score                                 │
│ Output:                                          │
│  - Compliance Index (0–100)                      │
│  - Actionable reasons                            │
└──────────┬───────────────────────────────────────┘
           ↓ (Structured metrics)
┌──────────────────────────────────────────────────┐
│ LAYER 3: RISK & FRAUD DETECTION (ML)              │
│                                                  │
│ Isolation Forest / XGBoost / Rules               │
│ Output:                                          │
│  - Risk score (0–100)                             │
│  - Anomaly flags                                 │
└──────────────────────────────────────────────────┘
🏫 EduTrack — AI-Based Institutional Compliance & Risk System

EduTrack is an AI-driven Decision Support System (DSS) that validates institutional documents, evaluates compliance, and detects risk using explainable scoring and anomaly detection.

It is designed for regulatory bodies such as AICTE, UGC, NAAC, and accreditation boards.

🚀 Features

📄 PDF & Image document upload

🔍 OCR-based document text extraction

📊 Document Sufficiency Score (DSS)

🏛 College-level compliance aggregation

🤖 ML-based anomaly detection (Isolation Forest)

📈 Institutional risk scoring (0–100)

🧾 Explainable flags at every layer

🏆 College ranking support

🧠 How It Works

EduTrack follows a 3-layer architecture:

Document Layer → Compliance Layer → Risk Layer

1️⃣ Document Validation

Extracts text via OCR

Checks for:

Date presence

Signature presence

Required keywords

Generates DSS score (0–100)

Example:

{
  "dss_score": 35,
  "flags": ["missing_date", "missing_signature"],
  "classification": "Needs Review"
}

2️⃣ College Compliance Aggregation

Combines multiple document DSS scores

Applies weighted scoring for mandatory documents

Outputs compliance score

Example:

{
  "college_compliance_score": 64.5,
  "status": "Review Required"
}

3️⃣ Risk Engine (ML-Based)

Uses Isolation Forest (unsupervised anomaly detection)

Evaluates:

Student–Faculty ratio

Placement rate

Infrastructure per student

Compliance score

Outputs risk score (0–100)

Example:

{
  "risk_score": 43.03,
  "status": "Normal"
}

📂 Project Structure
edutech/
│
├── doc_validator/
│   ├── ocr_engine.py
│   ├── predictor.py
│
├── college_aggregator.py
├── risk_engine.py
├── run_full_pipeline.py
├── college_data.csv
├── requirements.txt
└── README.md

⚙️ Installation
1️⃣ Clone Repository
git clone https://github.com/yourusername/edutrack.git
cd edutrack

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Install Tesseract OCR

Download:
https://github.com/tesseract-ocr/tesseract

Update path in:

ocr_engine.py

4️⃣ Install Poppler (for PDF support)

Download:
https://github.com/oschwartz10612/poppler-windows/releases/

Add to system PATH:

C:\poppler\Library\bin


Verify:

pdftoppm -h

▶️ Usage
Train Risk Model
python risk_engine.py

Run Full Pipeline
python run_full_pipeline.py

📊 Dataset

The system uses a college dataset including:

Total Students

Total Faculty

Placement Rate

Infrastructure Area

Rating

Fees

Location

Establishment Year

Derived features:

Student–Faculty Ratio

Infrastructure per student

Avg Document DSS

Missing Document Count

🛡 Design Principles

Explainable AI (no black-box decisions)

Human-review-first approach

Modular architecture

Scalable document types

Regulator-safe decision support

🔮 Future Improvements

FastAPI backend deployment

Role-based review system

PDF audit report generation

Real-time dashboard updates

Graph-based fraud detection

👨‍💻 Tech Stack

Python

Scikit-Learn

Pandas & NumPy

Tesseract OCR

pdf2image

React (Frontend)

