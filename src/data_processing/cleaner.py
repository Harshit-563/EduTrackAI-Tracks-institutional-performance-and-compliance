"""
Data Cleaning Module
Handles data cleaning, normalization, and preprocessing
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class DataCleaner:
    """Clean and preprocess institutional data"""
    
    def __init__(self):
        """Initialize Data Cleaner"""
        self.cleaning_report = {}
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Comprehensive data cleaning pipeline
        
        Args:
            df: Raw DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        logger.info("Starting data cleaning pipeline...")
        df_cleaned = df.copy()
        
        # Step 1: Remove duplicates
        df_cleaned = self._remove_duplicates(df_cleaned)
        
        # Step 2: Handle missing values
        df_cleaned = self._handle_missing_values(df_cleaned)
        
        # Step 3: Clean text columns
        df_cleaned = self._clean_text_columns(df_cleaned)
        
        # Step 4: Normalize numeric columns
        df_cleaned = self._normalize_numeric_columns(df_cleaned)
        
        # Step 5: Fix data types
        df_cleaned = self._fix_data_types(df_cleaned)
        
        logger.info(f"✓ Cleaning complete. Shape: {df_cleaned.shape}")
        return df_cleaned
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows"""
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=['College Name'], keep='first')
        removed = initial_count - len(df_clean)
        
        if removed > 0:
            logger.info(f"Removed {removed} duplicate records")
            self.cleaning_report['duplicates_removed'] = removed
        
        return df_clean
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values intelligently"""
        df_clean = df.copy()
        
        # Numeric columns: fill with median
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            missing_count = df_clean[col].isnull().sum()
            if missing_count > 0:
                median_val = df_clean[col].median()
                df_clean[col].fillna(median_val, inplace=True)
                logger.info(f"Filled {missing_count} missing values in '{col}' with median")
        
        # Text columns: fill with 'Unknown'
        text_cols = df_clean.select_dtypes(include=['object']).columns
        for col in text_cols:
            missing_count = df_clean[col].isnull().sum()
            if missing_count > 0:
                df_clean[col].fillna('Unknown', inplace=True)
                logger.info(f"Filled {missing_count} missing values in '{col}' with 'Unknown'")
        
        return df_clean
    
    def _clean_text_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize text columns"""
        text_cols = df.select_dtypes(include=['object']).columns
        df_clean = df.copy()
        
        for col in text_cols:
            # Strip whitespace
            df_clean[col] = df_clean[col].astype(str).str.strip()
            
            # Title case for college names and similar
            if 'name' in col.lower() or 'city' in col.lower():
                df_clean[col] = df_clean[col].str.title()
        
        logger.info(f"Cleaned {len(text_cols)} text columns")
        return df_clean
    
    def _normalize_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize and fix numeric columns"""
        df_clean = df.copy()
        
        # Known percentage columns (should be 0-100)
        percentage_cols = [
            'Placement_Rate', 'Fund_Utilization', 'Avg_Doc_DSS'
        ]
        
        for col in percentage_cols:
            if col in df_clean.columns:
                # Cap values to 0-100 range
                df_clean[col] = df_clean[col].clip(0, 100)
                
                # Check for outliers
                outliers = (df_clean[col] < 0) | (df_clean[col] > 100)
                if outliers.any():
                    logger.warning(f"Fixed {outliers.sum()} outliers in '{col}'")
        
        # Student/Faculty counts should be positive
        count_cols = ['Total_Students', 'Total_Faculty']
        for col in count_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].clip(lower=0)
                df_clean[col] = df_clean[col].astype('Int64')  # Nullable integer
        
        logger.info("Normalized numeric columns")
        return df_clean
    
    def _fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix and optimize data types"""
        df_clean = df.copy()
        
        type_mapping = {
            'College Name': 'string',
            'City': 'string',
            'State': 'string',
            'Country': 'string',
            'University': 'string',
            'College Type': 'category',
            'Genders Accepted': 'category',
            'Established Year': 'Int64',
            'Total_Students': 'Int64',
            'Total_Faculty': 'Int64',
            'Infrastructure_Area': 'float64',
            'Placement_Rate': 'float64',
            'Fund_Utilization': 'float64',
            'Avg_Doc_DSS': 'float64',
            'Missing_Doc_Count': 'Int64',
            'Average Fees': 'float64',
            'Rating': 'float64'
        }
        
        for col, dtype in type_mapping.items():
            if col in df_clean.columns:
                try:
                    df_clean[col] = df_clean[col].astype(dtype)
                except Exception as e:
                    logger.warning(f"Could not convert '{col}' to {dtype}: {e}")
        
        logger.info("Fixed data types")
        return df_clean
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """Get cleaning summary report"""
        return self.cleaning_report


# =====================================================
# STANDALONE FUNCTIONS
# =====================================================

def clean_college_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standalone function to clean data"""
    cleaner = DataCleaner()
    return cleaner.clean_dataframe(df)
