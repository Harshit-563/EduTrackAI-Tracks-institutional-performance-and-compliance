"""
Feature Engineering Module
Creates new features for analysis and modeling
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """Engineer and create new features"""
    
    def __init__(self):
        """Initialize Feature Engineer"""
        self.new_features = []
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all engineered features
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with new features
        """
        logger.info("Starting feature engineering...")
        df_features = df.copy()
        
        # Educational metrics
        df_features = self._create_educational_features(df_features)
        
        # Infrastructure metrics
        df_features = self._create_infrastructure_features(df_features)
        
        # Financial metrics
        df_features = self._create_financial_features(df_features)
        
        # Compliance metrics
        df_features = self._create_compliance_features(df_features)
        
        # Overall performance score
        df_features = self._create_performance_score(df_features)
        
        logger.info(f"✓ Created {len(self.new_features)} new features")
        return df_features
    
    def _create_educational_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create educational quality features"""
        df_feat = df.copy()
        
        # Student-Faculty Ratio
        if 'Total_Faculty' in df.columns and 'Total_Students' in df.columns:
            df_feat['Student_Faculty_Ratio'] = (
                df_feat['Total_Students'] / df_feat['Total_Faculty'].replace(0, 1)
            )
            self.new_features.append('Student_Faculty_Ratio')
            logger.info("Created: Student_Faculty_Ratio")
        
        # Faculty Adequacy Score (lower ratio is better, within reasonable bounds)
        if 'Student_Faculty_Ratio' in df_feat.columns:
            ratio = df_feat['Student_Faculty_Ratio']
            df_feat['Faculty_Adequacy'] = np.where(
                ratio <= 0,
                0,
                np.where(
                    ratio <= 30,
                    100 - (ratio / 30) * 20,  # 80-100 for good ratios
                    np.where(
                        ratio <= 50,
                        60 + ((50 - ratio) / 20) * 20,  # 60-80 for acceptable
                        np.maximum(0, 60 - ((ratio - 50) / 50) * 60)  # 0-60 for poor
                    )
                )
            )
            self.new_features.append('Faculty_Adequacy')
            logger.info("Created: Faculty_Adequacy")
        
        # Placement Performance Category
        if 'Placement_Rate' in df.columns:
            df_feat['Placement_Category'] = pd.cut(
                df_feat['Placement_Rate'],
                bins=[0, 40, 60, 75, 100],
                labels=['Poor', 'Average', 'Good', 'Excellent'],
                include_lowest=True
            )
            self.new_features.append('Placement_Category')
            logger.info("Created: Placement_Category")
        
        return df_feat
    
    def _create_infrastructure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create infrastructure quality features"""
        df_feat = df.copy()
        
        # Infrastructure per Student
        if 'Infrastructure_Area' in df.columns and 'Total_Students' in df.columns:
            df_feat['Infrastructure_Per_Student'] = (
                df_feat['Infrastructure_Area'] / df_feat['Total_Students'].replace(0, 1)
            )
            self.new_features.append('Infrastructure_Per_Student')
            logger.info("Created: Infrastructure_Per_Student")
        
        # Infrastructure Quality Score
        if 'Infrastructure_Per_Student' in df_feat.columns:
            area_per_student = df_feat['Infrastructure_Per_Student']
            df_feat['Infrastructure_Quality'] = np.where(
                area_per_student >= 5,
                100,  # Excellent (5+ sqm per student)
                np.where(
                    area_per_student >= 3,
                    80 + (area_per_student - 3) * 10,  # Good (3-5)
                    np.where(
                        area_per_student >= 2,
                        60 + (area_per_student - 2) * 20,  # Acceptable (2-3)
                        np.where(
                            area_per_student >= 1,
                            40 + area_per_student * 20,  # Poor (1-2)
                            20  # Critical (<1)
                        )
                    )
                )
            ).clip(0, 100)
            self.new_features.append('Infrastructure_Quality')
            logger.info("Created: Infrastructure_Quality")
        
        return df_feat
    
    def _create_financial_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create financial efficiency features"""
        df_feat = df.copy()
        
        # Financial Efficiency Score
        if 'Fund_Utilization' in df.columns:
            df_feat['Financial_Efficiency'] = df_feat['Fund_Utilization'].clip(0, 100)
            self.new_features.append('Financial_Efficiency')
            logger.info("Created: Financial_Efficiency")
        
        # Average Fees Category
        if 'Average Fees' in df.columns:
            # Convert to numeric, handling mixed types
            fees_numeric = pd.to_numeric(df_feat['Average Fees'], errors='coerce')
            # Fill NaN values with median
            fees_numeric.fillna(fees_numeric.median(), inplace=True)
            
            df_feat['Fee_Category'] = pd.cut(
                fees_numeric,
                bins=[0, 100000, 300000, 500000, float('inf')],
                labels=['Low', 'Medium', 'High', 'Premium'],
                include_lowest=True
            )
            self.new_features.append('Fee_Category')
            logger.info("Created: Fee_Category")
        
        return df_feat
    
    def _create_compliance_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create document compliance features"""
        df_feat = df.copy()
        
        # Document Sufficiency Score (DSS) Category
        if 'Avg_Doc_DSS' in df.columns:
            df_feat['DSS_Category'] = pd.cut(
                df_feat['Avg_Doc_DSS'],
                bins=[0, 40, 55, 70, 85, 100],
                labels=['Critical', 'Poor', 'Fair', 'Good', 'Excellent'],
                include_lowest=True
            )
            self.new_features.append('DSS_Category')
            logger.info("Created: DSS_Category")
        
        # Document Completeness Percentage
        if 'Avg_Doc_DSS' in df.columns and 'Missing_Doc_Count' in df.columns:
            # Assuming max 10 required documents
            max_docs = 10
            df_feat['Document_Completeness_Pct'] = (
                ((max_docs - df_feat['Missing_Doc_Count'].clip(upper=max_docs)) / max_docs * 100)
                .clip(0, 100)
            )
            self.new_features.append('Document_Completeness_Pct')
            logger.info("Created: Document_Completeness_Pct")
        
        # Compliance Risk Flag
        if 'Avg_Doc_DSS' in df.columns:
            df_feat['High_Compliance_Risk'] = (df_feat['Avg_Doc_DSS'] < 50).astype(int)
            self.new_features.append('High_Compliance_Risk')
            logger.info("Created: High_Compliance_Risk")
        
        return df_feat
    
    def _create_performance_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create overall institutional performance score"""
        df_feat = df.copy()
        
        components = []
        weights = {}
        
        # Collect performance components
        if 'Placement_Rate' in df_feat.columns:
            components.append(df_feat['Placement_Rate'].fillna(0))
            weights['placement'] = 0.25
        
        if 'Faculty_Adequacy' in df_feat.columns:
            components.append(df_feat['Faculty_Adequacy'].fillna(50))
            weights['faculty'] = 0.20
        
        if 'Infrastructure_Quality' in df_feat.columns:
            components.append(df_feat['Infrastructure_Quality'].fillna(50))
            weights['infrastructure'] = 0.20
        
        if 'Fund_Utilization' in df_feat.columns:
            components.append(df_feat['Fund_Utilization'].fillna(50))
            weights['financial'] = 0.15
        
        if 'Avg_Doc_DSS' in df_feat.columns:
            components.append(df_feat['Avg_Doc_DSS'].fillna(50))
            weights['compliance'] = 0.20
        
        # Calculate weighted average
        if components and weights:
            weight_values = list(weights.values())
            if sum(weight_values) > 0:
                normalized_weights = [w / sum(weight_values) for w in weight_values]
                
                score = sum(
                    comp * weight 
                    for comp, weight in zip(components, normalized_weights)
                ).clip(0, 100)
                
                df_feat['Overall_Performance_Score'] = score
                self.new_features.append('Overall_Performance_Score')
                logger.info("Created: Overall_Performance_Score")
        
        return df_feat
    
    def get_feature_summary(self) -> Dict[str, Any]:
        """Get feature engineering summary"""
        return {
            'features_created': self.new_features,
            'feature_count': len(self.new_features)
        }


# =====================================================
# STANDALONE FUNCTIONS
# =====================================================

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Standalone function to engineer features"""
    engineer = FeatureEngineer()
    return engineer.engineer_features(df)
