import json
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from collections import defaultdict
from utils_url import build_assessment_url

# ---------- CONFIG ----------
INDEX_FILE = "faiss.index"
META_FILE = "faiss_metadata.json"
XLS_FILE = "Gen_AI Dataset.xlsx"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 10

# ---------- LOAD ----------
index = faiss.read_index(INDEX_FILE)
metadata = json.load(open(META_FILE, encoding="utf-8"))
model = SentenceTransformer(MODEL_NAME)

# Build index -> URL using name
index_to_url = {
    i: build_assessment_url(item["name"])
    for i, item in enumerate(metadata)
}

# ---------- LOAD XLS ----------
df = pd.read_excel(XLS_FILE)

required_cols = {"Query", "Assessment_url"}
if not required_cols.issubset(df.columns):
    raise ValueError("XLS must contain Query and Assessment_url columns")

# ---------- GROUND TRUTH ----------
ground_truth = defaultdict(list)
for _, row in df.iterrows():
    ground_truth[row["Query"].strip()].append(row["Assessment_url"].strip())

# ---------- RETRIEVAL ----------
def retrieve_urls(query, k=10):
    emb = model.encode([query]).astype("float32")
    _, indices = index.search(emb, k)
    return [index_to_url[i] for i in indices[0]]

# ---------- EVALUATION ----------
query_to_results = {}

for query, relevant_urls in ground_truth.items():
    predicted_urls = retrieve_urls(query, TOP_K)
    hits = sum(1 for url in relevant_urls if url in predicted_urls)
    recall = hits / len(relevant_urls)

    query_to_results[query] = {
        "predicted": "; ".join(predicted_urls),
        "recall": round(recall, 4)
    }

# ---------- SAVE BACK ----------
df["Predicted_Assessment_URLs"] = df["Query"].map(
    lambda q: query_to_results[q]["predicted"]
)

df["Recall@10"] = df["Query"].map(
    lambda q: query_to_results[q]["recall"]
)

df.to_excel(XLS_FILE, index=False)

print("✅ Results saved to the SAME XLS file")
