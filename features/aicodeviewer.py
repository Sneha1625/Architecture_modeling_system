import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def review_code(code):

    prompt = f"""
You are a senior software engineer doing a professional code review.

Analyze the following Python code and provide:

1. Code Quality Issues
2. Code Smells
3. Performance Problems
4. Security Issues (if any)
5. Best Practice Violations
6. Suggestions for Improvement

Be clear, structured, and simple.

Code:
{code}
"""

    try:
        response = client.chat.completions.create(
         model="llama-3.1-8b-instant",   # ✅ updated model (important)
            messages=[
                {"role": "system", "content": "You are a senior code reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"