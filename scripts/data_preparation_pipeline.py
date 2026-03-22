"""
Complete Data Preparation Pipeline
Loads, cleans, engineers features, and generates analysis for EduTrack
"""

import sys
from pathlib import Path
import logging
import pandas as pd

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from src.data_processing.loader import DataLoader
from src.data_processing.cleaner import DataCleaner
from src.data_processing.transformer import FeatureEngineer


def run_pipeline(input_file: str = "data/raw/college_data.csv",
                 output_dir: str = "data/processed") -> pd.DataFrame:
    """
    Run complete data preparation pipeline
    
    Args:
        input_file: Path to raw CSV file
        output_dir: Directory for processed outputs
    
    Returns:
        Final DataFrame with engineered features
    """
    
    logger.info("="*60)
    logger.info("EDUTRACK DATA PREPARATION PIPELINE")
    logger.info("="*60)
    
    # =====================================================
    # STEP 1: LOAD DATA
    # =====================================================
    logger.info("\n[STEP 1] LOADING DATA...")
    
    try:
        loader = DataLoader(data_dir=str(Path(input_file).parent))
        df_raw = pd.read_csv(input_file)
        logger.info(f"✓ Loaded {len(df_raw)} records with {len(df_raw.columns)} columns")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return None
    
    # Validate
    is_valid, issues = loader.validate_data(df_raw)
    if issues:
        logger.warning(f"Data quality issues found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    
    # =====================================================
    # STEP 2: CLEAN DATA
    # =====================================================
    logger.info("\n[STEP 2] CLEANING DATA...")
    
    cleaner = DataCleaner()
    df_cleaned = cleaner.clean_dataframe(df_raw)
    
    logger.info(f"✓ Data cleaned")
    logger.info(f"  Original Shape: {df_raw.shape}")
    logger.info(f"  Cleaned Shape: {df_cleaned.shape}")
    
    # Save cleaned data
    cleaned_output = Path(output_dir) / "college_data_cleaned.csv"
    cleaned_output.parent.mkdir(parents=True, exist_ok=True)
    df_cleaned.to_csv(cleaned_output, index=False)
    logger.info(f"✓ Saved cleaned data: {cleaned_output}")
    
    # =====================================================
    # STEP 3: ENGINEER FEATURES
    # =====================================================
    logger.info("\n[STEP 3] ENGINEERING FEATURES...")
    
    engineer = FeatureEngineer()
    df_features = engineer.engineer_features(df_cleaned)
    
    logger.info(f"✓ Features engineered")
    logger.info(f"  New features created: {len(engineer.new_features)}")
    logger.info(f"  Final Shape: {df_features.shape}")
    
    # Log new features
    logger.info("  Features added:")
    for feature in engineer.new_features:
        logger.info(f"    - {feature}")
    
    # Save featured data
    features_output = Path(output_dir) / "college_data_features.csv"
    df_features.to_csv(features_output, index=False)
    logger.info(f"✓ Saved featured data: {features_output}")
    
    # =====================================================
    # STEP 4: GENERATE SUMMARY STATISTICS
    # =====================================================
    logger.info("\n[STEP 4] GENERATING SUMMARY STATISTICS...")
    
    summary_stats = {
        'Total Institutions': len(df_features),
        'Avg Placement Rate': f"{df_features['Placement_Rate'].mean():.2f}%",
        'Avg Document Sufficiency Score': f"{df_features['Avg_Doc_DSS'].mean():.2f}",
        'Avg Fund Utilization': f"{df_features['Fund_Utilization'].mean():.2f}%",
        'Avg Infrastructure per Student': f"{df_features.get('Infrastructure_Per_Student', pd.Series([0])).mean():.2f} sqm",
        'Avg Overall Performance Score': f"{df_features.get('Overall_Performance_Score', pd.Series([0])).mean():.2f}",
        'High Risk Institutions': (df_features['Avg_Doc_DSS'] < 50).sum(),
        'Low Placement Institutions': (df_features['Placement_Rate'] < 50).sum(),
    }
    
    for key, value in summary_stats.items():
        logger.info(f"  {key}: {value}")
    
    # =====================================================
    # STEP 5: DATA QUALITY REPORT
    # =====================================================
    logger.info("\n[STEP 5] DATA QUALITY REPORT...")
    
    missing_data = df_features.isnull().sum()
    if missing_data.sum() == 0:
        logger.info("✓ No missing values detected")
    else:
        logger.warning(f"Missing values found in {(missing_data > 0).sum()} columns")
    
    # =====================================================
    # COMPLETION
    # =====================================================
    logger.info("\n" + "="*60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("="*60)
    logger.info(f"Output Directory: {output_dir}")
    logger.info(f"Files Generated:")
    logger.info(f"  1. college_data_cleaned.csv")
    logger.info(f"  2. college_data_features.csv")
    logger.info("="*60 + "\n")
    
    return df_features


def generate_analysis_report(df: pd.DataFrame, output_dir: str = "outputs/analysis") -> None:
    """Generate detailed analysis report"""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Generating analysis report to {output_path}...")
    
    # Institutional summary
    summary = pd.DataFrame({
        'College Name': df['College Name'],
        'Overall_Performance_Score': df.get('Overall_Performance_Score', 0),
        'Placement_Rate': df['Placement_Rate'],
        'Avg_Doc_DSS': df['Avg_Doc_DSS'],
        'Fund_Utilization': df['Fund_Utilization'],
        'Infrastructure_Quality': df.get('Infrastructure_Quality', 0),
    }).sort_values('Overall_Performance_Score', ascending=False)
    
    summary.to_csv(output_path / "institutional_scores.csv", index=False)
    logger.info(f"✓ Saved institutional scores")
    
    # Risk assessment
    risk_report = pd.DataFrame({
        'College Name': df['College Name'],
        'DSS': df['Avg_Doc_DSS'],
        'High_Compliance_Risk': df.get('High_Compliance_Risk', 0),
        'Missing_Docs': df['Missing_Doc_Count'],
        'Placement_Rate': df['Placement_Rate'],
    }).sort_values('DSS')
    
    risk_report.to_csv(output_path / "risk_assessment.csv", index=False)
    logger.info(f"✓ Saved risk assessment")


if __name__ == "__main__":
    # Run pipeline
    df_final = run_pipeline(
        input_file="data/raw/college_data.csv",
        output_dir="data/processed"
    )
    
    # Generate analysis
    if df_final is not None:
        generate_analysis_report(df_final)
        logger.info("✓ All tasks completed successfully!")
