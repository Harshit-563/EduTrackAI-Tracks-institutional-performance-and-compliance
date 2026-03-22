# filepath: c:\edutech\utils\constants.py
"""
Project-wide constants and configurations
"""

# Document Requirements (by category)
REQUIRED_DOCUMENTS = {
    'accreditation': [
        'NAAC_Certificate',
        'NIRF_Registration',
        'NBA_Accreditation'
    ],
    'administrative': [
        'Affiliation_Letter',
        'Regulatory_Approval',
        'Government_Recognition'
    ],
    'academic': [
        'Curriculum_Approval',
        'Faculty_Credentials',
        'Research_Papers'
    ],
    'infrastructure': [
        'Campus_Details',
        'Lab_Certificates',
        'Facility_Report'
    ],
    'financial': [
        'Audit_Report',
        'Budget_Statement',
        'Tax_Documents'
    ]
}

# DSS Score Ranges
DSS_RANGES = {
    'excellent': (85, 100),
    'good': (70, 84),
    'satisfactory': (55, 69),
    'needs_improvement': (40, 54),
    'critical': (0, 39)
}

# Performance Tiers
PERFORMANCE_TIERS = {
    'excellent': {'color': '#2ecc71', 'description': 'Excellent Performance'},
    'good': {'color': '#3498db', 'description': 'Good Performance'},
    'satisfactory': {'color': '#f39c12', 'description': 'Satisfactory Performance'},
    'needs_improvement': {'color': '#e74c3c', 'description': 'Needs Improvement'},
    'critical': {'color': '#c0392b', 'description': 'Critical Status'}
}

# Schemes
SCHEMES = [
    'PARAMARSH',
    'SWAYAM',
    'NASSCOM',
    'DST_FUNDED',
    'DBT_FUNDED',
    'IMPRINT_INDIA'
]

# Evaluation Weights
EVALUATION_WEIGHTS = {
    'academic_performance': 0.35,
    'infrastructure': 0.25,
    'scheme_participation': 0.20,
    'rankings': 0.20
}

# Risk Levels
RISK_LEVELS = {
    'low': (0, 33),
    'medium': (34, 66),
    'high': (67, 100)
}

# File Upload Configuration
ALLOWED_UPLOAD_TYPES = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
MAX_UPLOAD_SIZE_MB = 50

# API Configuration
API_TITLE = "EduTrack Backend API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI-Based Institutional Compliance & Risk System"