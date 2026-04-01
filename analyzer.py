"""
analyzer.py — FREE AI Code Analyzer using Groq (FINAL STABLE VERSION)
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

# ================= ENV =================
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("Groq API key not found! Check your .env file.")

client = Groq(api_key=api_key)


# ================= HELPER =================
def safe_json_parse(text):
    try:
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return {
            "responsibility": "Could not parse AI response",
            "issues": [],
            "suggestions": ["AI response format issue"],
            "quality_score": 0,
            "complexity": "unknown"
        }


# ================= FUNCTION ANALYSIS =================
def analyze_function(func, source_code, file_path):

    prompt = f"""
You are a senior Python code reviewer.

Analyze ONLY this function from the code.

Function Name: {func.get("name")}

Full Code:
{source_code}

STRICTLY return JSON:

{{
 "responsibility": "clear explanation of what function does",
 "issues": [
   "real issues (edge cases, bugs, inefficiency)"
 ],
 "suggestions": [
   "specific improvements for THIS function"
 ],
 "quality_score": 0-100,
 "complexity": "low|medium|high"
}}

IMPORTANT:
- Suggestions must be specific to THIS code
- Mention improvements like:
  - edge case handling
  - time complexity
  - readability
  - Python best practices
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # ✅ WORKING MODEL
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content
        return safe_json_parse(raw)

    except Exception as e:
        return {
            "responsibility": "Error in AI analysis",
            "issues": [str(e)],
            "suggestions": ["Check API/model configuration"],
            "quality_score": 0,
            "complexity": "unknown"
        }


# ================= MAIN =================
def analyze_parsed_result(parsed_result, source_code):

    functions_result = []

    for func in parsed_result.get("functions", []):
        analysis = analyze_function(func, source_code, parsed_result.get("file"))

        functions_result.append({
            "name": func.get("name"),
            "line": func.get("line"),
            "analysis": analysis,
            "complexity": func.get("complexity", 1),
            "complexity_label": func.get("complexity_label", "low")
        })

    return {
        "functions": functions_result   # ✅ IMPORTANT (matches app.py)
    }


# ================= TEST =================
if __name__ == "__main__":
    from parser import parse_file, read_file

    parsed = parse_file("../samples/sample.py")
    source = read_file("../samples/sample.py")

    result = analyze_parsed_result(parsed, source)

    print(json.dumps(result, indent=2))