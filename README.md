
<img width="1920" height="1019" alt="Screenshot 2025-12-02 231423" src="https://github.com/user-attachments/assets/bd34b6ba-f206-4826-99a3-12b54a5573a1" />
<img width="1920" height="1039" alt="Screenshot 2025-12-03 1818441" src="https://github.com/user-attachments/assets/9688de50-c123-4883-a254-08ae337d993a" />





                
              ## 🧠 System Architecture

```text
                ┌────────────────────────┐
                │   Document Upload UI   │
                └──────────┬─────────────┘
                           ↓

┌──────────────────────────────────────────────────┐
│ LAYER 1: DOCUMENT TRUST & COMPLIANCE (Per-Doc)  │
│                                                  │
│ OCR → Rule Validation → (Optional) LLM Assist   │
│                                                  │
│ Output:                                          │
│  - DSS Score (0–100)                             │
│  - Classification (Valid / Review)               │
│  - Flags (explainable issues)                    │
└──────────┬───────────────────────────────────────┘
           ↓ (Aggregated per institution)

┌──────────────────────────────────────────────────┐
│ LAYER 2: INSTITUTION COMPLIANCE SCORING         │
│                                                  │
│ Aggregates all document results:                 │
│  - Missing mandatory documents?                  │
│  - Expired / weak documents?                     │
│  - Average DSS score                             │
│                                                  │
│ Output:                                          │
│  - Compliance Index (0–100)                      │
│  - Status (Compliant / Review Required)          │
│  - Actionable reasons                            │
└──────────┬───────────────────────────────────────┘
           ↓ (Structured institutional metrics)

┌──────────────────────────────────────────────────┐
│ LAYER 3: RISK & ANOMALY DETECTION (ML Layer)    │
│                                                  │
│ Isolation Forest (unsupervised anomaly model)    │
│                                                  │
│ Evaluates:                                       │
│  - Student–Faculty ratio                         │
│  - Placement rate                                │
│  - Infrastructure per student                    │
│  - Compliance score                              │
│                                                  │
│ Output:                                          │
│  - Risk score (0–100)                            │
│  - Risk status (Normal / High Risk)              │
│  - Anomaly flags                                 │
└──────────────────────────────────────────────────┘
```


# EduTrack

EduTrack is an AI-based institutional compliance and risk assessment platform for education regulators and institutions. It combines document validation, compliance scoring, anomaly detection, and dashboard-based review workflows to make accreditation and oversight decisions faster, more explainable, and easier to audit.

## Overview

The project is built around a three-step decision-support flow:

1. Documents are uploaded and processed with OCR-based validation.
2. Institution-level compliance signals are aggregated into explainable scores.
3. Machine learning models evaluate risk, performance, and anomalies from institutional metrics.

On top of that pipeline, EduTrack includes a React dashboard for reviewers, institutional users, and admins.

## Key Features

- OCR-assisted validation for uploaded PDF and image documents
- Document Sufficiency Score (DSS) generation with explainable flags
- Institution-level compliance scoring and review prioritization
- ML-powered risk assessment, performance tier prediction, and anomaly detection
- Rank-list and analytics views for institutional comparison
- FastAPI backend services for uploads, review workflows, and scoring APIs
- React frontend for dashboards, reviewer queues, uploads, and analytics
- Report generation outputs for institutional summaries and visualizations

## Architecture

```text
Frontend (React + Vite)
    |
    +-- Review dashboard
    +-- Upload workflow
    +-- Analytics and rank list
    |
FastAPI Services
    |
    +-- Workflow API
    |     - auth
    |     - upload and analyze
    |     - reviewer queue
    |     - institution overview
    |
    +-- ML Scoring API
          - risk prediction
          - performance prediction
          - anomaly detection
          - batch evaluation
    |
Core Processing
    |
    +-- OCR engine
    +-- document predictor
    +-- compliance aggregation
    +-- risk and anomaly models
    +-- report generation
```

## Tech Stack

- Python
- FastAPI
- Scikit-learn
- Pandas and NumPy
- Tesseract OCR
- React
- Vite
- Tailwind CSS
- Recharts

## Repository Structure

