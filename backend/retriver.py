import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_FILE = "faiss.index"
META_FILE = "faiss_metadata.json"

def load_assets():
    index = faiss.read_index(INDEX_FILE)
    metadata = json.load(open(META_FILE, encoding="utf-8"))
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return index, metadata, model

def search(query, top_k=10):
    index, metadata, model = load_assets()

    query_embedding = model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        item = metadata[idx]
        results.append({
            "name": item["name"],
            "test_type": item["test_type"],
            "job_levels": item["job_levels"],
            "duration_minutes": item["duration_minutes"],
            "score": float(dist)
        })

    return results

if __name__ == "__main__":
    query = """
    Looking for an assessment for an entry-level accounts payable role.
    Candidate should have basic accounting knowledge and attention to detail.
    """
    results = search(query)

    for r in results:
        print(f"{r['name']} | {r['test_type']} | {r['duration_minutes']} mins")
