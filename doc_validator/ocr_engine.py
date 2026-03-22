"""
OCR Engine for document text extraction
Supports: PDF, PNG, JPG, JPEG, TIFF, BMP
Features: Confidence scoring, page-level metadata, error recovery
"""

import logging
import os
import json
from typing import Any, Dict, List, Union, Optional, Tuple
from pathlib import Path
from datetime import datetime
from functools import lru_cache

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logger = logging.getLogger("ocr_engine")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Configure Tesseract path
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    logger.info(f"✓ Tesseract configured at {TESSERACT_CMD}")
else:
    logger.warning(f"⚠️ Tesseract not found at {TESSERACT_CMD}")

# Configuration
DEFAULT_DPI = 300
MAX_PAGES_DEFAULT = 10
SUPPORTED_FORMATS = {'.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
MIN_TEXT_LENGTH = 20  # Minimum meaningful text


class OCREngine:
    """Production-ready OCR Engine for document processing"""
    
    def __init__(
        self,
        dpi: int = DEFAULT_DPI,
        max_pages: int = MAX_PAGES_DEFAULT,
        tesseract_cmd: Optional[str] = None
    ):
        """
        Initialize OCR Engine
        
        Args:
            dpi: DPI for PDF conversion (default 300)
            max_pages: Maximum pages to process (default 10)
            tesseract_cmd: Path to Tesseract executable
        """
        self.dpi = dpi
        self.max_pages = max_pages
        self.available = OCR_AVAILABLE
        
        if tesseract_cmd and os.path.exists(tesseract_cmd):
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            logger.info(f"Tesseract configured at {tesseract_cmd}")
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Main entry point for OCR processing
        
        Args:
            file_path: Path to document file
        
        Returns:
            Structured OCR result with metadata
        """
        try:
            # Validate file
            file_path = str(file_path)
            if not os.path.exists(file_path):
                return self._error_response(f"File not found: {file_path}", file_path)
            
            file_obj = Path(file_path)
            filename = file_obj.name
            ext = file_obj.suffix.lower()
            
            # Validate format
            if ext not in SUPPORTED_FORMATS:
                return self._error_response(
                    f"Unsupported format: {ext}. Supported: {', '.join(SUPPORTED_FORMATS)}",
                    file_path
                )
            
            logger.info(f"Processing: {filename}")
            
            # Process based on file type
            if ext == '.pdf':
                result = self._process_pdf(file_path)
            else:
                result = self._process_image(file_path)
            
            # Add metadata
            result['file_path'] = file_path
            result['file_name'] = filename
            result['file_size_kb'] = round(os.path.getsize(file_path) / 1024, 2)
            result['processed_at'] = datetime.utcnow().isoformat()
            
            return result
        
        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            return self._error_response(str(e), file_path)
    
    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process PDF document"""
        try:
            logger.info("Converting PDF to images (DPI: %d)...", self.dpi)
            
            images = convert_from_path(file_path, dpi=self.dpi)
            page_count = len(images)
            
            if page_count > self.max_pages:
                logger.warning(
                    f"PDF has {page_count} pages. Processing first {self.max_pages}."
                )
                images = images[:self.max_pages]
            
            pages_payload = []
            full_text_parts = []
            confidences = []
            
            for page_no, image in enumerate(images, start=1):
                logger.info(f"Scanning page {page_no}/{len(images)}...")
                
                page_data = self._process_single_image(image, page_no)
                
                pages_payload.append({
                    "page_no": page_no,
                    "text": page_data['text'],
                    "ocr_conf_mean": page_data['confidence'],
                    "word_count": len(page_data['text'].split()),
                    "char_count": len(page_data['text'])
                })
                
                full_text_parts.append(page_data['text'])
                confidences.append(page_data['confidence'])
            
            # Calculate document-level statistics
            overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            total_words = sum(p['word_count'] for p in pages_payload)
            
            return {
                "success": True,
                "doc_id": Path(file_path).stem,
                "doc_type": "pdf",
                "file_format": "PDF",
                "page_count": page_count,
                "processed_pages": len(pages_payload),
                "pages": pages_payload,
                "full_text": "\n\n".join(full_text_parts),
                "ocr_conf_mean": round(overall_confidence, 3),
                "total_words": total_words,
                "avg_words_per_page": round(total_words / len(pages_payload), 1) if pages_payload else 0,
                "status": "success"
            }
        
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return self._error_response(str(e), file_path)
    
    def _process_image(self, file_path: str) -> Dict[str, Any]:
        """Process image document"""
        try:
            logger.info("Processing image...")
            
            image = Image.open(file_path)
            page_data = self._process_single_image(image, page_no=1)
            
            return {
                "success": True,
                "doc_id": Path(file_path).stem,
                "doc_type": "image",
                "file_format": Path(file_path).suffix.upper().strip('.'),
                "page_count": 1,
                "processed_pages": 1,
                "pages": [{
                    "page_no": 1,
                    "text": page_data['text'],
                    "ocr_conf_mean": page_data['confidence'],
                    "word_count": len(page_data['text'].split()),
                    "char_count": len(page_data['text'])
                }],
                "full_text": page_data['text'],
                "ocr_conf_mean": page_data['confidence'],
                "image_size": image.size,
                "image_mode": image.mode,
                "total_words": len(page_data['text'].split()),
                "status": "success"
            }
        
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return self._error_response(str(e), file_path)
    
    def _process_single_image(
        self,
        image_obj: Union[str, Image.Image],
        page_no: int = 1
    ) -> Dict[str, Any]:
        """
        Run OCR on single image with confidence calculation
        
        Args:
            image_obj: PIL Image or file path
            page_no: Page number for logging
        
        Returns:
            Dictionary with text and confidence
        """
        try:
            # Open image if path
            img = image_obj if isinstance(image_obj, Image.Image) else Image.open(image_obj)
            
            # Get detailed TSV output (word-level confidences)
            tsv = pytesseract.image_to_data(
                img,
                output_type=pytesseract.Output.DICT
            )
            
            words = []
            confidences = []
            
            for i in range(len(tsv.get('text', []))):
                text = str(tsv['text'][i]).strip()
                conf_str = str(tsv['conf'][i])
                
                # Skip empty text or invalid confidence
                if not text or conf_str == '-1':
                    continue
                
                words.append(text)
                
                try:
                    # Tesseract returns 0-100 scale
                    conf = float(conf_str) / 100.0
                    confidences.append(max(0.0, min(1.0, conf)))
                except (ValueError, TypeError):
                    continue
            
            # Combine words
            page_text = ' '.join(words)
            
            # Calculate average confidence
            avg_confidence = (
                sum(confidences) / len(confidences) if confidences else 0.0
            )
            
            # Quality metrics
            quality = self._assess_quality(avg_confidence, len(page_text))
            
            logger.info(
                f"Page {page_no}: {len(words)} words, "
                f"Conf: {avg_confidence:.2%}, Quality: {quality}"
            )
            
            return {
                'text': page_text,
                'confidence': round(avg_confidence, 3),
                'word_count': len(words),
                'quality': quality
            }
        
        except Exception as e:
            logger.error(f"Single image processing failed: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'word_count': 0,
                'quality': 'failed'
            }
    
    def _assess_quality(self, confidence: float, text_length: int) -> str:
        """Assess OCR quality"""
        if confidence >= 0.9 and text_length > 500:
            return "excellent"
        elif confidence >= 0.75 and text_length > 200:
            return "good"
        elif confidence >= 0.60 and text_length > 100:
            return "acceptable"
        else:
            return "poor"
    
    def _error_response(self, error_msg: str, file_path: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "doc_id": Path(file_path).stem if file_path else "unknown",
            "error": error_msg,
            "status": "failed",
            "pages": [],
            "full_text": "",
            "ocr_conf_mean": 0.0
        }


# =====================================================
# Standalone Function Interface
# =====================================================

_engine = None

def get_ocr_engine(
    dpi: int = DEFAULT_DPI,
    max_pages: int = MAX_PAGES_DEFAULT
) -> OCREngine:
    """Get or create OCR engine instance"""
    global _engine
    if _engine is None:
        _engine = OCREngine(dpi=dpi, max_pages=max_pages)
    return _engine

def run_ocr(file_path: str, max_pages: int = MAX_PAGES_DEFAULT) -> Dict[str, Any]:
    """
    Standalone function to run OCR on document
    
    Args:
        file_path: Path to document file
        max_pages: Maximum pages to process
    
    Returns:
        OCR result dictionary
    """
    engine = get_ocr_engine(max_pages=max_pages)
    return engine.process(file_path)


# =====================================================
# MAIN (FOR TESTING)
# =====================================================

if __name__ == "__main__":
    import sys
    
    logger.info("OCR Engine Test Started...")
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "test_document.pdf"
    
    logger.info(f"Input file: {input_file}")
    
    if os.path.exists(input_file):
        engine = OCREngine()
        result = engine.process(input_file)
        
        print("\n" + "="*60)
        print("OCR RESULT")
        print("="*60)
        print(json.dumps(result, indent=2, default=str))
    else:
        logger.error(f"File not found: {input_file}")