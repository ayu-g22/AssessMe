import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INPUT_FILE = "assessments_structured.json"
INDEX_FILE = "faiss.index"
META_FILE = "faiss_metadata.json"

def main():
    data = json.load(open(INPUT_FILE, encoding="utf-8"))

    texts = [d["text_for_embedding"] for d in data]

    print("🔹 Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("🔹 Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)

    embeddings = np.array(embeddings).astype("float32")

    print("🔹 Building FAISS index...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, INDEX_FILE)

    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("FAISS index built and saved")

if __name__ == "__main__":
    main()
