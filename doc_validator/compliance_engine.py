"""
AI-Powered Compliance Analysis Engine
Uses Groq LLM (Llama 3.3 70B) for intelligent document compliance assessment
"""

import json
import os
import re
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from functools import lru_cache
import time

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

logger = logging.getLogger(__name__)

# =====================================================
# ENVIRONMENT LOADING
# =====================================================

def _load_env_files() -> None:
    """
    Load environment variables from .env files.
    Searches parent directories without overwriting existing vars.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check up to 3 levels up
    candidates = []
    current = base_dir
    for _ in range(4):
        candidates.append(os.path.join(current, ".env"))
        parent = os.path.dirname(current)
        if parent == current:  # Reached root
            break
        current = parent
    
    for env_path in candidates:
        if not os.path.exists(env_path):
            continue
        
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line_num, raw_line in enumerate(f, 1):
                    line = raw_line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue
                    
                    if "=" not in line:
                        logger.debug(f"Skipping malformed .env line {line_num}: {line}")
                        continue
                    
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Only set if not already in environment
                    if key and key not in os.environ:
                        os.environ[key] = value
        
        except Exception as e:
            logger.warning(f"Failed to load .env from {env_path}: {e}")
            continue
        
        logger.info(f"Loaded environment from: {env_path}")
        break


def _build_groq_client() -> Optional[Groq]:
    """
    Build Groq client with API key from environment.
    
    Returns:
        Groq client instance or None if API key unavailable
    """
    _load_env_files()
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        logger.error("GROQ_API_KEY not found in environment variables")
        return None
    
    try:
        client = Groq(api_key=api_key)
        logger.info("✓ Groq client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")
        return None


# =====================================================
# JSON PARSING & VALIDATION
# =====================================================

def extract_json(text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from LLM output.
    Handles markdown, extra text, and malformed JSON gracefully.
    
    Args:
        text: Raw text from LLM (may contain markdown, extra text)
    
    Returns:
        Parsed JSON dict or error dict
    """
    if not isinstance(text, str):
        return {
            "success": False,
            "error": "Invalid input: expected string",
            "raw_output": str(text)
        }
    
    text = text.strip()
    if not text:
        return {
            "success": False,
            "error": "Empty LLM output",
            "raw_output": ""
        }
    
    # Try markdown code fence extraction
    fence_patterns = [
        r"```json\s*(\{.*?\})\s*```",
        r"```\s*(\{.*?\})\s*```",
    ]
    
    for pattern in fence_patterns:
        match = re.search(pattern, text, flags=re.DOTALL)
        if match:
            text = match.group(1)
            break
    
    # Extract JSON object from text
    start = text.find("{")
    end = text.rfind("}")
    
    if start == -1 or end == -1 or end < start:
        return {
            "success": False,
            "error": "No JSON object found in output",
            "raw_output": text
        }
    
    text = text[start:end + 1]
    
    # Try parsing
    try:
        parsed = json.loads(text)
        
        if not isinstance(parsed, dict):
            return {
                "success": False,
                "error": "Parsed JSON is not a dictionary",
                "raw_output": text
            }
        
        # Mark as successful
        parsed["success"] = True
        return parsed
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {
            "success": False,
            "error": f"JSON parsing failed: {str(e)}",
            "raw_output": text
        }
    except Exception as e:
        logger.error(f"Unexpected parsing error: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "raw_output": text
        }


