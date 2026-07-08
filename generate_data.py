import pandas as pd
import numpy as np

def prepare_data(input_file='college_data_v3.csv', output_file='college_data.csv'):
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)

    # 1. Standardize column names
    df = df.rename(columns={'Total Student Enrollments': 'Total_Students', 'Total Faculty': 'Total_Faculty'})

    # 2. Extract numeric Infrastructure Area
    df['Infrastructure_Area'] = df['Campus Size'].str.extract('(\d+)').astype(float)
    
    # 3. Clean numeric columns
    df['Total_Students'] = pd.to_numeric(df['Total_Students'], errors='coerce')
    df['Total_Faculty'] = pd.to_numeric(df['Total_Faculty'], errors='coerce')

    # 4. Fill missing values
    df['Total_Students'] = df['Total_Students'].fillna(df['Total_Students'].median())
    df['Total_Faculty'] = df['Total_Faculty'].fillna(df['Total_Faculty'].median())
    df['Infrastructure_Area'] = df['Infrastructure_Area'].fillna(df['Infrastructure_Area'].median())

    # 5. Generate Metrics including DSS and Missing Doc Count
    def apply_logic(row):
        name = str(row['College Name']).lower()
        is_tier_1 = 'indian institute of technology' in name or 'national institute' in name
        
        if is_tier_1:
            placement, funds = np.random.uniform(92, 99), np.random.uniform(90, 100)
            avg_dss, missing_docs = np.random.uniform(90, 100), 0
        else:
            placement, funds = np.random.uniform(40, 80), np.random.uniform(50, 85)
            avg_dss = np.random.uniform(40, 85)
            # Randomly assign 0-2 missing documents
            missing_docs = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
            
        return pd.Series([placement, funds, avg_dss, missing_docs])

    df[['Placement_Rate', 'Fund_Utilization', 'Avg_Doc_DSS', 'Missing_Doc_Count']] = df.apply(apply_logic, axis=1)

    df.to_csv(output_file, index=False)
    print(f"✅ Created {output_file} with Avg_Doc_DSS and Missing_Doc_Count.")

if __name__ == "__main__":
    prepare_data()