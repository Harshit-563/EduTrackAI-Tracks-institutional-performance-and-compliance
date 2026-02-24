import json
import os
import re
from typing import Any, Dict

from groq import Groq


def _load_env_files() -> None:
    """
    Load env vars from common local .env locations if present.
    Existing process environment variables are not overwritten.
    """
    base_dir = os.path.dirname(__file__)
    candidates = [
        os.path.join(base_dir, ".env"),
        os.path.join(os.path.dirname(base_dir), ".env"),
    ]

    for path in candidates:
        if not os.path.exists(path):
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")

                    if key and key not in os.environ:
                        os.environ[key] = value
        except Exception:
            # Keep running; missing/invalid local .env should not crash import.
            continue


def _build_client() -> Groq:
    _load_env_files()
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY environment variable is not set (checked process env and local .env files)."
        )

    return Groq(api_key=api_key)


def extract_json(text: str) -> Dict[str, Any]:
    """
    Clean model output and parse JSON safely.
    Handles markdown-wrapped JSON and extra pre/postamble text.
    """
    if not isinstance(text, str) or not text.strip():
        return {"error": "JSON Parsing Failed: empty output", "raw_output": text}

    candidate = text.strip()

    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, flags=re.DOTALL)
    if fence_match:
        candidate = fence_match.group(1)

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
