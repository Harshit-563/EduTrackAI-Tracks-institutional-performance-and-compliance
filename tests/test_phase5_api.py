
from src.main import app


client = TestClient(app)


def test_predict_risk_endpoint():
    response = client.post(
        "/api/v1/predict/risk",
        json={
            "student_faculty_ratio": 18.5,
            "faculty_adequacy": 85.0,
            "placement_rate": 82.0,
            "infrastructure_quality": 76.0,
            "financial_efficiency": 71.0,
            "fund_utilization": 69.0,
            "avg_doc_dss": 78.0,
            "missing_doc_count": 0,
            "total_students": 4000,
            "total_faculty": 220,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_level" in data


def test_predict_performance_endpoint():
    response = client.post(
        "/api/v1/predict/performance",
        json={
            "student_faculty_ratio": 18.5,
            "faculty_adequacy": 85.0,
            "placement_rate": 82.0,
            "infrastructure_quality": 76.0,
            "financial_efficiency": 71.0,
            "fund_utilization": 69.0,
            "avg_doc_dss": 78.0,
            "missing_doc_count": 0,
            "total_students": 4000,
            "total_faculty": 220,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "performance_tier" in data


def test_evaluate_institution_endpoint():
    response = client.post(
        "/api/v1/evaluate/institution",
        json={
            "student_faculty_ratio": 18.5,
            "faculty_adequacy": 85.0,
            "placement_rate": 82.0,
            "infrastructure_quality": 76.0,
            "financial_efficiency": 71.0,
            "fund_utilization": 69.0,
            "avg_doc_dss": 78.0,
            "missing_doc_count": 0,
            "total_students": 4000,
            "total_faculty": 220,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_assessment" in data
    assert "performance_tier" in data
    assert "anomaly_detection" in data
