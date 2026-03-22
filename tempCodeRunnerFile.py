# run_full_pipeline.py

"""
End-to-End DSS Pipeline

Flow:
1. OCR documents
2. Document validation (DSS per document)
3. College-level aggregation
4. Risk prediction

This script assumes:
- doc_validator/ exists
- college_aggregator.py exists
- risk_engine.py exists
"""

from doc_validator.ocr_engine import run_ocr
from doc_validator.predictor import predict_from_ocr
from college_aggregator import aggregate_college
from risk_engine import predict_risk

# ----------------------------------
# STEP 0: INPUTS (simulate one college)
# ----------------------------------

COLLEGE_METADATA = {
    "college_id": "COL_001",
    "Total_Students": 1200,
    "Total_Faculty": 35,
    "Placement_Rate": 58,
    "Fund_Utilization": 82,
    "Infrastructure_Area": 4200
}

DOCUMENT_FILES = {
    "fire_safety_certificate": "sample_docs/fire_cert.pdf",
    "faculty_list": "sample_docs/faculty_list.pdf",
    "affiliation_letter": "sample_docs/affiliation_letter.pdf"
}

# ----------------------------------
# STEP 1: OCR + DOCUMENT VALIDATION
# ----------------------------------

print("\n🔹 STEP 1: Document Validation\n")

document_outputs = {}

for doc_type, file_path in DOCUMENT_FILES.items():
    print(f"Processing document: {doc_type}")

    # OCR
    ocr_output = run_ocr(file_path)
    ocr_output["doc_type"] = doc_type

    # Document DSS
    doc_result = predict_from_ocr(ocr_output)

    document_outputs[doc_type] = doc_result

    print(f"  DSS Score: {doc_result['dss_score']}")
    print(f"  Flags   : {doc_result['flags']}\n")

# ----------------------------------
# STEP 2: COLLEGE COMPLIANCE AGGREGATION
# ----------------------------------

print("\n🔹 STEP 2: College Compliance Aggregation\n")

college_compliance = aggregate_college(document_outputs)

print("College Compliance Result:")
print(college_compliance)

# ----------------------------------
# STEP 3: PREPARE RISK INPUT
# ----------------------------------

avg_doc_dss = college_compliance["college_compliance_score"]
missing_docs = len(college_compliance["flags"])

risk_input = {
    **COLLEGE_METADATA,
    "Avg_Doc_DSS": avg_doc_dss,
    "Missing_Doc_Count": missing_docs
}

# ----------------------------------
# STEP 4: RISK PREDICTION
# ----------------------------------

print("\n🔹 STEP 3: Risk Prediction\n")

risk_result = predict_risk(risk_input)

print("Risk Assessment Result:")
print(risk_result)

# ----------------------------------
# FINAL OUTPUT
# ----------------------------------


def final_verdict(college_compliance, risk_result):
    if risk_result["status"] == "High Risk":
        return "Reject"
    if college_compliance["status"] == "Review Required":
        return "Manual Review Required"
    return "Approved"
final_decision = final_verdict(college_compliance, risk_result)

final_output = {
    "college_id": COLLEGE_METADATA["college_id"],
    "document_summary": document_outputs,
    "college_compliance": college_compliance,
    "risk_assessment": risk_result
}

print("\n✅ FINAL DSS OUTPUT\n")
print(final_output)
