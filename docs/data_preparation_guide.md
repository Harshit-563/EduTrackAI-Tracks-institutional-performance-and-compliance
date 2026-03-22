# EduTrack Data Preparation & Analytics Guide

## 📊 Overview

This document outlines the complete data preparation and analytics workflow for the EduTrack institutional evaluation system.

---

## 🎯 Objectives

1. **Load & Validate** - Import institutional data and assess quality
2. **Clean & Normalize** - Fix issues and standardize formats
3. **Engineer Features** - Create new predictive features
4. **Analyze & Explore** - Generate insights from data
5. **Score Institutions** - Calculate performance and risk metrics
6. **Generate Reports** - Produce actionable outputs

---

## 📁 Data Directory Structure

```
data/
├── raw/
│   ├── college_data.csv              # Original dataset
│   └── (other raw data files)
├── processed/
│   ├── college_data_cleaned.csv      # After cleaning
│   ├── college_data_features.csv     # With engineered features
│   └── college_data_analysis.csv     # Final analysis dataset
└── external/
    └── (reference data)
```

---

## 🔄 Data Processing Pipeline

### Step 1: Load Data

**Location**: `src/data_processing/loader.py`

**Purpose**: Load and validate institutional data

**Key Functions**:
- `DataLoader.load_csv()` - Load CSV with encoding detection
- `DataLoader.load_college_data()` - Load main dataset
- `DataLoader.validate_data()` - Check data quality
- `DataLoader.get_data_summary()` - Get statistical summary

**Usage**:
```python
from src.data_processing.loader import load_college_data

df = load_college_data("data/raw/college_data.csv")
```

---

### Step 2: Clean Data

**Location**: `src/data_processing/cleaner.py`

**Purpose**: Clean, normalize, and fix data issues

**Key Functions**:
- `DataCleaner.clean_dataframe()` - Full cleaning pipeline
- `_remove_duplicates()` - Remove duplicate records
- `_handle_missing_values()` - Fill NaN intelligently
- `_clean_text_columns()` - Normalize text
- `_normalize_numeric_columns()` - Fix numeric ranges
- `_fix_data_types()` - Optimize data types

**Cleaning Steps**:
1. Remove duplicate college records
2. Fill missing numeric values with median
3. Fill missing text values with 'Unknown'
4. Strip whitespace and standardize case
5. Cap percentage columns to 0-100
6. Convert to appropriate data types

**Usage**:
```python
from src.data_processing.cleaner import clean_college_data

df_cleaned = clean_college_data(df_raw)
```

---

### Step 3: Engineer Features

**Location**: `src/data_processing/transformer.py`

**Purpose**: Create new, predictive features

**New Features Created**:

#### Educational Metrics
- `Student_Faculty_Ratio` - Raw ratio of students to faculty
- `Faculty_Adequacy` - Scored faculty quality (0-100)
- `Placement_Category` - Categorical placement quality

#### Infrastructure Metrics
- `Infrastructure_Per_Student` - Campus area per student (sqm)
- `Infrastructure_Quality` - Scored infrastructure (0-100)

#### Financial Metrics
- `Financial_Efficiency` - Fund utilization score (0-100)
- `Fee_Category` - Categorical fee levels

#### Compliance Metrics
- `DSS_Category` - Document sufficiency category
- `Document_Completeness_Pct` - Percentage of docs present (0-100)
- `High_Compliance_Risk` - Binary risk flag

#### Overall Score
- `Overall_Performance_Score` - Weighted institutional score (0-100)

**Weights in Overall Score**:
- Placement Rate: 25%
- Faculty Adequacy: 20%
- Infrastructure Quality: 20%
- Financial Efficiency: 15%
- Compliance (DSS): 20%

**Usage**:
```python
from src.data_processing.transformer import engineer_features

df_features = engineer_features(df_cleaned)
```

---

## 📊 Notebooks

### Notebook 1: Data Cleaning (`01_data_cleaning.ipynb`)

**Content**:
- Data loading and exploration
- Missing value analysis
- Data quality assessment
- Cleaning and normalization
- Before/after comparison

**Output**:
- `data/processed/college_data_cleaned.csv`

---

### Notebook 2: Exploratory Analysis (`02_exploratory_analysis.ipynb`)

