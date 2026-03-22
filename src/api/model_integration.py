"""
EduTrack API Model Integration
- Loads trained ML models
- Provides prediction functions for API endpoints
- Handles real-time scoring and risk assessment
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelPredictor:
    """Load and use trained ML models for predictions"""
    
    def __init__(self, model_dir: str = "models/trained_models"):
        self.model_dir = Path(model_dir)
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        logger.info("Loading trained models...")
        
        try:
            # Load risk model
            with open(self.model_dir / 'risk_model.pkl', 'rb') as f:
                self.models['risk'] = pickle.load(f)
            logger.info("✓ Risk model loaded")
        except FileNotFoundError:
            logger.warning("Risk model not found")
        
        try:
            # Load performance model
            with open(self.model_dir / 'performance_model.pkl', 'rb') as f:
                self.models['performance'] = pickle.load(f)
            logger.info("✓ Performance model loaded")
        except FileNotFoundError:
            logger.warning("Performance model not found")
        
        try:
            # Load anomaly model
            with open(self.model_dir / 'anomaly_model.pkl', 'rb') as f:
                self.models['anomaly'] = pickle.load(f)
            logger.info("✓ Anomaly model loaded")
        except FileNotFoundError:
            logger.warning("Anomaly model not found")
        
        # Load scalers
        for scaler_type in ['risk', 'performance', 'anomaly']:
            try:
                with open(self.model_dir / f'{scaler_type}_scaler.pkl', 'rb') as f:
                    self.scalers[scaler_type] = pickle.load(f)
            except FileNotFoundError:
                logger.warning(f"{scaler_type} scaler not found")
        
        # Load encoders
        try:
            with open(self.model_dir / 'performance_encoder.pkl', 'rb') as f:
                self.encoders['performance'] = pickle.load(f)
        except FileNotFoundError:
            logger.warning("Performance encoder not found")
    
    def predict_risk_level(self, features_dict: Dict) -> Dict:
        """
        Predict institutional risk level
        
        Args:
            features_dict: Dict with institution metrics
            
        Returns:
            Dict with risk prediction and confidence
        """
        if 'risk' not in self.models:
            return {'error': 'Risk model not available'}
        
        try:
            feature_cols = [
                'Student_Faculty_Ratio', 'Faculty_Adequacy',
                'Placement_Rate', 'Infrastructure_Quality',
                'Financial_Efficiency', 'Fund_Utilization',
                'Avg_Doc_DSS', 'Missing_Doc_Count',
                'Total_Students', 'Total_Faculty'
            ]
            
            # Extract features
            X = np.array([features_dict.get(col, 0) for col in feature_cols]).reshape(1, -1)
            
            # Scale
            X_scaled = self.scalers['risk'].transform(X)
            
            # Predict
            prediction = self.models['risk'].predict(X_scaled)[0]
            probability = self.models['risk'].predict_proba(X_scaled)[0]
            
            risk_level = 'High Risk' if prediction == 1 else 'Low Risk'
            confidence = max(probability) * 100
            
            return {
                'risk_level': risk_level,
                'risk_probability': float(probability[1]),
                'confidence': confidence,
                'prediction': int(prediction)
            }
        except Exception as e:
            logger.error(f"Risk prediction error: {str(e)}")
            return {'error': str(e)}
    
    def predict_performance_tier(self, features_dict: Dict) -> Dict:
        """
        Predict institutional performance tier
        
        Args:
            features_dict: Dict with institution metrics
            
        Returns:
            Dict with performance tier prediction
        """
        if 'performance' not in self.models:
            return {'error': 'Performance model not available'}
        
        try:
            feature_cols = [
                'Student_Faculty_Ratio', 'Faculty_Adequacy',
                'Placement_Rate', 'Infrastructure_Quality',
                'Financial_Efficiency', 'Fund_Utilization',
                'Avg_Doc_DSS', 'Missing_Doc_Count',
                'Total_Students', 'Total_Faculty'
            ]
            
            # Extract features
            X = np.array([features_dict.get(col, 0) for col in feature_cols]).reshape(1, -1)
            
            # Scale
            X_scaled = self.scalers['performance'].transform(X)
            
            # Predict
            prediction = self.models['performance'].predict(X_scaled)[0]
            probability = self.models['performance'].predict_proba(X_scaled)[0]
            
            # Decode
            encoder = self.encoders.get('performance')
            if encoder:
                tier = encoder.inverse_transform([prediction])[0]
            else:
                tier = str(prediction)
            
            confidence = max(probability) * 100
            
            return {
                'performance_tier': tier,
                'confidence': confidence,
                'probabilities': {
                    encoder.inverse_transform([i])[0]: float(prob)
                    for i, prob in enumerate(probability)
                } if encoder else {}
            }
        except Exception as e:
            logger.error(f"Performance prediction error: {str(e)}")
            return {'error': str(e)}
    
    def detect_anomalies(self, features_dict: Dict) -> Dict:
        """
        Detect if institution is anomalous
        
        Args:
            features_dict: Dict with institution metrics
            
        Returns:
            Dict with anomaly detection result
        """
        if 'anomaly' not in self.models:
            return {'error': 'Anomaly model not available'}
        
        try:
            feature_cols = [
                'Student_Faculty_Ratio', 'Faculty_Adequacy',
                'Placement_Rate', 'Infrastructure_Quality',
                'Financial_Efficiency', 'Fund_Utilization',
                'Avg_Doc_DSS', 'Missing_Doc_Count',
                'Total_Students', 'Total_Faculty'
            ]
            
            # Extract features
            X = np.array([features_dict.get(col, 0) for col in feature_cols]).reshape(1, -1)
            
            # Scale
            X_scaled = self.scalers['anomaly'].transform(X)
            
            # Predict
            prediction = self.models['anomaly'].predict(X_scaled)[0]
            is_anomaly = prediction == -1
            
            return {
                'is_anomaly': bool(is_anomaly),
                'anomaly_score': float(self.models['anomaly'].score_samples(X_scaled)[0]),
                'status': 'Anomalous' if is_anomaly else 'Normal'
            }
        except Exception as e:
            logger.error(f"Anomaly detection error: {str(e)}")
            return {'error': str(e)}
    
    def predict_all(self, features_dict: Dict) -> Dict:
        """
        Make all predictions for an institution
        
        Args:
            features_dict: Dict with institution metrics
            
        Returns:
            Dict with all predictions
        """
        return {
            'risk_assessment': self.predict_risk_level(features_dict),
            'performance_tier': self.predict_performance_tier(features_dict),
            'anomaly_detection': self.detect_anomalies(features_dict)
        }


class InstitutionScorer:
    """Score institutions using all available metrics"""
    
    def __init__(self, model_predictor: ModelPredictor):
        self.predictor = model_predictor
    
    def calculate_comprehensive_score(self, row: pd.Series) -> Dict:
        """
        Calculate comprehensive institutional score
        
        Args:
            row: Pandas Series with institution data
            
        Returns:
            Dict with comprehensive scoring
        """
        features_dict = row.to_dict()
        
        # Get ML predictions
        predictions = self.predictor.predict_all(features_dict)
        
        # Component scores (0-100)
        score_components = {
            'placement_score': row.get('Placement_Rate', 0),
            'faculty_score': row.get('Faculty_Adequacy', 0),
            'infrastructure_score': row.get('Infrastructure_Quality', 0),
            'financial_score': row.get('Financial_Efficiency', 0),
            'compliance_score': row.get('Avg_Doc_DSS', 0),
            'overall_performance_score': row.get('Overall_Performance_Score', 0)
        }
        
        # Create comprehensive report
        report = {
            'metrics': score_components,
            'predictions': predictions,
            'risk_level': predictions.get('risk_assessment', {}).get('risk_level', 'Unknown'),
            'performance_tier': predictions.get('performance_tier', {}).get('performance_tier', 'Unknown'),
            'is_anomalous': predictions.get('anomaly_detection', {}).get('is_anomaly', False),
            'overall_score': score_components.get('overall_performance_score', 0)
        }
        
        return report
    
    def batch_score_institutions(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score multiple institutions
        
        Args:
            df: DataFrame with institution data
            
        Returns:
            DataFrame with scoring results
        """
        results = []
        
        for idx, row in df.iterrows():
            try:
                score_report = self.calculate_comprehensive_score(row)
                score_report['college_name'] = row.get('College Name', 'Unknown')
                results.append(score_report)
            except Exception as e:
                logger.error(f"Error scoring institution {idx}: {str(e)}")
        
        return pd.DataFrame(results)


