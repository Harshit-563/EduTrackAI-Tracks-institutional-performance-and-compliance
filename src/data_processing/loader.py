"""
Data Loader Module
Handles loading, validating, and initial preprocessing of institutional data
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class DataLoader:
    """Load and validate institutional data"""
    
    def __init__(self, data_dir: str = "data/raw"):
        """
        Initialize Data Loader
        
        Args:
            data_dir: Directory containing raw data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_csv(
        self,
        filename: str,
        encoding: str = 'utf-8',
        dtype_dict: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Load CSV file with validation
        
        Args:
            filename: CSV filename
            encoding: File encoding
            dtype_dict: Data type mapping
        
        Returns:
            Loaded DataFrame
        """
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        logger.info(f"Loading: {filename}")
        
        try:
            df = pd.read_csv(filepath, encoding=encoding, dtype=dtype_dict)
            logger.info(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")
            return df
        
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            raise
    
    def load_college_data(self) -> pd.DataFrame:
        """Load institutional data with automatic type detection"""
        df = self.load_csv("college_data.csv")
        
        # Validate essential columns
        required_cols = [
            'College Name', 'Total_Students', 'Total_Faculty',
            'Infrastructure_Area', 'Placement_Rate', 'Fund_Utilization'
        ]
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing columns: {missing_cols}")
        
        return df
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, list]:
        """
        Validate data quality
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for duplicates
        if df.duplicated().any():
            dup_count = df.duplicated().sum()
            issues.append(f"Found {dup_count} duplicate rows")
        
        # Check for missing values
        missing = df.isnull().sum()
        if missing.any():
            for col, count in missing[missing > 0].items():
                pct = (count / len(df)) * 100
                issues.append(f"Column '{col}' has {count} missing values ({pct:.1f}%)")
        
        # Check numeric columns for negative values
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if (df[col] < 0).any():
                neg_count = (df[col] < 0).sum()
                issues.append(f"Column '{col}' has {neg_count} negative values")
        
        return len(issues) == 0, issues
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get data summary statistics"""
        return {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_count': df.isnull().sum().to_dict(),
            'duplicates': int(df.duplicated().sum()),
        }


# =====================================================
# STANDALONE FUNCTIONS
# =====================================================

def load_college_data(
    csv_path: str = "data/raw/college_data.csv"
) -> pd.DataFrame:
    """Standalone function to load college data"""
    loader = DataLoader()
    return loader.load_college_data()
