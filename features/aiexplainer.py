import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise Exception("❌ GROQ API KEY NOT FOUND")

client = Groq(api_key=api_key)


def explain_code(code: str):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # ✅ FIXED MODEL
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that explains code in simple, beginner-friendly English."
            },
            {
                "role": "user",
                "content": f"Explain this code clearly:\n\n{code}"
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content