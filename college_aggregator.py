# college_aggregator.py

MANDATORY_DOCS = {
    "fire_safety_certificate": 30,
    "affiliation_letter": 40,
    "faculty_list": 30
}

def aggregate_college(doc_outputs: dict):
    """
    doc_outputs = {
        "fire_safety_certificate": {...},
        "faculty_list": {...}
    }
    """

    score = 0
    flags = []

    for doc, weight in MANDATORY_DOCS.items():
        if doc not in doc_outputs:
            flags.append(f"Missing mandatory document: {doc}")
            continue

        score += doc_outputs[doc]["dss_score"] * (weight / 100)

    status = "Compliant" if score >= 70 and not flags else "Review Required"

    return {
        "college_compliance_score": round(score, 2),
        "status": status,
        "flags": flags
    }
