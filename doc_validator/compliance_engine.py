import json
import os
import re
from typing import Any, Dict

from groq import Groq


GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def _build_client() -> Groq:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY environment variable is not set")
    return Groq(api_key=GROQ_API_KEY)


def extract_json(text: str) -> Dict[str, Any]:
    """
    Clean model output and parse JSON safely.
    Handles markdown-wrapped JSON and extra pre/postamble text.
    """
    if not isinstance(text, str) or not text.strip():
        return {"error": "JSON Parsing Failed: empty output", "raw_output": text}

    candidate = text.strip()

    # Remove markdown code fences if present.
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, flags=re.DOTALL)
    if fence_match:
        candidate = fence_match.group(1)

    # Keep only the outermost JSON object if extra text exists.
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end >= start:
        candidate = candidate[start : end + 1]

    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
        return {"error": "JSON Parsing Failed: expected object", "raw_output": text}
    except Exception as e:
        return {"error": f"JSON Parsing Failed: {e}", "raw_output": text}


def analyze_compliance_with_llm(ocr_text: str, doc_type: str) -> Dict[str, Any]:
    """
    Send OCR text to Groq-hosted Llama for compliance-oriented extraction.
    """
    system_prompt = f"""
You are an AI Compliance Officer for AICTE/UGC.
Analyze the provided document text.

Document Type: {doc_type}

Your Tasks:
1. Extract the 'Document Date' and 'Expiry Date' (if any).
2. Check if the document appears valid (contains official stamps/signatures keywords).
3. Summarize the key details in 1 sentence.

Output strictly in this JSON format:
{{
  "is_valid_document": true,
  "extracted_dates": ["YYYY-MM-DD"],
  "compliance_status": "Compliant",
  "reason": "Brief explanation",
  "summary": "One line summary"
}}
""".strip()

    try:
        client = _build_client()
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the OCR Text:\n\n{(ocr_text or '')[:4000]}"},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        raw_content = completion.choices[0].message.content or ""
        return extract_json(raw_content)
    except Exception as e:
        return {"error": str(e), "status": "LLM_Failed"}


if __name__ == "__main__":
    sample = "Fire Safety Cert. Valid Upto: 2025-12-31. Signed by CFO."
    print(analyze_compliance_with_llm(sample, "Fire Safety Certificate"))
