"""
Document Validator - Advanced DSS Prediction
Provides comprehensive document scoring using OCR data, text analysis, and ML
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import json
import logging
import os
import re
from pathlib import Path
from datetime import datetime, timedelta
from functools import lru_cache

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    SentenceTransformer = None

logger = logging.getLogger("doc_validator")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# =====================================================
# CONSTANTS & CONFIGURATION
# =====================================================

REQUIRED_KEYWORDS = {
    "financial_statement": [
        "balance sheet", "income", "profit", "auditor", "revenue",
        "assets", "liabilities", "equity"
    ],
    "faculty_list": [
        "name", "designation", "qualification", "signature",
        "department", "email", "contact"
    ],
    "fire_safety_certificate": [
        "fire", "safety", "certificate", "valid", "authority",
        "issued", "noc", "evacuation", "fire safety"
    ],
    "affidavit": [
        "sworn", "affidavit", "deponent", "signed", "notary",
        "solemnly", "declare"
    ],
    "affiliation_letter": [
        "affiliation", "approved", "recognized", "university",
        "affiliated", "letter", "valid"
    ],
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Thresholds
OCR_CONF_EXCELLENT = 0.85
OCR_CONF_GOOD = 0.70
OCR_CONF_ACCEPTABLE = 0.55
KEYWORD_COVERAGE_THRESHOLD = 0.30
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Regex patterns
DATE_PATTERNS = [
    r"\b(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b",
    r"\b(0[1-9]|[12]\d|3[01])[-/](0[1-9]|1[0-2])[-/](20\d{2})\b",
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[ ,.-]*(20\d{2})\b",
]
NUMBER_PATTERN = re.compile(r"(?:(?:\d{1,3}(?:,\d{3})+)|\d+)(?:\.\d+)?")
SIGNATURE_KEYWORDS = [
    "signature", "signed", "signatory", "authorised signatory",
    "authorized", "autho", "seal", "stamp"
]
OFFICIAL_KEYWORDS = [
    "official", "certified", "authorized", "approved",
    "accredited", "government", "ministry", "department"
]


class DocumentValidator:
    """Advanced document validator with semantic analysis"""
    
    def __init__(
        self,
        templates_dir: Optional[str] = None,
        use_semantic: bool = True,
        embedding_model_name: str = EMBEDDING_MODEL_NAME,
        debug: bool = False
    ):
        """
        Initialize Document Validator
        
        Args:
            templates_dir: Directory containing template files
            use_semantic: Enable semantic similarity checking
            embedding_model_name: Name of embedding model
            debug: Include debug information in output
        """
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self.use_semantic = use_semantic and SEMANTIC_AVAILABLE
        self.embedding_model_name = embedding_model_name
        self.debug = debug
        self._emb_model = None
        
        if self.use_semantic:
            self._load_embedding_model()
    
    def _load_embedding_model(self) -> None:
        """Load semantic embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self._emb_model = SentenceTransformer(self.embedding_model_name)
            logger.info("✓ Embedding model loaded successfully")
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}")
            self._emb_model = None
            self.use_semantic = False
    
    # =====================================================
    # TEXT PROCESSING METHODS
    # =====================================================
    
    def _clean_text(self, text: Optional[str]) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        text = text.replace("\x00", " ").strip()
        text = re.sub(r"\s+", " ", text)
        return text
    
    def _extract_dates(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract dates with confidence scores
        
        Args:
            text: Text to search
        
        Returns:
            List of date dictionaries
        """
        dates = []
        seen = set()
        
        for pattern in DATE_PATTERNS:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                date_str = match.group(0)
                
                if date_str in seen:
                    continue
                seen.add(date_str)
                
                # Parse date components
                try:
                    # Try to standardize format
                    parts = re.findall(r'\d+', date_str)
                    
                    if len(parts) >= 3:
                        if len(parts[0]) == 4:  # Year first
                            year, month, day = parts[0], parts[1], parts[2]
                        else:  # Year last
                            month, day, year = parts[0], parts[1], parts[2]
                        
                        # Validate
                        year_int = int(year)
                        month_int = int(month)
                        day_int = int(day)
                        
                        if 1900 <= year_int <= 2100 and 1 <= month_int <= 12 and 1 <= day_int <= 31:
                            dates.append({
                                "value": date_str,
                                "year": year_int,
                                "month": month_int,
                                "day": day_int,
                                "position": (match.start(), match.end())
                            })
                except (ValueError, IndexError):
                    continue
        
        return dates
    
    def _extract_numbers(self, text: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Extract numeric values"""
        numbers = []
        
        for match in NUMBER_PATTERN.finditer(text):
            try:
                value = float(match.group(0).replace(',', ''))
                numbers.append({
                    "value": value,
                    "text": match.group(0),
                    "position": (match.start(), match.end())
                })
                if len(numbers) >= top_n:
                    break
            except ValueError:
                continue
        
        return numbers
    
    def _keyword_coverage(self, text: str, doc_type: str) -> float:
        """
        Calculate keyword coverage percentage
        
        Args:
            text: Text to analyze
            doc_type: Document type
        
        Returns:
            Coverage percentage (0.0 - 1.0)
        """
        keywords = REQUIRED_KEYWORDS.get(doc_type.lower(), [])
        if not keywords:
            return 0.0
        
        text_lower = text.lower()
        found = sum(1 for kw in keywords if kw.lower() in text_lower)
        
        return found / len(keywords)
    
    def _has_signature_or_seal(self, text: str) -> Dict[str, bool]:
        """Check for signature/seal indicators"""
        text_lower = text.lower()
        
        return {
            "has_signature": any(kw in text_lower for kw in SIGNATURE_KEYWORDS),
            "has_official_mark": any(kw in text_lower for kw in OFFICIAL_KEYWORDS)
        }
    
    # =====================================================
    # SEMANTIC ANALYSIS
    # =====================================================
    
    def _semantic_similarity(self, text: str, doc_type: str) -> Optional[float]:
        """Calculate semantic similarity to document type template"""
        if not self.use_semantic or self._emb_model is None:
            return None
        
        template = self._load_template_text(doc_type)
        if not template:
            return None
        
        try:
            vectors = self._emb_model.encode(
                [text, template],
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            a, b = vectors[0], vectors[1]
            denom = np.linalg.norm(a) * np.linalg.norm(b)
            
            if denom == 0:
                return 0.0
            
            similarity = float(np.dot(a, b) / denom)
            return max(0.0, min(1.0, similarity))
        
        except Exception as e:
            logger.warning(f"Semantic similarity failed: {e}")
            return None
    
    def _load_template_text(self, doc_type: str) -> Optional[str]:
        """Load document template"""
        template_file = os.path.join(
            self.templates_dir,
            f"{doc_type.lower()}.txt"
        )
        
        if not os.path.exists(template_file):
            return None
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to load template: {e}")
            return None
    
    # =====================================================
    # DSS SCORING LOGIC
    # =====================================================
    
    def _calculate_dss_score(
        self,
        ocr_conf: Optional[float],
        keyword_coverage: float,
        has_signature: bool,
        has_date: bool,
        has_official_mark: bool,
        semantic_sim: Optional[float],
        text_length: int,
        doc_type: str
    ) -> int:
        """
        Calculate Document Sufficiency Score (DSS)
        
        Args:
            ocr_conf: OCR confidence (0.0-1.0)
            keyword_coverage: Keyword coverage percentage (0.0-1.0)
            has_signature: Whether signature detected
            has_date: Whether date detected
            has_official_mark: Whether official mark detected
            semantic_sim: Semantic similarity (0.0-1.0)
            text_length: Length of extracted text
            doc_type: Type of document
        
        Returns:
            DSS Score (0-100)
        """
        score = 50.0  # Neutral baseline
        
        # OCR Confidence (25 points max)
        if ocr_conf is not None:
            if ocr_conf >= OCR_CONF_EXCELLENT:
                score += 25
            elif ocr_conf >= OCR_CONF_GOOD:
                score += 18
            elif ocr_conf >= OCR_CONF_ACCEPTABLE:
                score += 10
            else:
                score -= 10
        
        # Keyword Coverage (20 points max)
        if keyword_coverage >= 0.8:
            score += 20
        elif keyword_coverage >= 0.5:
            score += 12
        elif keyword_coverage >= 0.3:
            score += 6
        else:
            score -= 5
        
        # Signature/Authentication (15 points max)
        if has_signature:
            score += 10
        if has_official_mark:
            score += 5
        
        # Date Information (10 points max)
        if has_date:
            score += 10
        else:
            score -= 5
        
        # Semantic Similarity (15 points max)
        if semantic_sim is not None:
            if semantic_sim >= 0.7:
                score += 15
            elif semantic_sim >= 0.5:
                score += 10
            elif semantic_sim >= 0.3:
                score += 5
        
        # Text Length (10 points max)
        if text_length > 1000:
            score += 10
        elif text_length > 500:
            score += 6
        elif text_length > 200:
            score += 3
        elif text_length < 50:
            score -= 10
        
        # Normalize score
        return max(0, min(100, int(round(score))))
    
    # =====================================================
    # MAIN PREDICTION METHOD
    # =====================================================
    
    def predict_from_dict(self, ocr: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict DSS from OCR output dictionary
        
        Args:
            ocr: OCR output dictionary
        
        Returns:
            Prediction result with DSS score
        """
        try:
            # Extract fields
            doc_id = ocr.get("doc_id") or ocr.get("id") or "unknown"
            doc_type = (ocr.get("doc_type") or ocr.get("file_format") or "unknown").lower()
            pages = ocr.get("pages", []) or []
            full_text = ocr.get("full_text", "") or ""
            ocr_conf = ocr.get("ocr_conf_mean")
            
            # Reconstruct text if missing
            if not full_text and pages:
                full_text = "\n\n".join(
                    p.get("text", "") or "" for p in pages
                )
            
            full_text = self._clean_text(full_text)
            text_length = len(full_text)
            
            # Determine status based on OCR confidence
            status = "parsed"
            if ocr_conf is not None:
                if ocr_conf < 0.55:
                    status = "low_confidence"
            
            if text_length < 50:
                status = "low_confidence"
            
            # Initialize result
            flags = []
            fields = {}
            
            # Extract key information
            dates = self._extract_dates(full_text)
            numbers = self._extract_numbers(full_text, top_n=5)
            
            fields['extracted_dates'] = [
                {"value": d['value'], "year": d['year']}
                for d in dates
            ]
            fields['numeric_values'] = [
                {"value": n['value'], "text": n['text']}
                for n in numbers
            ]
            
            # Analyze content
            coverage = self._keyword_coverage(full_text, doc_type)
            auth_check = self._has_signature_or_seal(full_text)
            
            fields['keyword_coverage'] = round(coverage, 3)
            fields['has_signature'] = auth_check['has_signature']
            fields['has_official_mark'] = auth_check['has_official_mark']
            
            # Semantic analysis
            semsim = self._semantic_similarity(full_text, doc_type)
            if semsim is not None:
                fields['semantic_similarity'] = round(semsim, 3)
            
            # Generate flags
            if ocr_conf is not None and ocr_conf < 0.60:
                flags.append("low_ocr_confidence")
            
            if coverage < 0.30:
                flags.append("low_keyword_coverage")
            
            if not auth_check['has_signature']:
                flags.append("no_signature_detected")
            
            if not dates:
                flags.append("no_date_found")
            
            if text_length < 200:
                flags.append("minimal_text_content")
            
            # Calculate DSS Score
            dss_score = self._calculate_dss_score(
                ocr_conf=ocr_conf,
                keyword_coverage=coverage,
                has_signature=auth_check['has_signature'],
                has_date=len(dates) > 0,
                has_official_mark=auth_check['has_official_mark'],
                semantic_sim=semsim,
                text_length=text_length,
                doc_type=doc_type
            )
            
            # Determine classification
            if dss_score >= 85:
                classification = "Valid - High Confidence"
            elif dss_score >= 70:
                classification = "Valid - Medium Confidence"
            elif dss_score >= 55:
                classification = "Needs Review"
            elif dss_score >= 40:
                classification = "Requires Correction"
            else:
                classification = "Invalid"
            
            # Build result
            result = {
                "success": True,
                "doc_id": doc_id,
                "doc_type": doc_type,
                "status": status,
                "classification": classification,
                "dss_score": dss_score,
                "flags": sorted(set(flags)),
                "fields": fields,
                "ocr_confidence": ocr_conf,
                "text_length": text_length,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if self.debug:
                result['raw_ocr'] = ocr
            
            return result
        
        except Exception as e:
            logger.exception(f"Prediction failed: {e}")
            return {
                "success": False,
                "doc_id": ocr.get("doc_id", "unknown") if isinstance(ocr, dict) else "unknown",
                "status": "failed",
                "error": str(e),
                "dss_score": 0,
                "flags": ["exception"],
                "fields": {}
            }
    
    def predict_from_path(self, json_path: str) -> Dict[str, Any]:
        """Predict from JSON file"""
        if not os.path.exists(json_path):
            raise FileNotFoundError(json_path)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            ocr = json.load(f)
        
        return self.predict_from_dict(ocr)


# =====================================================
# STANDALONE FUNCTIONS
# =====================================================

_default_validator: Optional[DocumentValidator] = None

def get_default_validator(debug: bool = False) -> DocumentValidator:
    """Get or create default validator instance"""
    global _default_validator
    if _default_validator is None:
        _default_validator = DocumentValidator(debug=debug)
    return _default_validator

def predict_from_ocr(
    input_data: Union[str, Dict[str, Any]],
    debug: bool = False
) -> Dict[str, Any]:
    """
    Main prediction function
    
    Args:
        input_data: File path or OCR dictionary
        debug: Include debug info
    
    Returns:
        Prediction result with DSS score
    """
    validator = get_default_validator(debug=debug)
    
    if isinstance(input_data, str):
        return validator.predict_from_path(input_data)
    elif isinstance(input_data, dict):
        return validator.predict_from_dict(input_data)
    else:
        raise ValueError("input_data must be file path or dictionary")


# =====================================================
# MAIN (FOR TESTING)
# =====================================================

if __name__ == "__main__":
    import argparse
    import pprint
    
    parser = argparse.ArgumentParser(description="Document Validator")
    parser.add_argument("--ocr", required=True, help="Path to OCR JSON file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    logger.info(f"Validating: {args.ocr}")
    
    validator = DocumentValidator(debug=args.debug)
    output = validator.predict_from_path(args.ocr)
    
    print("\n" + "="*60)
    print("PREDICTION RESULT")
    print("="*60)
    pprint.pprint(output)