def validate_compliance_response(response: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate compliance response structure and content.
    
    Args:
        response: Response dict from LLM
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required fields
    required_fields = [
        'is_valid_document',
        'extracted_dates',
        'compliance_status',
        'summary'
    ]
    
    for field in required_fields:
        if field not in response:
            issues.append(f"Missing required field: {field}")
    
    # Validate field types
    if 'is_valid_document' in response:
        if not isinstance(response['is_valid_document'], bool):
            issues.append("is_valid_document must be boolean")
    
    if 'extracted_dates' in response:
        if not isinstance(response['extracted_dates'], list):
            issues.append("extracted_dates must be a list")
        else:
            # Validate date format
            for date_str in response['extracted_dates']:
                if not re.match(r'\d{4}-\d{2}-\d{2}', str(date_str)):
                    issues.append(f"Invalid date format: {date_str} (expected YYYY-MM-DD)")
    
    if 'compliance_status' in response:
        valid_statuses = ['Compliant', 'Non-Compliant', 'Partial', 'Undetermined']
        if response['compliance_status'] not in valid_statuses:
            issues.append(f"Invalid compliance_status. Must be one of: {valid_statuses}")
    
    return len(issues) == 0, issues


# =====================================================
# COMPLIANCE ANALYSIS ENGINE
# =====================================================

class ComplianceEngine:
    """LLM-powered compliance analysis engine"""
    
    def __init__(self, retry_count: int = 3, timeout_seconds: int = 30):
        """
        Initialize Compliance Engine
        
        Args:
            retry_count: Number of retries on failure
            timeout_seconds: Timeout for API calls
        """
        self.client = _build_groq_client() if GROQ_AVAILABLE else None
        self.retry_count = retry_count
        self.timeout_seconds = timeout_seconds
        self.available = self.client is not None
        
        if not self.available:
            logger.warning("⚠️ Groq client not available. Using fallback mode.")
    
    def analyze_compliance(
        self,
        ocr_text: str,
        doc_type: str,
        institution_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze document compliance using LLM.
        
        Args:
            ocr_text: Extracted text from OCR
            doc_type: Type of document (e.g., 'Fire Safety Certificate')
            institution_name: Optional institution name for context
        
        Returns:
            Compliance analysis result
        """
        # Validate inputs
        if not ocr_text or not isinstance(ocr_text, str):
            return self._create_error_response(
                "Invalid OCR text provided",
                doc_type
            )
        
        if not doc_type or not isinstance(doc_type, str):
            return self._create_error_response(
                "Invalid document type",
                doc_type or "unknown"
            )
        
        # Check API availability
        if not self.available:
            logger.warning("Groq API not available, using fallback analysis")
            return self._fallback_compliance_analysis(ocr_text, doc_type)
        
        # Attempt LLM analysis with retries
        for attempt in range(self.retry_count):
            try:
                result = self._analyze_with_llm(ocr_text, doc_type, institution_name)
                
                if result.get("success"):
                    return result
                
                # Log failed attempt
                logger.warning(
                    f"Attempt {attempt + 1}/{self.retry_count} failed: "
                    f"{result.get('error', 'Unknown error')}"
                )
                
                # Wait before retry (exponential backoff)
                if attempt < self.retry_count - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
            
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} exception: {e}")
                
                if attempt == self.retry_count - 1:
                    # All retries failed, use fallback
                    logger.warning("All retries failed, using fallback analysis")
                    return self._fallback_compliance_analysis(ocr_text, doc_type)
                
                time.sleep(2 ** attempt)
        
        return self._create_error_response(
            "Max retries exceeded",
            doc_type
        )
    
    def _analyze_with_llm(
        self,
        ocr_text: str,
        doc_type: str,
        institution_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Internal LLM analysis method.
        
        Args:
            ocr_text: Extracted text
            doc_type: Document type
            institution_name: Optional institution context
        
        Returns:
            Analysis result
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(doc_type, institution_name)
        
        # Truncate OCR text to avoid token limits
        truncated_text = ocr_text[:3000]
        
        try:
            # Call Groq API
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Analyze this document:\n\n{truncated_text}"
                    },
                ],
                temperature=0,  # Deterministic output
                max_tokens=500,
                response_format={"type": "json_object"},
            )
            
            # Extract response
            raw_content = completion.choices[0].message.content or ""
            logger.debug(f"Raw LLM response: {raw_content[:200]}...")
            
            # Parse JSON
            result = extract_json(raw_content)
            
            # Validate response
            is_valid, issues = validate_compliance_response(result)
            
            if not is_valid:
                logger.warning(f"Response validation failed: {issues}")
                result['validation_issues'] = issues
            
            # Add metadata
            result['doc_type'] = doc_type
            result['timestamp'] = datetime.utcnow().isoformat()
            result['llm_model'] = 'llama-3.3-70b-versatile'
            
            return result
        
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return {
                "success": False,
                "error": f"LLM API error: {str(e)}",
                "doc_type": doc_type,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_system_prompt(
        self,
        doc_type: str,
        institution_name: Optional[str] = None
    ) -> str:
        """Build comprehensive system prompt for LLM"""
        institution_context = ""
        if institution_name:
            institution_context = f"\nInstitution: {institution_name}"
        
        return f"""You are an Expert Compliance Officer for AICTE/UGC Educational Institutions.
Your role: Analyze educational documents for compliance.

Document Type: {doc_type}{institution_context}

CRITICAL TASKS:
1. Extract Document Date and Expiry Date (YYYY-MM-DD format)
2. Verify document authenticity (official stamps, signatures, seals)
3. Check for required compliance elements specific to {doc_type}
4. Assess overall compliance status
5. Provide concise summary and reasoning

COMPLIANCE RULES:
- Government-issued documents require official marks
- Dates must be in YYYY-MM-DD format
- Expiry dates must be in future (unless explicitly expired)
- Missing critical elements = Non-Compliant
- Partial information = Partial compliance

OUTPUT STRICTLY IN THIS JSON FORMAT (no extra text):
{{
  "is_valid_document": boolean,
  "extracted_dates": ["YYYY-MM-DD"],
  "document_date": "YYYY-MM-DD or null",
  "expiry_date": "YYYY-MM-DD or null",
  "compliance_status": "Compliant|Non-Compliant|Partial|Undetermined",
  "has_official_marks": boolean,
  "critical_elements_found": ["element1", "element2"],
  "missing_elements": ["element1"],
  "flags": ["warning1", "warning2"],
  "reason": "Brief explanation of compliance status",
  "summary": "One-line summary of document"
}}

Be strict but fair. Output only valid JSON.
""".strip()
    
    def _fallback_compliance_analysis(
        self,
        ocr_text: str,
        doc_type: str
    ) -> Dict[str, Any]:
        """
        Fallback analysis when LLM is unavailable.
        Uses regex and heuristics.
        
        Args:
            ocr_text: Extracted text
            doc_type: Document type
        
        Returns:
            Analysis result
        """
        logger.info("Using fallback compliance analysis")
        
        text_lower = ocr_text.lower()
        
        # Extract dates
        dates = self._extract_dates_from_text(ocr_text)
        document_date = dates[0] if len(dates) > 0 else None
        expiry_date = dates[-1] if len(dates) > 1 else dates[0] if dates else None
        
        # Check official marks
        official_keywords = ['signature', 'signature', 'seal', 'stamp', 'certified', 'authorized']
        has_official_marks = any(kw in text_lower for kw in official_keywords)
        
        # Determine compliance
        is_valid = len(ocr_text) > 100 and has_official_marks
        
        critical_elements = []
        if has_official_marks:
            critical_elements.append("Official marks")
        if dates:
            critical_elements.append("Date information")
        
        flags = []
        if not has_official_marks:
            flags.append("No official marks detected - may be informal")
        if not dates:
            flags.append("No dates found - expiry verification impossible")
        
        compliance_status = "Compliant" if is_valid else ("Partial" if len(critical_elements) > 0 else "Non-Compliant")
        
        return {
            "success": True,
            "is_valid_document": is_valid,
            "extracted_dates": dates,
            "document_date": document_date,
            "expiry_date": expiry_date,
            "compliance_status": compliance_status,
            "has_official_marks": has_official_marks,
            "critical_elements_found": critical_elements,
            "missing_elements": [],
            "flags": flags,
            "reason": "Fallback analysis (LLM unavailable)",
            "summary": f"{doc_type} - {compliance_status}",
            "doc_type": doc_type,
            "timestamp": datetime.utcnow().isoformat(),
            "llm_model": "fallback_heuristic"
        }
    
    def _extract_dates_from_text(self, text: str) -> List[str]:
        """
        Extract dates from text using multiple patterns.
        
        Args:
            text: Text to search
        
        Returns:
            List of dates in YYYY-MM-DD format
        """
        dates = []
        
        patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{1,2})-(\w+)-(\d{4})',      # DD-Month-YYYY
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    if len(match[2]) == 4:  # Year is at index 2
                        year, month, day = match[2], match[0], match[1]
                    else:  # Year is at index 0
                        year, month, day = match[0], match[1], match[2]
                    
                    # Format as YYYY-MM-DD
                    formatted = f"{year}-{int(month):02d}-{int(day):02d}"
                    if formatted not in dates:
                        dates.append(formatted)
                except (ValueError, IndexError):
                    continue
        
        return dates
    
    def _create_error_response(
        self,
        error_message: str,
        doc_type: str
    ) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "error": error_message,
            "doc_type": doc_type,
            "timestamp": datetime.utcnow().isoformat(),
            "is_valid_document": False,
            "compliance_status": "Undetermined",
            "flags": [error_message]
        }
    
    def batch_analyze(
        self,
        documents: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple documents.
        
        Args:
            documents: List of {ocr_text, doc_type, institution_name}
        
        Returns:
            List of analysis results
        """
        results = []
        
        for doc in documents:
            try:
                result = self.analyze_compliance(
                    doc.get('ocr_text', ''),
                    doc.get('doc_type', 'Unknown'),
                    doc.get('institution_name')
                )
                results.append(result)
                
                # Rate limiting
                time.sleep(0.5)
            
            except Exception as e:
                logger.error(f"Batch analysis error: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "doc_type": doc.get('doc_type', 'Unknown')
                })
        
        return results


# =====================================================
# STANDALONE FUNCTIONS (Backward Compatibility)
# =====================================================

_engine = None

def get_compliance_engine() -> ComplianceEngine:
    """Get or create compliance engine instance"""
    global _engine
    if _engine is None:
        _engine = ComplianceEngine()
    return _engine

def analyze_compliance_with_llm(
    ocr_text: str,
    doc_type: str,
    institution_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Standalone function for compliance analysis.
    
    Args:
        ocr_text: Extracted OCR text
        doc_type: Type of document
        institution_name: Optional institution context
    
    Returns:
        Compliance analysis result
    """
    engine = get_compliance_engine()
    return engine.analyze_compliance(ocr_text, doc_type, institution_name)


# =====================================================
# MAIN (FOR TESTING)
# =====================================================

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Test sample
    sample_ocr = """
    FIRE SAFETY CERTIFICATE
    
    Certificate No: FS-2024-001234
    Date Issued: 2024-01-15
    Valid Until: 2025-12-31
    
    This certifies that the institution at XYZ College
    has been inspected and found to comply with all
    fire safety regulations as per IS 1643.
    
    Inspector Signature: [STAMP]
    
    Authorized by: Fire Safety Department
    Government of India
    """
    
    engine = get_compliance_engine()
    result = engine.analyze_compliance(
        sample_ocr,
        "Fire Safety Certificate",
        "XYZ College of Engineering"
    )
    
    print(json.dumps(result, indent=2))