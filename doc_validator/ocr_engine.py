import logging
import os
from typing import Any, Dict, List, Union

import pytesseract
from pdf2image import convert_from_path
from PIL import Image


logger = logging.getLogger("ocr_engine")
logging.basicConfig(level=logging.INFO)

# Point this to your local Tesseract install path.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _process_single_image(image_obj: Union[str, Image.Image]) -> Dict[str, Any]:
    """
    Run OCR on a single image (PIL Image or file path) using Tesseract.
    Approximates confidence using per-word confidences from TSV output.
    """
    img = image_obj if isinstance(image_obj, Image.Image) else Image.open(image_obj)

    # Detailed output with word-level confidences
    tsv = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    words: List[str] = []
    confs: List[float] = []

    for i in range(len(tsv["text"])):
        text = tsv["text"][i].strip()
        conf = tsv["conf"][i]

        if text and conf != "-1":
            words.append(text)
            try:
                # Tesseract returns confidence in 0-100 range.
                confs.append(float(conf) / 100.0)
            except ValueError:
                continue

    page_text = " ".join(words)
    avg_conf = sum(confs) / len(confs) if confs else 0.0

    return {
        "text": page_text,
        "conf": avg_conf,
    }


def run_ocr(file_path: str, max_pages: int = 10) -> Dict[str, Any]:
    """
    Main entry point.
    Handles .pdf, .jpg, .png, etc.
    Returns the JSON format required by predictor.py.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()

    pages_payload: List[Dict[str, Any]] = []
    full_text_parts: List[str] = []

    logger.info("Processing: %s", filename)

    try:
        if ext == ".pdf":
            logger.info("Converting PDF to images...")
            images = convert_from_path(file_path, dpi=200)

            if len(images) > max_pages:
                logger.warning(
                    "PDF has %s pages. Truncating to first %s.",
                    len(images),
                    max_pages,
                )
                images = images[:max_pages]

            # 1-based indexing for document page numbers.
            for page_no, img in enumerate(images, start=1):
                logger.info("OCR Scanning Page %s/%s...", page_no, len(images))
                p_data = _process_single_image(img)
                pages_payload.append(
                    {
                        "page_no": page_no,
                        "text": p_data["text"],
                        "ocr_conf_mean": round(p_data["conf"], 3),
                    }
                )
                full_text_parts.append(p_data["text"])

        elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
            logger.info("Scanning single image...")
            p_data = _process_single_image(file_path)
            pages_payload.append(
                {
                    "page_no": 1,
                    "text": p_data["text"],
                    "ocr_conf_mean": round(p_data["conf"], 3),
                }
            )
            full_text_parts.append(p_data["text"])

        else:
            raise ValueError(f"Unsupported file format: {ext}")

        all_confs = [p["ocr_conf_mean"] for p in pages_payload if p["ocr_conf_mean"] > 0]
        doc_avg_conf = sum(all_confs) / len(all_confs) if all_confs else 0.0

        return {
            "doc_id": filename,
            "doc_type": "unknown",
            "pages": pages_payload,
            "full_text": "\n\n".join(full_text_parts),
            "ocr_conf_mean": round(doc_avg_conf, 3),
        }
    except Exception as e:
        logger.error("OCR Engine Failed: %s", e)
        return {
            "doc_id": filename,
            "error": str(e),
            "status": "failed",
        }


if __name__ == "__main__":
    import json
    import sys

    print("OCR engine script started...")
    input_file = sys.argv[1] if len(sys.argv) > 1 else "test_fire_cert.jpg"
    print(f"Input file: {input_file}")

    if os.path.exists(input_file):
        result = run_ocr(input_file)
        print("\n===== OCR RESULT =====")
        print(json.dumps(result, indent=2))
    else:
        print(f"Please provide a valid file path. {input_file} not found.")
