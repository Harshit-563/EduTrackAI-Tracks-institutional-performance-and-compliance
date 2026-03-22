"""
EduTrack Visualization Dashboard Generator
- Creates comprehensive visualizations for institutional analysis
- Generates performance dashboards and risk heatmaps
- Exports to HTML and PNG formats
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f8f9fa'


class DashboardGenerator:
    """Generate visualizations for EduTrack"""
    
    def __init__(self, output_dir: str = "outputs/visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self, features_file: str) -> pd.DataFrame:
        """Load featured data"""
        logger.info(f"Loading data from {features_file}")
        return pd.read_csv(features_file)
    
    def create_performance_distribution(self, df: pd.DataFrame):
        """Create performance score distribution visualization"""
        logger.info("[VIZ 1/6] Creating performance distribution...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Institutional Performance Distributions', fontsize=16, fontweight='bold')
        
        # Overall Performance Score
        axes[0, 0].hist(df['Overall_Performance_Score'], bins=40, color='#2E86AB', edgecolor='black', alpha=0.7)
        axes[0, 0].set_title('Overall Performance Score', fontweight='bold')
        axes[0, 0].set_xlabel('Score')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].axvline(df['Overall_Performance_Score'].mean(), color='red', linestyle='--', label='Mean')
        axes[0, 0].legend()
        
        # Placement Rate
        axes[0, 1].hist(df['Placement_Rate'], bins=40, color='#A23B72', edgecolor='black', alpha=0.7)
        axes[0, 1].set_title('Placement Rate (%)', fontweight='bold')
        axes[0, 1].set_xlabel('Rate')
        axes[0, 1].set_ylabel('Count')
        axes[0, 1].axvline(df['Placement_Rate'].mean(), color='red', linestyle='--', label='Mean')
        axes[0, 1].legend()
        
        # DSS Score
        axes[1, 0].hist(df['Avg_Doc_DSS'], bins=40, color='#F18F01', edgecolor='black', alpha=0.7)
        axes[1, 0].set_title('Document Sufficiency Score (DSS)', fontweight='bold')
        axes[1, 0].set_xlabel('DSS')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].axvline(df['Avg_Doc_DSS'].mean(), color='red', linestyle='--', label='Mean')
        axes[1, 0].legend()
        
        # Financial Efficiency
        axes[1, 1].hist(df['Financial_Efficiency'], bins=40, color='#C73E1D', edgecolor='black', alpha=0.7)
        axes[1, 1].set_title('Financial Efficiency (%)', fontweight='bold')
        axes[1, 1].set_xlabel('Efficiency')
        axes[1, 1].set_ylabel('Count')
        axes[1, 1].axvline(df['Financial_Efficiency'].mean(), color='red', linestyle='--', label='Mean')
        axes[1, 1].legend()
        
        plt.tight_layout()
        path = self.output_dir / '01_performance_distribution.png'
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {path}")
    
    def create_category_breakdown(self, df: pd.DataFrame):
        """Create category breakdown visualization"""
        logger.info("[VIZ 2/6] Creating category breakdown...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Institutional Category Breakdown', fontsize=16, fontweight='bold')
        
        # Placement Categories
        placement_counts = df['Placement_Category'].value_counts()
        colors_placement = ['#90BE6D', '#F9C74F', '#F8961E']
        axes[0, 0].bar(placement_counts.index, placement_counts.values, color=colors_placement, edgecolor='black')
        axes[0, 0].set_title('Placement Categories', fontweight='bold')
        axes[0, 0].set_ylabel('Count')
        for i, v in enumerate(placement_counts.values):
            pct = (v / len(df)) * 100
            axes[0, 0].text(i, v + 20, f'{v}\n({pct:.1f}%)', ha='center', fontweight='bold')
        
        # DSS Categories
        dss_counts = df['DSS_Category'].value_counts().sort_index()
        colors_dss = ['#E63946', '#F1FAEE', '#A8DADC', '#457B9D']
        axes[0, 1].bar(dss_counts.index, dss_counts.values, color=colors_dss[:len(dss_counts)], edgecolor='black')
        axes[0, 1].set_title('DSS Categories', fontweight='bold')
        axes[0, 1].set_ylabel('Count')
        for i, v in enumerate(dss_counts.values):
            pct = (v / len(df)) * 100
            axes[0, 1].text(i, v + 20, f'{v}\n({pct:.1f}%)', ha='center', fontweight='bold')
        plt.setp(axes[0, 1].xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Fee Categories
        fee_counts = df['Fee_Category'].value_counts()
        colors_fee = ['#264653', '#2A9D8F', '#E9C46A', '#F4A261']
        axes[1, 0].pie(fee_counts.values, labels=fee_counts.index, autopct='%1.1f%%', 
                       colors=colors_fee, startangle=90)
        axes[1, 0].set_title('Fee Categories\n(Pie Chart)', fontweight='bold')
        
        # Infrastructure Quality
        infra_counts = df['Infrastructure_Quality'].value_counts().sort_index()
        axes[1, 1].bar(range(len(infra_counts)), infra_counts.values, color='#457B9D', edgecolor='black')
        axes[1, 1].set_title('Infrastructure Quality Scores', fontweight='bold')
        axes[1, 1].set_ylabel('Count')
        axes[1, 1].set_xticks(range(len(infra_counts)))
        axes[1, 1].set_xticklabels([f'{x:.0f}' for x in infra_counts.index], rotation=45)
        
        plt.tight_layout()
        path = self.output_dir / '02_category_breakdown.png'
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {path}")
    
    def create_correlation_heatmap(self, df: pd.DataFrame):
        """Create correlation heatmap"""
        logger.info("[VIZ 3/6] Creating correlation heatmap...")
        
        # Select numeric columns
        numeric_cols = [
            'Overall_Performance_Score', 'Placement_Rate', 'Avg_Doc_DSS',
            'Student_Faculty_Ratio', 'Faculty_Adequacy', 'Infrastructure_Quality',
            'Financial_Efficiency', 'Fund_Utilization', 'Total_Students', 'Total_Faculty'
        ]
        
        corr_matrix = df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, ax=ax, cbar_kws={'label': 'Correlation'})
        ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        path = self.output_dir / '03_correlation_heatmap.png'
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {path}")
    
    def create_risk_analysis(self, df: pd.DataFrame):
        """Create risk analysis visualization"""
        logger.info("[VIZ 4/6] Creating risk analysis...")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Risk Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # Risk Distribution
        risk_counts = df['High_Compliance_Risk'].value_counts()
        colors = ['#06D6A0', '#EF476F']
        axes[0, 0].bar(['Low Risk', 'High Risk'], [risk_counts.get(0, 0), risk_counts.get(1, 0)], 
                      color=colors, edgecolor='black', width=0.5)
        axes[0, 0].set_title('Compliance Risk Distribution', fontweight='bold')
        axes[0, 0].set_ylabel('Count')
        for i, v in enumerate([risk_counts.get(0, 0), risk_counts.get(1, 0)]):
            pct = (v / len(df)) * 100
            axes[0, 0].text(i, v + 50, f'{v}\n({pct:.1f}%)', ha='center', fontweight='bold')
        
        # Performance vs DSS
        axes[0, 1].scatter(df['Overall_Performance_Score'], df['Avg_Doc_DSS'], 
                          alpha=0.5, s=30, c=df['Overall_Performance_Score'], cmap='viridis')
        axes[0, 1].set_xlabel('Overall Performance Score')
        axes[0, 1].set_ylabel('DSS')
        axes[0, 1].set_title('Performance Score vs DSS', fontweight='bold')
        
        # Placement Rate by Risk
        risk_labels = ['Low Risk', 'High Risk']
        placement_by_risk = [
            df[df['High_Compliance_Risk'] == 0]['Placement_Rate'].mean(),
            df[df['High_Compliance_Risk'] == 1]['Placement_Rate'].mean()
        ]
        axes[1, 0].bar(risk_labels, placement_by_risk, color=['#06D6A0', '#EF476F'], edgecolor='black')
        axes[1, 0].set_title('Avg Placement Rate by Risk Level', fontweight='bold')
        axes[1, 0].set_ylabel('Avg Placement Rate (%)')
        for i, v in enumerate(placement_by_risk):
            axes[1, 0].text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')
        
        # DSS Distribution by Risk
        df.boxplot(column='Avg_Doc_DSS', by='High_Compliance_Risk', ax=axes[1, 1])
        axes[1, 1].set_xlabel('Risk Level (0=Low, 1=High)')
        axes[1, 1].set_ylabel('DSS')
        axes[1, 1].set_title('DSS Distribution by Risk Level', fontweight='bold')
        plt.suptitle('')
        
        plt.tight_layout()
        path = self.output_dir / '04_risk_analysis.png'
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {path}")
    
    def create_top_performers(self, df: pd.DataFrame):
        """Create top performers visualization"""
        logger.info("[VIZ 5/6] Creating top performers...")
        
        # Get top 15 performers
        top_15 = df.nlargest(15, 'Overall_Performance_Score')[
            ['College Name', 'Overall_Performance_Score']
        ]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        y_pos = np.arange(len(top_15))
        scores = top_15['Overall_Performance_Score'].values
        colors_gradient = plt.cm.RdYlGn(scores / 100)
        
        ax.barh(y_pos, scores, color=colors_gradient, edgecolor='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels([name[:50] for name in top_15['College Name'].values], fontsize=9)
        ax.set_xlabel('Overall Performance Score', fontweight='bold')
        ax.set_title('Top 15 Performing Institutions', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 100)
        
        # Add score labels
        for i, score in enumerate(scores):
            ax.text(score + 1, i, f'{score:.1f}', va='center', fontweight='bold')
        
        plt.tight_layout()
        path = self.output_dir / '05_top_performers.png'
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {path}")
    
    def create_geographic_analysis(self, df: pd.DataFrame):
        """Create geographic analysis"""
        logger.info("[VIZ 6/6] Creating geographic analysis...")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Geographic Analysis', fontsize=16, fontweight='bold')
        
        # States with most institutions
        top_states = df['State'].value_counts().head(10)
        axes[0].barh(range(len(top_states)), top_states.values, color='#1F77B4', edgecolor='black')
        axes[0].set_yticks(range(len(top_states)))
        axes[0].set_yticklabels(top_states.index)
        axes[0].set_xlabel('Number of Institutions')
        axes[0].set_title('Top 10 States by Institution Count', fontweight='bold')
        axes[0].invert_yaxis()
        
        # Average performance by state (top 10)
        state_performance = df.groupby('State')['Overall_Performance_Score'].agg(['mean', 'count'])
        state_performance = state_performance.sort_values('mean', ascending=False).head(10)
        
        axes[1].barh(range(len(state_performance)), state_performance['mean'].values, 
                    color='#FF7F0E', edgecolor='black')
        axes[1].set_yticks(range(len(state_performance)))
        axes[1].set_yticklabels(state_performance.index)
        axes[1].set_xlabel('Avg Performance Score')
        axes[1].set_title('Top 10 States by Avg Performance', fontweight='bold')
        axes[1].invert_yaxis()
        
        plt.tight_layout()
        path = self.output_dir / '06_geographic_analysis.png'
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved: {path}")
    
    def create_all_dashboards(self, df: pd.DataFrame):
        """Generate all visualizations"""
        self.create_performance_distribution(df)
        self.create_category_breakdown(df)
        self.create_correlation_heatmap(df)
        self.create_risk_analysis(df)
        self.create_top_performers(df)
        self.create_geographic_analysis(df)
    
    def generate_summary(self):
        """Generate summary report"""
        logger.info("\n" + "=" * 60)
        logger.info("VISUALIZATION DASHBOARD SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Output Directory: {self.output_dir}")
        logger.info("\nDashboards Generated:")
        logger.info("  1. Performance Distributions (01_performance_distribution.png)")
        logger.info("  2. Category Breakdown (02_category_breakdown.png)")
        logger.info("  3. Correlation Heatmap (03_correlation_heatmap.png)")
        logger.info("  4. Risk Analysis (04_risk_analysis.png)")
        logger.info("  5. Top Performers (05_top_performers.png)")
        logger.info("  6. Geographic Analysis (06_geographic_analysis.png)")
        logger.info("=" * 60)


def main():
    """Main dashboard generation pipeline"""
    logger.info("=" * 60)
    logger.info("EDUTRACK VISUALIZATION DASHBOARD GENERATOR")
    logger.info("=" * 60)
    
    generator = DashboardGenerator()
    df = generator.load_data("data/processed/college_data_features.csv")
    
    logger.info(f"\nGenerating {6} comprehensive visualizations...\n")
    generator.create_all_dashboards(df)
    generator.generate_summary()
    
    logger.info("\n[SUCCESS] All dashboards created!")
    return generator


if __name__ == "__main__":
    main()
