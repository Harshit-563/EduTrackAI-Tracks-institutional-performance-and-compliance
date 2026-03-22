# risk_engine.py

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

MODEL_PATH = "risk_model.pkl"
SCALER_PATH = "scaler.pkl"

# -------------------------------
# TRAINING
# -------------------------------

def train_model(csv_path="college_data.csv"):
    """
    Trains an Isolation Forest model to detect risky / anomalous colleges.
    Uses ONLY college-level aggregated metrics.
    """

    print("📥 Loading college dataset...")
    df = pd.read_csv(csv_path)

    # -------------------------------
    # Feature Engineering
    # -------------------------------

    df["Student_Faculty_Ratio"] = df["Total_Students"] / df["Total_Faculty"].replace(0, np.nan)
    df["Infra_Per_Student"] = df["Infrastructure_Area"] / df["Total_Students"].replace(0, np.nan)

    df.fillna(0, inplace=True)

    FEATURES = [
        "Placement_Rate",
        "Fund_Utilization",
        "Student_Faculty_Ratio",
        "Infra_Per_Student",
        "Avg_Doc_DSS",
        "Missing_Doc_Count"
    ]

    X = df[FEATURES]

    # -------------------------------
    # Scaling
    # -------------------------------

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # -------------------------------
    # Model Training
    # -------------------------------

    model = IsolationForest(
        n_estimators=200,
        contamination=0.08,   # expected risky institutions
        random_state=42
    )

    model.fit(X_scaled)

    # -------------------------------
    # Save artifacts
    # -------------------------------

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    print("✅ Risk model trained successfully")
    print("💾 Saved: risk_model.pkl, scaler.pkl")


# -------------------------------
# PREDICTION
# -------------------------------

def predict_risk(metrics_json: dict):
    """
    Predicts institutional risk.

    Input (example):
    {
        "Total_Students": 1200,
        "Total_Faculty": 40,
        "Placement_Rate": 55,
        "Fund_Utilization": 78,
        "Infrastructure_Area": 3500,
        "Avg_Doc_DSS": 62,
        "Missing_Doc_Count": 2
    }
    """

    try:
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
    except FileNotFoundError:
        return {"error": "Risk model not trained. Run train_model() first."}

    try:
        # -------------------------------
        # Input parsing
        # -------------------------------

        students = float(metrics_json["Total_Students"])
        faculty = float(metrics_json["Total_Faculty"])
        placement = float(metrics_json["Placement_Rate"])
        funds = float(metrics_json["Fund_Utilization"])
        infra = float(metrics_json["Infrastructure_Area"])
        avg_dss = float(metrics_json["Avg_Doc_DSS"])
        missing_docs = int(metrics_json["Missing_Doc_Count"])

        sf_ratio = students / faculty if faculty > 0 else 999
        infra_per_student = infra / students if students > 0 else 0

        feature_names = [
            "Placement_Rate",
            "Fund_Utilization",
            "Student_Faculty_Ratio",
            "Infra_Per_Student",
            "Avg_Doc_DSS",
            "Missing_Doc_Count"
        ]

        input_df = pd.DataFrame(
            [[placement, funds, sf_ratio, infra_per_student, avg_dss, missing_docs]],
            columns=feature_names
        )

        input_scaled = scaler.transform(input_df)

        # -------------------------------
        # Model Prediction
        # -------------------------------

        prediction = model.predict(input_scaled)[0]     # -1 = anomaly
        anomaly_score = model.decision_function(input_scaled)[0]

        # -------------------------------
        # Risk Score Mapping (0–100)
        # -------------------------------

        # Lower decision_function → more risky
        normalized = np.clip((anomaly_score + 0.25) / 0.5, 0, 1)
        risk_score = round(100 * (1 - normalized), 2)

        # -------------------------------
        # Explainable Flags
        # -------------------------------

        flags = []

        if sf_ratio > 40:
            flags.append(f"Critical student–faculty ratio ({sf_ratio:.1f}:1)")

        if placement < 35:
            flags.append(f"Low placement rate ({placement}%)")

        if avg_dss < 60:
            flags.append("Poor average document compliance score")

        if missing_docs >= 2:
            flags.append(f"{missing_docs} mandatory documents missing")

        if prediction == -1:
            flags.append("AI detected anomalous institutional patterns")

        status = "High Risk" if prediction == -1 or risk_score > 70 else "Normal"

        return {
            "risk_score": risk_score,
            "status": status,
            "flags": flags
        }

    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# LOCAL TEST
# -------------------------------

if __name__ == "__main__":
    train_model()

    print("\n🟢 NORMAL COLLEGE")
    good_college = {
        "Total_Students": 1000,
        "Total_Faculty": 50,
        "Placement_Rate": 85,
        "Fund_Utilization": 92,
        "Infrastructure_Area": 4000,
        "Avg_Doc_DSS": 88,
        "Missing_Doc_Count": 0
    }
    print(predict_risk(good_college))

    print("\n🔴 HIGH RISK COLLEGE")
    bad_college = {
        "Total_Students": 2000,
        "Total_Faculty": 8,
        "Placement_Rate": 28,
        "Fund_Utilization": 95,
        "Infrastructure_Area": 3000,
        "Avg_Doc_DSS": 52,
        "Missing_Doc_Count": 3
    }
    print(predict_risk(bad_college))
