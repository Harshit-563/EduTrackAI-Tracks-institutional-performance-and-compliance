"""
Document Validator - predictor.py

Provides:
- DocumentValidator class
- predict_from_ocr(input_data) helper
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import json
import logging
import os
import re

import numpy as np

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:
    SentenceTransformer = None


logger = logging.getLogger("doc_validator")
logging.basicConfig(level=logging.INFO)


REQUIRED_KEYWORDS = {
    "financial_statement": ["balance sheet", "income", "profit", "auditor", "revenue"],
    "faculty_list": ["name", "designation", "qualification", "signature"],
    "fire_safety_certificate": ["fire", "safety", "certificate", "valid", "authority", "issued"],
    "affidavit": ["sworn", "affidavit", "deponent", "signed", "notary"],
}

BASE_DIR = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

OCR_CONF_LOW_THRESHOLD = 0.6
KEYWORD_COVERAGE_THRESHOLD = 0.3
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_DATE_PATTERNS = [
    r"\b(20\d{2})[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b",
    r"\b(0[1-9]|[12]\d|3[01])[-/](0[1-9]|1[0-2])[-/](20\d{2})\b",
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[ ,.-]*(20\d{2})\b",
]
_NUMBER_PATTERN = re.compile(r"(?:(?:\d{1,3}(?:,\d{3})+)|\d+)(?:\.\d+)?")
_SIGNATURE_KEYWORDS = [
    "signature",
    "signed",
    "signatory",
    "authorised signatory",
    "authorised",
    "autho",
]


class DocumentValidator:
    def __init__(
        self,
        templates_dir: Optional[str] = None,
        use_semantic: bool = True,
        embedding_model_name: str = EMBEDDING_MODEL_NAME,
        debug: bool = False,
    ):
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self.use_semantic = use_semantic and (SentenceTransformer is not None)
        self.embedding_model_name = embedding_model_name
        self.debug = debug
        self._emb_model = None

        if self.use_semantic:
            try:
                logger.info("Loading embedding model: %s", self.embedding_model_name)
                self._emb_model = SentenceTransformer(self.embedding_model_name)
            except Exception as e:
                logger.warning(
                    "Failed to load SentenceTransformer; semantic features disabled. Error: %s",
                    e,
                )
                self._emb_model = None
                self.use_semantic = False

    def _load_template_text(self, doc_type: str) -> Optional[str]:
        file_path = os.path.join(self.templates_dir, f"{doc_type}.txt")
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf8") as f:
                return f.read()
        except Exception:
            return None

    def _clean_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        text = text.replace("\x00", " ").strip()
        return re.sub(r"\s+", " ", text)

    def _mean_ocr_confidence(self, pages: List[Dict[str, Any]]) -> Optional[float]:
        confs: List[float] = []
        for page in pages:
            conf = page.get("ocr_conf_mean")
            if conf is None:
                continue
            try:
                confs.append(float(conf))
            except Exception:
                continue
        if not confs:
            return None
        return float(sum(confs) / len(confs))

    def _find_date(self, text: str) -> Optional[Tuple[str, int, int]]:
        for pattern in _DATE_PATTERNS:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return (match.group(0), match.start(), match.end())
        return None

    def _find_numbers(self, text: str, top_n: int = 3) -> List[Tuple[str, int, int]]:
        values: List[Tuple[str, int, int]] = []
        for match in _NUMBER_PATTERN.finditer(text):
            values.append((match.group(0), match.start(), match.end()))
            if len(values) >= top_n:
                break
        return values

    def _keyword_coverage(self, text: str, doc_type: str) -> float:
        keywords = REQUIRED_KEYWORDS.get(doc_type, [])
        if not keywords:
            return 0.0
        text_lc = text.lower()
        found = sum(1 for kw in keywords if kw.lower() in text_lc)
        return found / len(keywords)

    def _has_signature(self, text: str) -> bool:
        text_lc = text.lower()
        return any(keyword in text_lc for keyword in _SIGNATURE_KEYWORDS)

    def _semantic_similarity(self, text: str, doc_type: str) -> Optional[float]:
        if not self.use_semantic or self._emb_model is None:
            return None
        template = self._load_template_text(doc_type)
        if not template:
            return None
        try:
            vectors = self._emb_model.encode(
                [text, template],
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            a = vectors[0]
            b = vectors[1]
            denom = np.linalg.norm(a) * np.linalg.norm(b)
            if denom == 0:
                return 0.0
            return float(np.dot(a, b) / denom)
        except Exception as e:
            logger.warning("Semantic similarity failed: %s", e)
            return None

    def _find_snippet_page(
        self, pages: List[Dict[str, Any]], pattern: str
    ) -> Optional[Tuple[int, int, int, str]]:
        for page in pages:
            text = page.get("text", "") or ""
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                page_no = int(page.get("page_no", 1))
                return (page_no, match.start(), match.end(), match.group(0))
        return None

    def predict_from_dict(self, ocr: Dict[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        try:
            doc_id = ocr.get("doc_id") or ocr.get("id") or "unknown"
            doc_type = (ocr.get("doc_type") or "unknown").lower()
            pages = ocr.get("pages", []) or []
            full_text = ocr.get("full_text", "") or ""

            if not full_text:
                full_text = " ".join((p.get("text", "") or "") for p in pages)
            full_text = self._clean_text(full_text)

            ocr_conf = self._mean_ocr_confidence(pages)
            status = "parsed"
            if ocr_conf is not None and ocr_conf < OCR_CONF_LOW_THRESHOLD:
                status = "low_confidence"

            fields: Dict[str, Any] = {}
            text_snippets: List[Dict[str, Any]] = []
            dss_flags: List[str] = []

            date_match = self._find_date(full_text)
            if date_match:
                date_value, start, end = date_match
                page_info = self._find_snippet_page(pages, re.escape(date_value))
                if page_info:
                    page_no, page_start, page_end, snippet_text = page_info
                    snippet_start = page_start
                    snippet_end = page_end
                    snippet_value = snippet_text
                else:
                    page_no = int(pages[0].get("page_no", 1)) if pages else 1
                    snippet_start = start
                    snippet_end = end
                    snippet_value = date_value

                fields["document_date"] = {
                    "value": date_value,
                    "conf": 0.9 if ocr_conf is None or ocr_conf > 0.8 else 0.75,
                    "page": page_no,
                    "bbox": None,
                }
                text_snippets.append(
                    {
                        "page": page_no,
                        "start": snippet_start,
                        "end": snippet_end,
                        "text": snippet_value,
                    }
                )
            else:
                fields["document_date"] = {"value": None, "conf": 0.0, "page": None, "bbox": None}
                dss_flags.append("missing_date")

            numbers = self._find_numbers(full_text, top_n=5)
            fields["numeric_mentions"] = [
                {"value": value, "start": start, "end": end}
                for (value, start, end) in numbers
            ]

            coverage = self._keyword_coverage(full_text, doc_type)
            fields["keyword_coverage"] = {"value": coverage, "conf": 0.9}
            if coverage < KEYWORD_COVERAGE_THRESHOLD:
                dss_flags.append("low_keyword_coverage")

            has_signature = self._has_signature(full_text)
            fields["has_signature"] = {"value": has_signature, "conf": 0.95 if has_signature else 0.1}
            if not has_signature:
                dss_flags.append("missing_signature")

            semsim = self._semantic_similarity(full_text, doc_type) if self.use_semantic else None
            fields["semantic_similarity"] = {"value": semsim, "conf": 0.9 if semsim is not None else 0.0}

            if doc_type == "fire_safety_certificate":
                if re.search(
                    r"\b(fire department|municipal|authority|fire\s+brigade)\b",
                    full_text,
                    flags=re.IGNORECASE,
                ):
                    fields["issuing_authority"] = {"value": "present", "conf": 0.85}
                else:
                    fields["issuing_authority"] = {"value": None, "conf": 0.0}
                    dss_flags.append("no_issuing_authority_found")

            if ocr_conf is None and len(full_text.split()) < 20:
                status = "low_confidence"

            dss_score = 100
            if ocr_conf is not None:
                if ocr_conf < 0.5:
                    dss_score -= 30
                elif ocr_conf < 0.7:
                    dss_score -= 20
                elif ocr_conf < 0.85:
                    dss_score -= 10

            if coverage < 0.2:
                dss_score -= 30
            elif coverage < 0.4:
                dss_score -= 15

            if not has_signature:
                dss_score -= 25
            if "missing_date" in dss_flags:
                dss_score -= 10

            dss_score = max(0, min(100, int(round(dss_score))))

            result["doc_id"] = doc_id
            result["status"] = status
            result["fields"] = fields
            result["text_snippets"] = text_snippets
            result["ocr_confidence"] = ocr_conf
            result["dss_flags"] = sorted(set(dss_flags))
            result["dss_score"] = dss_score

            if self.debug:
                result["raw"] = ocr
            return result
        except Exception as e:
            logger.exception("DocumentValidator failed: %s", e)
            return {
                "doc_id": ocr.get("doc_id", "unknown") if isinstance(ocr, dict) else "unknown",
                "status": "failed",
                "fields": {},
                "text_snippets": [],
                "ocr_confidence": None,
                "dss_flags": ["exception"],
                "error": str(e),
                "raw": (ocr if self.debug else None),
            }

    def predict_from_path(self, json_path: str) -> Dict[str, Any]:
        if not os.path.exists(json_path):
            raise FileNotFoundError(json_path)
        with open(json_path, "r", encoding="utf8") as f:
            ocr = json.load(f)
        return self.predict_from_dict(ocr)


_default_validator: Optional[DocumentValidator] = None


def get_default_validator(debug: bool = False) -> DocumentValidator:
    global _default_validator
    if _default_validator is None:
        _default_validator = DocumentValidator(debug=debug)
    return _default_validator


def predict_from_ocr(input_data: Union[str, Dict[str, Any]], debug: bool = False) -> Dict[str, Any]:
    validator = get_default_validator(debug=debug)
    if isinstance(input_data, str):
        return validator.predict_from_path(input_data)
    if isinstance(input_data, dict):
        return validator.predict_from_dict(input_data)
    raise ValueError("input_data must be file path or dict")


if __name__ == "__main__":
    import argparse
    import pprint

    parser = argparse.ArgumentParser()
    parser.add_argument("--ocr", required=True, help="Path to OCR json file")
    parser.add_argument("--debug", action="store_true", help="Include raw OCR in output")
    args = parser.parse_args()

    validator = DocumentValidator(debug=args.debug)
    output = validator.predict_from_path(args.ocr)
    pprint.pprint(output)
