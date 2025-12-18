
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# ---- STANDARD IMPORTS ----
import json
import faiss
import numpy as np
import requests
from bs4 import BeautifulSoup
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# ================= CONFIG =================
INDEX_FILE = "faiss.index"
META_FILE = "faiss_metadata.json"
MODEL_NAME = "all-MiniLM-L6-v2"   # safe model for accuracy vs memory

# ================= LAZY-LOADED GLOBALS =================
index = None
metadata = None
model = None

# ================= LOAD ASSETS LAZILY =================
def load_assets():
    global index, metadata, model

    if index is None:
        index = faiss.read_index(INDEX_FILE)

    if metadata is None:
        with open(META_FILE, encoding="utf-8") as f:
            metadata = json.load(f)

    if model is None:
        model = SentenceTransformer(MODEL_NAME)

# ================= FASTAPI APP =================
app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0"
)

# ================= CORS (REQUIRED FOR FRONTEND) =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # OK for assignment submission
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= REQUEST MODEL =================
class RecommendRequest(BaseModel):
    query_text: Optional[str] = None
    query_url: Optional[str] = None
    top_k: int = 5

# ================= UTIL: URL TEXT EXTRACTION =================
def extract_text_from_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    return " ".join(text.split())

# ================= HEALTH CHECK =================
@app.get("/")
def health():
    return {"status": "ok"}

# ================= RECOMMEND ENDPOINT =================
@app.post("/recommend")
def recommend(req: RecommendRequest):
    # ---- VALIDATION ----
    if not req.query_text and not req.query_url:
        raise HTTPException(
            status_code=400,
            detail="Either query_text or query_url must be provided"
        )

    top_k = max(5, min(req.top_k, 10))

    # ---- LOAD HEAVY ASSETS (LAZY) ----
    load_assets()

    # ---- GET QUERY TEXT ----
    if req.query_text:
        query = req.query_text
    else:
        try:
            query = extract_text_from_url(req.query_url)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch URL: {str(e)}"
            )

    # ---- VECTOR SEARCH ----
    query_vec = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vec, top_k)

    # ---- FORMAT RESPONSE ----
    results = []
    for idx, score in zip(indices[0], distances[0]):
        item = metadata[idx]

        results.append({
            "Assessment Name": item.get("name", "N/A"),
            "Test Type": item.get("test_type", "N/A"),
            "Job Levels": ", ".join(item.get("job_levels", [])) or "N/A",
            "Duration (min)": item.get("duration_minutes") or "N/A",
            "Score": round(float(score), 4),
        })

    return {
        "results_count": len(results),
        "table": results
    }
