import anthropic
import os
from dotenv import load_dotenv

# Fix: load .env using the file's actual location
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("API key not found! Check your .env file.")

client = anthropic.Anthropic(api_key="ANTHROPIC_API_KEY")


def analyze_function(func_name, func_args, file_path, source_code):
    prompt = f"""You are an expert Python code reviewer.

Analyze this Python code from file '{file_path}':
```python
{source_code}
```

Focus on the function called '{func_name}' with arguments {func_args}.

Give me:
1. What this function does (1-2 sentences)
2. Any code smells or issues
3. Suggestions to improve it
4. Complexity rating: low / medium / high

Keep your response concise and structured."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content[0].text


def analyze_parsed_result(parsed_result, source_code):
    all_analysis = []

    print(f"\nAnalyzing file: {parsed_result['file']}")
    print(f"Found {len(parsed_result['functions'])} functions to analyze...\n")

    for func in parsed_result["functions"]:
        print(f"  Analyzing function: {func['name']}...")
        analysis = analyze_function(
            func["name"],
            func["args"],
            parsed_result["file"],
            source_code
        )
        all_analysis.append({
            "type": "function",
            "name": func["name"],
            "line": func["line"],
            "analysis": analysis
        })

    return all_analysis


# Test it
if __name__ == "__main__":
    from parser import parse_file, read_file

    parsed = parse_file("../samples/sample.py")
    source = read_file("../samples/sample.py")

    results = analyze_parsed_result(parsed, source)

    for item in results:
        print(f"\n{'='*50}")
        print(f"Function: {item['name']} (line {item['line']})")
        print(f"{'='*50}")
        print(item["analysis"])