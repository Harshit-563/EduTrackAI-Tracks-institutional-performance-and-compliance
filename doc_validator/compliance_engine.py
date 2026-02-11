# doc_validator/compliance_engine.py
import os
import json
import re
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


# Load from environment to avoid committing secrets
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY environment variable is not set")
client = Groq(api_key=GROQ_API_KEY)

def extract_json(text):
    """
    Helper: Cleans LLM output to ensure json.loads() works.
    Removes markdown code blocks (```json ... ```) and finds the main { object }.
    """
    try:
        # 1. Remove Markdown code blocks if present
        if "```" in text:
            # Matches content inside ```json ... ``` or just ``` ... ```
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                text = match.group(1)
        
        # 2. Find the first '{' and last '}' to strip external filler text
        start = text.find("{")
        end = text.rfind("}") + 1
        
        if start != -1 and end != -1:
            clean_text = text[start:end]
            return json.loads(clean_text)
        else:
            # Fallback: Try loading raw text
            return json.loads(text)
            
    except Exception as e:
        return {"error": f"JSON Parsing Failed: {str(e)}", "raw_output": text}

def analyze_compliance_with_llm(ocr_text, doc_type):
    """
    Sends OCR text to Llama-3 (via Groq) for intelligent analysis.
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
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the OCR Text:\n\n{ocr_text[:4000]}"}
            ],
            temperature=0,
            # IMPORTANT: forcing json_object helps, but our helper is the safety net
            response_format={"type": "json_object"} 
        )
        
        raw_content = completion.choices[0].message.content
        
        # USE THE HELPER FUNCTION HERE
        return extract_json(raw_content)

    except Exception as e:
        return {"error": str(e), "status": "LLM_Failed"}

# Test it
if __name__ == "__main__":
    dummy_text = "Fire Safety Cert. Valid Upto: 2025-12-31. Signed by CFO."
    print(analyze_compliance_with_llm(dummy_text, "Fire Safety Certificate"))
