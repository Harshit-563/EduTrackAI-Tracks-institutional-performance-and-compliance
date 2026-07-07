"""
Compliance scoring algorithms for institutional compliance assessment.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ComplianceScore:
    """Compliance score result."""
    overall_score: float  # 0-100
    document_compliance: float  # 0-100
    risk_level: str  # "low", "medium", "high"
    components: Dict[str, float]  # Breakdown by category
    recommendations: List[str]


class ComplianceScoringEngine:
    """Engine for calculating institutional compliance scores."""
    
    # Document type weights
    DOCUMENT_WEIGHTS = {
        "fire_safety_certificate": 0.15,
        "financial_audit": 0.20,
        "faculty_list": 0.15,
        "affiliation_letter": 0.15,
        "infrastructure_report": 0.12,
        "placement_report": 0.10,
        "other": 0.13,
    }
    
    # DSS score thresholds
    DSS_THRESHOLDS = {
        "excellent": 90,
        "good": 75,
        "satisfactory": 60,
        "needs_improvement": 40,
        "critical": 0,
    }
    
    # Risk level mappings
    RISK_MAPPINGS = {
        "excellent": ("low", 20),
        "good": ("low", 40),
        "satisfactory": ("medium", 60),
        "needs_improvement": ("high", 80),
        "critical": ("high", 100),
    }

    @classmethod
    def calculate_compliance(
        cls,
        submissions: List[Dict],
        institution_metrics: Dict,
    ) -> ComplianceScore:
        """
        Calculate overall institutional compliance score.
        
        Args:
            submissions: List of submission records with DSS scores and status
            institution_metrics: Dict with institution profile (students, faculty, etc.)
        
        Returns:
            ComplianceScore with overall and component scores
        """
        if not submissions:
            return ComplianceScore(
                overall_score=0,
                document_compliance=0,
                risk_level="high",
                components={},
                recommendations=["No submissions found. Submit required documents."],
            )
        
        # Calculate document compliance
        doc_scores = cls._calculate_document_compliance(submissions)
        
        # Calculate institutional metrics compliance
        metrics_scores = cls._calculate_metrics_compliance(institution_metrics)
        
        # Calculate submission status compliance
        status_scores = cls._calculate_status_compliance(submissions)
        
        # Calculate documentation coverage
        coverage_score = cls._calculate_documentation_coverage(submissions)
        
        # Combine all components (weighted)
        components = {
            "document_quality": doc_scores,
            "institutional_metrics": metrics_scores,
            "submission_status": status_scores,
            "documentation_coverage": coverage_score,
        }
        
        # Overall score: weighted average
        overall_score = (
            doc_scores * 0.40 +
            metrics_scores * 0.25 +
            status_scores * 0.20 +
            coverage_score * 0.15
        )
        
        # Determine risk level
        risk_level = cls._determine_risk_level(overall_score, status_scores)
        
        # Generate recommendations
        recommendations = cls._generate_recommendations(
            overall_score, components, submissions, institution_metrics
        )
        
        return ComplianceScore(
            overall_score=round(overall_score, 2),
            document_compliance=round(doc_scores, 2),
            risk_level=risk_level,
            components={k: round(v, 2) for k, v in components.items()},
            recommendations=recommendations,
        )

    @staticmethod
    def _calculate_document_compliance(submissions: List[Dict]) -> float:
        """Calculate compliance based on document DSS scores."""
        if not submissions:
            return 0.0
        
        total_score = sum(s.get("dss", 0) for s in submissions)
        avg_dss = total_score / len(submissions)
        
        return min(100, avg_dss)

    @staticmethod
    def _calculate_metrics_compliance(institution_metrics: Dict) -> float:
        """Calculate compliance based on institutional metrics."""
        if not institution_metrics:
            return 50.0
        
        components = []
        
        # Student-to-faculty ratio (optimal: 20-30)
        students = institution_metrics.get("total_students", 0)
        faculty = institution_metrics.get("total_faculty", 1)
        if students > 0 and faculty > 0:
            ratio = students / faculty
            ratio_score = 100 - abs(ratio - 25) * 2  # Optimal at 25:1
            ratio_score = max(0, min(100, ratio_score))
            components.append(ratio_score)
        
        # Placement rate (higher is better)
        placement = institution_metrics.get("placement_rate", 0)
        if placement is not None:
            placement_score = min(100, placement)
            components.append(placement_score)
        
        # Fund utilization (50-90% is optimal)
        fund_util = institution_metrics.get("fund_utilization", 0)
        if fund_util is not None:
            if 50 <= fund_util <= 90:
                fund_score = 100
            else:
                fund_score = 100 - abs(fund_util - 70) * 0.5
            fund_score = max(0, min(100, fund_score))
            components.append(fund_score)
        
        # Infrastructure adequacy (area per student: 15-30 sqft optimal)
        infrastructure = institution_metrics.get("infrastructure_area", 0)
        if infrastructure and students:
            area_per_student = infrastructure * 10 / students  # Convert to sqft
            if 15 <= area_per_student <= 30:
                infra_score = 100
            else:
                infra_score = 100 - abs(area_per_student - 22.5) * 2
            infra_score = max(0, min(100, infra_score))
            components.append(infra_score)
        
        return sum(components) / len(components) if components else 50.0

    @staticmethod
    def _calculate_status_compliance(submissions: List[Dict]) -> float:
        """Calculate compliance based on submission status."""
        if not submissions:
            return 0.0
        
        status_scores = {
            "approved": 100,
            "parsed": 85,
            "low_confidence": 60,
            "needs_manual_review": 50,
            "rejected": 0,
        }
        
        total_score = sum(
            status_scores.get(s.get("status", "needs_manual_review"), 50)
            for s in submissions
        )
        
        return total_score / len(submissions)

    @staticmethod
    def _calculate_documentation_coverage(submissions: List[Dict]) -> float:
        """Calculate compliance based on required document coverage."""
        required_docs = {
            "fire_safety_certificate",
            "financial_audit",
            "faculty_list",
            "affiliation_letter",
        }
        
        submitted_types = {s.get("doc_type", "other") for s in submissions if s.get("status") in {"approved", "parsed"}}
        
        coverage = len(submitted_types.intersection(required_docs)) / len(required_docs)
        
        return coverage * 100

    @staticmethod
    def _determine_risk_level(overall_score: float, status_score: float) -> str:
        """Determine institutional risk level."""
        if overall_score >= 80 and status_score >= 80:
            return "low"
        elif overall_score >= 60 and status_score >= 60:
            return "medium"
        else:
            return "high"

    @staticmethod
    def _generate_recommendations(
        overall_score: float,
        components: Dict[str, float],
        submissions: List[Dict],
        institution_metrics: Dict,
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Overall score based recommendations
        if overall_score < 50:
            recommendations.append("Critical: Institution compliance is severely below standards. Immediate action required.")
        elif overall_score < 70:
            recommendations.append("Warning: Institution compliance is below acceptable standards. Plan corrective actions.")
        
        # Component-based recommendations
        if components.get("document_quality", 0) < 70:
            recommendations.append("Improve document quality. Consider resubmitting documents with higher DSS scores.")
        
        if components.get("submission_status", 0) < 70:
            recommendations.append("Resolve pending reviews and rejections. Submit revisions for flagged documents.")
        
        if components.get("documentation_coverage", 0) < 100:
            recommendations.append("Complete missing required documentation. All mandatory documents must be submitted.")
        
        if components.get("institutional_metrics", 0) < 60:
            recommendations.append("Review institutional metrics. Address gaps in student-faculty ratio, placement, or infrastructure.")
        
        # Status-specific recommendations
        pending_count = sum(1 for s in submissions if s.get("status") == "needs_manual_review")
        if pending_count > 0:
            recommendations.append(f"Resolve {pending_count} pending manual reviews to improve compliance score.")
        
        rejected_count = sum(1 for s in submissions if s.get("status") == "rejected")
        if rejected_count > 0:
            recommendations.append(f"Address {rejected_count} rejected documents. Resubmit with corrections.")
        
        if not recommendations:
            recommendations.append("Maintain current compliance standards. Continue to monitor and submit updates as required.")
        
        return recommendations