**Content**:
- Distribution analysis
- Correlation heatmaps
- Placement rate patterns
- Student-faculty ratio insights
- Infrastructure analysis
- Compliance trends
- Geographic distribution
- Key findings and recommendations

**Visualizations**:
- Histograms and box plots
- Scatter plots with trend lines
- Heatmaps and bar charts
- Correlation matrices

---

### Notebook 3: Feature Engineering (`03_feature_engineering.ipynb`)

**Content**:
- Feature creation and validation
- Student-faculty ratio analysis
- Infrastructure quality scoring
- Compliance risk assessment
- Overall performance scoring
- Feature importance analysis
- Top/bottom performer identification

**Output**:
- `data/processed/college_data_features.csv`

---

## 🚀 Running the Pipeline

### Option 1: Complete Pipeline Script

```bash
cd c:\edutech
python scripts/data_preparation_pipeline.py
```

**Output**:
- Logs all steps and metrics
- Creates cleaned dataset
- Creates featured dataset
- Generates institutional scores
- Generates risk assessment

---

### Option 2: Jupyter Notebooks

Run sequentially:
1. `notebooks/01_data_cleaning.ipynb`
2. `notebooks/02_exploratory_analysis.ipynb`
3. `notebooks/03_feature_engineering.ipynb`

---

## 📈 Key Metrics & Thresholds

### Placement Rate
- **Good**: ≥ 75%
- **Average**: 60-74%
- **Poor**: < 60%

### Document Sufficiency Score (DSS)
- **Excellent**: 85-100
- **Good**: 70-84
- **Fair**: 55-69
- **Poor**: 40-54
- **Critical**: < 40

### Student-Faculty Ratio
- **Excellent**: 15-25:1
- **Good**: 25-35:1
- **Acceptable**: 35-50:1
- **Poor**: > 50:1

### Infrastructure per Student
- **Excellent**: ≥ 5 sqm
- **Good**: 3-5 sqm
- **Acceptable**: 2-3 sqm
- **Poor**: 1-2 sqm
- **Critical**: < 1 sqm

### Fund Utilization
- **Excellent**: ≥ 90%
- **Good**: 75-89%
- **Acceptable**: 60-74%
- **Poor**: < 60%

---

## 🔍 Data Quality Checks

| Check | Status | Details |
|-------|--------|---------|
| Missing Values | ✓ | Filled with median/Unknown |
| Duplicates | ✓ | Removed based on College Name |
| Outliers | ✓ | Capped to valid ranges |
| Data Types | ✓ | Optimized for memory |
| Consistency | ✓ | Validated cross-columns |

---

## 📋 Output Files

### Processed Data
- `college_data_cleaned.csv` - Cleaned records
- `college_data_features.csv` - With engineered features

### Analysis Outputs
- `institutional_scores.csv` - Ranked scores
- `risk_assessment.csv` - Risk flags

---

## 🎓 Usage Examples

### Load and Analyze

```python
import pandas as pd
from src.data_processing.loader import DataLoader
from src.data_processing.cleaner import DataCleaner
from src.data_processing.transformer import FeatureEngineer

# Load
loader = DataLoader()
df = loader.load_college_data()

# Clean
cleaner = DataCleaner()
df_clean = cleaner.clean_dataframe(df)

# Engineer
engineer = FeatureEngineer()
df_features = engineer.engineer_features(df_clean)

# Use features
high_performers = df_features[df_features['Overall_Performance_Score'] > 80]
risk_institutions = df_features[df_features['High_Compliance_Risk'] == 1]
```

---

## 🐛 Troubleshooting

### Issue: File not found
**Solution**: Ensure data file is in `data/raw/` directory

### Issue: Missing values persist
**Solution**: Check data source or adjust handling logic in `cleaner.py`

### Issue: Feature values out of range
**Solution**: Verify normalization logic in `transformer.py`

---

## 📚 References

- [Data Dictionary](../docs/data_dictionary.md)
- [System Architecture](../docs/system_architecture.md)
- [ML Models Documentation](../docs/ml_models.md)

---

## 📞 Support

For issues or questions:
1. Check notebook outputs
2. Review logs in terminal
3. Consult documentation
4. Run validation checks

---

**Last Updated**: March 22, 2026  
**Version**: 1.0.0
