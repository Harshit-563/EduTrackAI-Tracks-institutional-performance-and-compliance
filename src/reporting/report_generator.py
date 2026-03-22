"""
EduTrack Report Generator
- Creates comprehensive institutional evaluation reports
- Generates PDF, Excel, and HTML formats
- Includes scoring, risk assessment, and recommendations
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional
import json

# For PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generate comprehensive institutional reports"""
    
    def __init__(self, output_dir: str = "outputs/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self, features_file: str) -> pd.DataFrame:
        """Load featured data"""
        logger.info(f"Loading data from {features_file}")
        return pd.read_csv(features_file)
    
    def generate_executive_summary(self, institution: pd.Series) -> Dict:
        """Generate executive summary for institution"""
        summary = {
            'college_name': institution['College Name'],
            'state': institution['State'],
            'city': institution['City'],
            'college_type': institution['College Type'],
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'report_time': datetime.now().strftime('%H:%M:%S'),
            'metrics': {
                'total_students': int(float(institution['Total_Students'])) if pd.notna(institution['Total_Students']) else 0,
                'total_faculty': int(float(institution['Total_Faculty'])) if pd.notna(institution['Total_Faculty']) else 0,
                'student_faculty_ratio': round(float(institution['Student_Faculty_Ratio']), 2) if pd.notna(institution['Student_Faculty_Ratio']) else 0,
                'placement_rate': round(float(institution['Placement_Rate']), 2) if pd.notna(institution['Placement_Rate']) else 0,
                'average_fees': int(float(institution['Average Fees'])) if pd.notna(institution['Average Fees']) else 0,
                'fund_utilization': round(float(institution['Fund_Utilization']), 2) if pd.notna(institution['Fund_Utilization']) else 0,
                'infrastructure_area': round(float(institution['Infrastructure_Area']), 2) if pd.notna(institution['Infrastructure_Area']) else 0
            },
            'scores': {
                'overall_performance_score': round(institution['Overall_Performance_Score'], 2),
                'faculty_adequacy': round(institution['Faculty_Adequacy'], 2),
                'placement_category': institution['Placement_Category'],
                'infrastructure_quality': round(institution['Infrastructure_Quality'], 2),
                'financial_efficiency': round(institution['Financial_Efficiency'], 2),
                'avg_doc_dss': round(institution['Avg_Doc_DSS'], 2),
                'dss_category': institution['DSS_Category'],
                'document_completeness': round(institution['Document_Completeness_Pct'], 2)
            }
        }
        return summary
    
    def generate_risk_assessment(self, institution: pd.Series) -> Dict:
        """Generate risk assessment"""
        overall_score = institution['Overall_Performance_Score']
        dss_score = institution['Avg_Doc_DSS']
        placement_rate = institution['Placement_Rate']
        
        # Determine risk level
        if institution['High_Compliance_Risk'] == 1:
            risk_level = 'HIGH RISK'
            risk_color = 'Red'
        elif overall_score < 50 or dss_score < 50:
            risk_level = 'MEDIUM RISK'
            risk_color = 'Orange'
        else:
            risk_level = 'LOW RISK'
            risk_color = 'Green'
        
        # Generate recommendations
        recommendations = []
        if placement_rate < 60:
            recommendations.append("Improve placement rate (currently below 60%)")
        if dss_score < 60:
            recommendations.append("Enhance document completeness and compliance")
        if institution['Faculty_Adequacy'] < 60:
            recommendations.append("Optimize faculty-to-student ratio")
        if institution['Infrastructure_Quality'] < 60:
            recommendations.append("Upgrade infrastructure and facilities")
        if institution['Financial_Efficiency'] < 60:
            recommendations.append("Improve fund utilization efficiency")
        
        if not recommendations:
            recommendations.append("Institution performing well; maintain current trajectory")
        
        return {
            'risk_level': risk_level,
            'risk_color': risk_color,
            'overall_score': round(overall_score, 2),
            'compliance_risk': 'YES' if institution['High_Compliance_Risk'] == 1 else 'NO',
            'missing_documents': int(institution['Missing_Doc_Count']),
            'recommendations': recommendations
        }
    
    def generate_performance_analysis(self, institution: pd.Series, all_institutions: pd.DataFrame) -> Dict:
        """Generate performance analysis with benchmarks"""
        overall_score = institution['Overall_Performance_Score']
        placement_rate = institution['Placement_Rate']
        
        # Percentile rankings
        overall_percentile = (all_institutions['Overall_Performance_Score'] < overall_score).sum() / len(all_institutions) * 100
        placement_percentile = (all_institutions['Placement_Rate'] < placement_rate).sum() / len(all_institutions) * 100
        
        # State ranking
        state_institutions = all_institutions[all_institutions['State'] == institution['State']]
        state_rank = (state_institutions['Overall_Performance_Score'] < overall_score).sum() + 1
        
        return {
            'overall_performance_score': round(overall_score, 2),
            'placement_rate': round(placement_rate, 2),
            'percentile_overall': round(overall_percentile, 1),
            'percentile_placement': round(placement_percentile, 1),
            'state_rank': int(state_rank),
            'state_rank_total': len(state_institutions),
            'national_rank': (all_institutions['Overall_Performance_Score'] < overall_score).sum() + 1,
            'national_rank_total': len(all_institutions),
            'performance_trend': 'Stable'  # Would need historical data for real trend
        }
    
    def generate_detailed_metrics(self, institution: pd.Series) -> Dict:
        """Generate detailed metrics breakdown"""
        return {
            'academic_metrics': {
                'student_faculty_ratio': round(float(institution['Student_Faculty_Ratio']), 2) if pd.notna(institution['Student_Faculty_Ratio']) else 0,
                'faculty_adequacy_score': round(float(institution['Faculty_Adequacy']), 2) if pd.notna(institution['Faculty_Adequacy']) else 0,
                'total_students': int(float(institution['Total_Students'])) if pd.notna(institution['Total_Students']) else 0,
                'total_faculty': int(float(institution['Total_Faculty'])) if pd.notna(institution['Total_Faculty']) else 0,
                'placement_rate': round(float(institution['Placement_Rate']), 2) if pd.notna(institution['Placement_Rate']) else 0,
                'placement_category': institution['Placement_Category']
            },
            'infrastructure_metrics': {
                'campus_size': institution['Campus Size'],
                'infrastructure_area': round(float(institution['Infrastructure_Area']), 2) if pd.notna(institution['Infrastructure_Area']) else 0,
                'infrastructure_quality_score': round(float(institution['Infrastructure_Quality']), 2) if pd.notna(institution['Infrastructure_Quality']) else 0,
                'infrastructure_per_student': round(float(institution['Infrastructure_Per_Student']), 2) if pd.notna(institution['Infrastructure_Per_Student']) else 0
            },
            'financial_metrics': {
                'average_fees': int(float(institution['Average Fees'])) if pd.notna(institution['Average Fees']) else 0,
                'fee_category': institution['Fee_Category'],
                'fund_utilization': round(float(institution['Fund_Utilization']), 2) if pd.notna(institution['Fund_Utilization']) else 0,
                'financial_efficiency_score': round(float(institution['Financial_Efficiency']), 2) if pd.notna(institution['Financial_Efficiency']) else 0
            },
            'compliance_metrics': {
                'avg_doc_dss': round(float(institution['Avg_Doc_DSS']), 2) if pd.notna(institution['Avg_Doc_DSS']) else 0,
                'dss_category': institution['DSS_Category'],
                'missing_documents': int(institution['Missing_Doc_Count']) if pd.notna(institution['Missing_Doc_Count']) else 0,
                'document_completeness': round(float(institution['Document_Completeness_Pct']), 2) if pd.notna(institution['Document_Completeness_Pct']) else 0,
                'high_compliance_risk': 'YES' if institution['High_Compliance_Risk'] == 1 else 'NO'
            }
        }
    
    def generate_excel_report(self, institution: pd.Series, all_institutions: pd.DataFrame, filename: Optional[str] = None):
        """Generate Excel report"""
        try:
            import openpyxl
        except ImportError:
            logger.warning("openpyxl not installed, skipping Excel report")
            return None
            
        if filename is None:
            college_name = institution['College Name'].replace(' ', '_')[:30]
            filename = f"{college_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        filepath = self.output_dir / "institutional_reports" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating Excel report: {filename}")
        
        # Generate data
        executive_summary = self.generate_executive_summary(institution)
        risk_assessment = self.generate_risk_assessment(institution)
        performance = self.generate_performance_analysis(institution, all_institutions)
        detailed_metrics = self.generate_detailed_metrics(institution)
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Sheet 1: Executive Summary
            summary_df = pd.DataFrame([executive_summary['metrics']])
            summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
            
            # Sheet 2: Performance Scores
            scores_df = pd.DataFrame([executive_summary['scores']])
            scores_df.to_excel(writer, sheet_name='Performance Scores', index=False)
            
            # Sheet 3: Risk Assessment
            risk_df = pd.DataFrame([risk_assessment])
            risk_df.to_excel(writer, sheet_name='Risk Assessment', index=False)
            
            # Sheet 4: Rankings & Benchmarks
            perf_df = pd.DataFrame([performance])
            perf_df.to_excel(writer, sheet_name='Rankings', index=False)
            
            # Sheet 5: Detailed Metrics
            for category, metrics in detailed_metrics.items():
                metrics_df = pd.DataFrame([metrics])
                metrics_df.to_excel(writer, sheet_name='Detailed Metrics', index=False, startrow=len(metrics_df)+2)
        
        logger.info(f"Excel report saved: {filepath}")
        return filepath
    
    def generate_html_report(self, institution: pd.Series, all_institutions: pd.DataFrame, filename: Optional[str] = None):
        """Generate HTML report"""
        if filename is None:
            college_name = institution['College Name'].replace(' ', '_')[:30]
            filename = f"{college_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        filepath = self.output_dir / "institutional_reports" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating HTML report: {filename}")
        
        # Generate data
        executive_summary = self.generate_executive_summary(institution)
        risk_assessment = self.generate_risk_assessment(institution)
        performance = self.generate_performance_analysis(institution, all_institutions)
        detailed_metrics = self.generate_detailed_metrics(institution)
        
        # Create HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{executive_summary['college_name']} - Institutional Report</title>
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }}
        .header h1 {{ margin: 0 0 10px 0; }}
        .header p {{ margin: 5px 0; opacity: 0.9; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .summary-box {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; }}
        .summary-box h2 {{ color: #667eea; margin-bottom: 15px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }}
        .metric-card {{ background: white; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .risk-high {{ color: #dc3545; }}
        .risk-medium {{ color: #ffc107; }}
        .risk-low {{ color: #28a745; }}
        .recommendation {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px 15px; margin: 10px 0; }}
        .table-wrapper {{ overflow-x: auto; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        td {{ border-bottom: 1px solid #ddd; padding: 12px; }}
        tr:hover {{ background: #f5f5f5; }}
        .footer {{ text-align: center; color: #666; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{executive_summary['college_name']}</h1>
        <p>{executive_summary['city']}, {executive_summary['state']} | {executive_summary['college_type']}</p>
        <p>Report Generated: {executive_summary['report_date']} {executive_summary['report_time']}</p>
    </div>
    
    <div class="container">
        <!-- Executive Summary -->
        <div class="summary-box">
            <h2>Executive Summary</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Overall Performance Score</div>
                    <div class="metric-value">{executive_summary['scores']['overall_performance_score']}/100</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Placement Rate</div>
                    <div class="metric-value">{executive_summary['metrics']['placement_rate']:.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Student-Faculty Ratio</div>
                    <div class="metric-value">{executive_summary['metrics']['student_faculty_ratio']}:1</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Fund Utilization</div>
                    <div class="metric-value">{executive_summary['metrics']['fund_utilization']:.1f}%</div>
                </div>
            </div>
        </div>
        
        <!-- Risk Assessment -->
        <div class="summary-box">
            <h2>Risk Assessment</h2>
            <p><strong>Risk Level:</strong> <span class="risk-{risk_assessment['risk_level'].split()[0].lower()}">{risk_assessment['risk_level']}</span></p>
            <p><strong>Compliance Risk:</strong> {risk_assessment['compliance_risk']}</p>
            <p><strong>Missing Documents:</strong> {risk_assessment['missing_documents']}</p>
            <h3 style="margin-top: 20px; margin-bottom: 10px;">Recommendations:</h3>
            {''.join(f'<div class="recommendation">{rec}</div>' for rec in risk_assessment['recommendations'])}
        </div>
        
        <!-- Performance Analysis -->
        <div class="summary-box">
            <h2>Performance Analysis</h2>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">National Percentile</div>
                    <div class="metric-value">{performance['percentile_overall']:.1f}%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">State Rank</div>
                    <div class="metric-value">{performance['state_rank']}/{performance['state_rank_total']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">National Rank</div>
                    <div class="metric-value">{performance['national_rank']}/{performance['national_rank_total']}</div>
                </div>
            </div>
        </div>
        
        <!-- Detailed Metrics -->
        <div class="summary-box">
            <h2>Detailed Metrics Breakdown</h2>
            <div class="table-wrapper">
                <table>
                    <tbody>
"""
        
        # Add detailed metrics
        for category, metrics in detailed_metrics.items():
            html_content += f"<tr><td colspan='2' style='background: #f8f9fa; font-weight: bold;'>{category.replace('_', ' ').title()}</td></tr>"
            for key, value in metrics.items():
                html_content += f"<tr><td>{key.replace('_', ' ').title()}</td><td>{value}</td></tr>"
        
        html_content += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>EduTrack Institutional Evaluation System</strong></p>
            <p>Report generated on """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved: {filepath}")
        return filepath
    
    def generate_json_report(self, institution: pd.Series, all_institutions: pd.DataFrame, filename: Optional[str] = None):
        """Generate JSON report"""
        if filename is None:
            college_name = institution['College Name'].replace(' ', '_')[:30]
            filename = f"{college_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / "institutional_reports" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating JSON report: {filename}")
        
        report_data = {
            'header': {
                'generated_date': datetime.now().isoformat(),
                'report_type': 'Institutional Evaluation Report',
                'system': 'EduTrack'
            },
            'executive_summary': self.generate_executive_summary(institution),
            'risk_assessment': self.generate_risk_assessment(institution),
            'performance_analysis': self.generate_performance_analysis(institution, all_institutions),
            'detailed_metrics': self.generate_detailed_metrics(institution)
        }
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"JSON report saved: {filepath}")
        return filepath
    
    def generate_batch_reports(self, df: pd.DataFrame, report_format: str = 'all', limit: int = 10):
        """Generate reports for multiple institutions"""
        logger.info(f"\nGenerating {report_format} reports for top {limit} institutions...")
        
        # Get top institutions
        top_institutions = df.nlargest(limit, 'Overall_Performance_Score')
        
        results = []
        for idx, (_, institution) in enumerate(top_institutions.iterrows(), 1):
            logger.info(f"[{idx}/{limit}] {institution['College Name']}")
            
            if report_format in ['all', 'html']:
                self.generate_html_report(institution, df)
            if report_format in ['all', 'excel']:
                self.generate_excel_report(institution, df)
            if report_format in ['all', 'json']:
                self.generate_json_report(institution, df)
            
            results.append(institution['College Name'])
        
        return results


def main():
    """Main report generation pipeline"""
    logger.info("=" * 60)
    logger.info("EDUTRACK REPORT GENERATOR")
    logger.info("=" * 60)
    
    generator = ReportGenerator()
    df = generator.load_data("data/processed/college_data_features.csv")
    
    logger.info("\nGenerating comprehensive institutional reports...\n")
    
    # Generate reports for top 5 institutions
    results = generator.generate_batch_reports(df, report_format='all', limit=5)
    
    logger.info("\n" + "=" * 60)
    logger.info("REPORT GENERATION COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Reports generated for {len(results)} institutions:")
    for name in results:
        logger.info(f"  - {name}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
