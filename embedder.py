from sentence_transformers import SentenceTransformer
import json

# Load the model once (downloads automatically on first run ~80MB)
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_code_embedding(code_snippet):
    embedding = model.encode(code_snippet)
    return embedding.tolist()


def embed_parsed_result(parsed_result):
    embeddings = []

    for func in parsed_result["functions"]:
        text = f"function {func['name']} with args {func['args']} in file {parsed_result['file']}"
        embedding = get_code_embedding(text)
        embeddings.append({
            "type": "function",
            "name": func["name"],
            "line": func["line"],
            "embedding": embedding
        })

    for cls in parsed_result["classes"]:
        text = f"class {cls['name']} in file {parsed_result['file']}"
        embedding = get_code_embedding(text)
        embeddings.append({
            "type": "class",
            "name": cls["name"],
            "line": cls["line"],
            "embedding": embedding
        })

    return embeddings


def cosine_similarity(vec1, vec2):
    dot = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = sum(a ** 2 for a in vec1) ** 0.5
    mag2 = sum(b ** 2 for b in vec2) ** 0.5
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


# Test it
if __name__ == "__main__":
    from parser import parse_file

    # Parse the sample file
    parsed = parse_file("../samples/sample.py")

    # Embed it
    embeddings = embed_parsed_result(parsed)

    # Print summary (not full vectors — they are 384 numbers long!)
    for item in embeddings:
        print(f"{item['type']:10} | {item['name']:20} | vector length: {len(item['embedding'])}")

    # Test similarity between two items
    if len(embeddings) >= 2:
        sim = cosine_similarity(embeddings[0]["embedding"], embeddings[1]["embedding"])
        print(f"\nSimilarity between '{embeddings[0]['name']}' and '{embeddings[1]['name']}': {sim:.4f}")