def test_models():
    """Test model loading and prediction"""
    logger.info("\n" + "=" * 60)
    logger.info("TESTING MODEL INTEGRATION")
    logger.info("=" * 60)
    
    # Load predictor
    predictor = ModelPredictor()
    
    # Test features
    test_features = {
        'Student_Faculty_Ratio': 25.0,
        'Faculty_Adequacy': 75.0,
        'Placement_Rate': 85.0,
        'Infrastructure_Quality': 75.0,
        'Financial_Efficiency': 80.0,
        'Fund_Utilization': 85.0,
        'Avg_Doc_DSS': 80.0,
        'Missing_Doc_Count': 0,
        'Total_Students': 1000,
        'Total_Faculty': 40
    }
    
    logger.info("\nTest Institution Features:")
    for key, val in test_features.items():
        logger.info(f"  {key}: {val}")
    
    # Make predictions
    logger.info("\n[RISK PREDICTION]")
    risk_pred = predictor.predict_risk_level(test_features)
    logger.info(f"  Result: {risk_pred}")
    
    logger.info("\n[PERFORMANCE PREDICTION]")
    perf_pred = predictor.predict_performance_tier(test_features)
    logger.info(f"  Result: {perf_pred}")
    
    logger.info("\n[ANOMALY DETECTION]")
    anomaly_pred = predictor.detect_anomalies(test_features)
    logger.info(f"  Result: {anomaly_pred}")
    
    logger.info("\n" + "=" * 60)
    logger.info("MODEL INTEGRATION TEST COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    test_models()