```text
edutech/
|-- backend/                  # Additional backend setup docs
|-- data/                     # Raw and processed datasets
|-- doc_validator/            # OCR and document validation logic
|-- docs/                     # Project documentation
|-- edutrack-frontend/        # React frontend
|-- models/                   # Trained ML models
|-- notebooks/                # Data cleaning and analysis notebooks
|-- outputs/                  # Reports, analysis outputs, visualizations
|-- scripts/                  # Data preparation pipelines
|-- src/
|   |-- api/                  # ML scoring FastAPI app
|   |-- data_processing/      # Cleaning and transformation logic
|   |-- ml_models/            # Model training utilities
|   `-- reporting/            # HTML and JSON report generators
|-- utils/                    # Shared constants and helpers
|-- run_full_pipeline.py      # End-to-end DSS pipeline runner
`-- README.md
```

## Core Workflows

### 1. Document Validation

Uploaded files are processed through OCR and rule-based checks to extract fields and identify missing or weak evidence. Each file receives a DSS score and validation flags.

### 2. Compliance Aggregation

Document-level outputs are rolled up into institution-level compliance indicators, including average document quality and missing document penalties.

### 3. ML-Based Evaluation

Institutional metrics such as placement rate, faculty adequacy, infrastructure quality, financial efficiency, and compliance score are evaluated by ML models to produce:

- risk level
- performance tier
- anomaly status
- overall institutional score

## Local Setup

### Prerequisites

- Python 3.10+
- Node.js 16+
- npm
- Tesseract OCR installed and added to system path

Optional for PDF-heavy workflows:

- Poppler installed and added to system path

### 1. Clone the repository

```bash
git clone https://github.com/your-username/edutrack.git
cd edutrack
```

### 2. Install Python dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install frontend dependencies

```bash
cd edutrack-frontend
npm install
cd ..
```

### 4. Configure frontend API URL

Create `edutrack-frontend/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Running the Project

EduTrack includes two FastAPI apps in the repository:

- `src/main.py`: workflow API for auth, uploads, reviewer actions, and institution views
- `src/api/main.py`: ML scoring API for risk, performance, anomaly, and batch evaluation

You can run either service independently depending on what you want to demo.

### Run the workflow backend

```bash
uvicorn src.main:app --reload --port 8000
```

### Run the ML scoring backend

```bash
uvicorn src.api.main:app --reload --port 8001
```

### Run the frontend

```bash
cd edutrack-frontend
npm run dev
```

Frontend default local URL:

```text
http://localhost:5173
```

## API Highlights

### Workflow API

- `POST /auth/login`
- `GET /auth/me`
- `GET /reviewer/queue`
- `GET /reviewer/document/{id}`
- `POST /reviews/{id}/action`
- `POST /upload-analyze`
- `GET /institutions/{id}/overview`
- `GET /institutions/{id}/dss-trend`
- `GET /institutions/rank-list`

### ML Scoring API

- `GET /health`
- `POST /predict/risk`
- `POST /predict/performance`
- `POST /predict/anomaly`
- `POST /evaluate/institution`
- `POST /batch/evaluate`

## Demo Login Accounts

The workflow backend includes demo users in memory for local testing:

- `principal.techno@college.test` / `test123`
- `reviewer.ramesh@aicte-review.test` / `test123`
- `superadmin@edutrack.test` / `admin123`

## End-to-End Pipeline

To run the scripted document-to-risk workflow:

```bash
python run_full_pipeline.py
```

This pipeline demonstrates:

- OCR on sample institutional documents
- per-document DSS scoring
- institution-level compliance aggregation
- final risk prediction and decision support output

## Sample Outputs

The repository already contains generated artifacts under `outputs/`, including:

- institutional HTML and JSON reports
- risk assessment CSV outputs
- analytics visualizations
- derived institutional scores

## Why This Project Matters

EduTrack is designed to support regulator-safe and human-review-first decision making. Instead of producing black-box outputs, it emphasizes traceable scores, review flags, and institution-level summaries that can help teams:

- reduce manual document screening time
- prioritize high-risk submissions
- compare institutions consistently
- support accreditation and compliance audits with explainable evidence

## Future Improvements

- Database-backed persistence instead of in-memory demo data
- Role-based access hardening and production auth
- Real-time dashboard updates
- Improved OCR extraction for more document types
- Better deployment separation between workflow and scoring services
- Expanded reporting and audit trails
