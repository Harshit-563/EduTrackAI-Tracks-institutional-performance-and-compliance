"""
EduTrack ML Model Trainer
- Trains risk classification and performance prediction models
- Uses engineered features for institutional evaluation
- Saves and evaluates models
"""

import pandas as pd
import numpy as np
import logging
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier, IsolationForest
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    roc_curve, precision_recall_curve, f1_score
)
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/model_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train ML models for EduTrack"""
    
    def __init__(self, model_dir: str = "models/trained_models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        
    def load_data(self, features_file: str) -> pd.DataFrame:
        """Load engineered features"""
        logger.info(f"Loading features from {features_file}")
        df = pd.read_csv(features_file)
        logger.info(f"Loaded {len(df):,} records with {len(df.columns)} features")
        return df
    
    def prepare_risk_classification(self, df: pd.DataFrame):
        """Prepare data for risk classification (High vs Low Risk)"""
        logger.info("[RISK MODEL] Preparing data...")
        
        # Target: High Compliance Risk (1) vs Low (0)
        y = df['High_Compliance_Risk'].astype(int)
        
        # Select features for risk prediction
        feature_cols = [
            'Student_Faculty_Ratio', 'Faculty_Adequacy',
            'Placement_Rate', 'Infrastructure_Quality',
            'Financial_Efficiency', 'Fund_Utilization',
            'Avg_Doc_DSS', 'Missing_Doc_Count',
            'Total_Students', 'Total_Faculty'
        ]
        
        X = df[feature_cols].copy()
        X = X.fillna(X.median())
        
        logger.info(f"Features: {len(feature_cols)} | Target: Risk Classification")
        logger.info(f"Class distribution: {y.value_counts().to_dict()}")
        
        return X, y, feature_cols
    
    def prepare_performance_classification(self, df: pd.DataFrame):
        """Prepare data for performance tier classification"""
        logger.info("[PERFORMANCE MODEL] Preparing data...")
        
        # Create performance tiers based on Overall_Performance_Score
        score = df['Overall_Performance_Score']
        y = pd.cut(score, bins=[0, 40, 60, 80, 100], 
                   labels=['Critical', 'Average', 'Good', 'Excellent'])
        y = y.astype(str)
        
        # Features
        feature_cols = [
            'Student_Faculty_Ratio', 'Faculty_Adequacy',
            'Placement_Rate', 'Infrastructure_Quality',
            'Financial_Efficiency', 'Fund_Utilization',
            'Avg_Doc_DSS', 'Missing_Doc_Count',
            'Total_Students', 'Total_Faculty'
        ]
        
        X = df[feature_cols].copy()
        X = X.fillna(X.median())
        
        logger.info(f"Features: {len(feature_cols)} | Target: Performance Tiers")
        logger.info(f"Class distribution: {y.value_counts().to_dict()}")
        
        return X, y, feature_cols
    
    def train_risk_model(self, X, y, feature_names):
        """Train risk classification model"""
        logger.info("\n[TRAINING] Risk Classification Model")
        logger.info("=" * 60)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['risk'] = scaler
        
        logger.info(f"Training set: {X_train.shape[0]:,} | Test set: {X_test.shape[0]:,}")
        
        # Train multiple models and select best
        models_to_train = {
            'RandomForest': RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
            'GradientBoosting': GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42),
            'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42)
        }
        
        best_model = None
        best_score = 0
        results = {}
        
        for name, model in models_to_train.items():
            # Train
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            y_proba = model.predict_proba(X_test_scaled)[:, 1]
            
            score = roc_auc_score(y_test, y_proba)
            f1 = f1_score(y_test, y_pred)
            
            logger.info(f"\n{name}:")
            logger.info(f"  ROC-AUC: {score:.4f}")
            logger.info(f"  F1-Score: {f1:.4f}")
            
            results[name] = {'auc': score, 'f1': f1, 'model': model}
            
            if score > best_score:
                best_score = score
                best_model = model
                best_name = name
        
        logger.info(f"\n[BEST MODEL] {best_name} (ROC-AUC: {best_score:.4f})")
        
        # Save model
        model_path = self.model_dir / 'risk_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(best_model, f)
        logger.info(f"Saved: {model_path}")
        
        self.models['risk'] = best_model
        return best_model, scaler
    
    def train_performance_model(self, X, y, feature_names):
        """Train performance tier classification model"""
        logger.info("\n[TRAINING] Performance Classification Model")
        logger.info("=" * 60)
        
        # Encode target
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        self.encoders['performance'] = le
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['performance'] = scaler
        
        logger.info(f"Training set: {X_train.shape[0]:,} | Test set: {X_test.shape[0]:,}")
        logger.info(f"Classes: {le.classes_}")
        
        # Train models
        model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        from sklearn.metrics import accuracy_score
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model: RandomForest")
        logger.info(f"Accuracy: {accuracy:.4f}")
        
        # Classification report
        logger.info("\nClassification Report:")
        report = classification_report(y_test, y_pred, target_names=le.classes_)
        logger.info(report)
        
        # Save
        model_path = self.model_dir / 'performance_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Saved: {model_path}")
        
        self.models['performance'] = model
        return model, scaler
    
    def train_anomaly_detector(self, X, feature_names):
        """Train anomaly detection model"""
        logger.info("\n[TRAINING] Anomaly Detection Model (Isolation Forest)")
        logger.info("=" * 60)
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        self.scalers['anomaly'] = scaler
        
        # Train Isolation Forest
        model = IsolationForest(contamination=0.05, random_state=42, n_jobs=-1)
        y_pred = model.fit_predict(X_scaled)
        
        n_anomalies = (y_pred == -1).sum()
        pct_anomalies = (n_anomalies / len(y_pred)) * 100
        
        logger.info(f"Anomalies detected: {n_anomalies} ({pct_anomalies:.2f}%)")
        
        # Save
        model_path = self.model_dir / 'anomaly_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Saved: {model_path}")
        
        self.models['anomaly'] = model
        return model, scaler
    
    def save_scalers(self):
        """Save all scalers"""
        for name, scaler in self.scalers.items():
            path = self.model_dir / f'{name}_scaler.pkl'
            with open(path, 'wb') as f:
                pickle.dump(scaler, f)
            logger.info(f"Saved scaler: {path}")
    
    def save_encoders(self):
        """Save all encoders"""
        for name, encoder in self.encoders.items():
            path = self.model_dir / f'{name}_encoder.pkl'
            with open(path, 'wb') as f:
                pickle.dump(encoder, f)
            logger.info(f"Saved encoder: {path}")
    
    def generate_summary(self):
        """Generate training summary"""
        logger.info("\n" + "=" * 60)
        logger.info("MODEL TRAINING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Models trained: {len(self.models)}")
        for name in self.models.keys():
            logger.info(f"  ✓ {name.title()}")
        logger.info(f"\nModels saved to: {self.model_dir}")
        logger.info("=" * 60)


def main():
    """Main training pipeline"""
    logger.info("=" * 60)
    logger.info("EDUTRACK ML MODEL TRAINING PIPELINE")
    logger.info("=" * 60)
    
    trainer = ModelTrainer()
    
    # Load data
    df = trainer.load_data("data/processed/college_data_features.csv")
    
    # Train Risk Classification Model
    X_risk, y_risk, risk_features = trainer.prepare_risk_classification(df)
    risk_model, risk_scaler = trainer.train_risk_model(X_risk, y_risk, risk_features)
    
    # Train Performance Classification Model
    X_perf, y_perf, perf_features = trainer.prepare_performance_classification(df)
    perf_model, perf_scaler = trainer.train_performance_model(X_perf, y_perf, perf_features)
    
    # Train Anomaly Detection Model
    X_anomaly, _, anomaly_features = trainer.prepare_risk_classification(df)
    anomaly_model, anomaly_scaler = trainer.train_anomaly_detector(X_anomaly, anomaly_features)
    
    # Save all models
    trainer.save_scalers()
    trainer.save_encoders()
    trainer.generate_summary()
    
    logger.info("\n✓ All models trained successfully!")
    return trainer


if __name__ == "__main__":
    trainer = main()
