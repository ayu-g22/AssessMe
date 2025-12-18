# app.py

import json
import faiss
import numpy as np
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from typing import Optional

# ================= CONFIG =================
INDEX_FILE = "faiss.index"
META_FILE = "faiss_metadata.json"
MODEL_NAME = "all-MiniLM-L6-v2"

# ================= LOAD ASSETS =================
print("Loading FAISS index and metadata...")
index = faiss.read_index(INDEX_FILE)
metadata = json.load(open(META_FILE, encoding="utf-8"))
model = SentenceTransformer(MODEL_NAME)

# ================= FASTAPI APP =================
app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0",
)

# ================= CORS (FIXES 405 OPTIONS) =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://assess-me-n913.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # allows OPTIONS, POST, etc.
    allow_headers=["*"],
)

# ================= MODELS =================
class RecommendRequest(BaseModel):
    query_text: Optional[str] = None
    query_url: Optional[str] = None
    top_k: int = 5

# ================= UTIL =================
def extract_text_from_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    return " ".join(text.split())

# ================= ROUTES =================
@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/recommend")
def recommend(req: RecommendRequest):
    # -------- validation --------
    if not req.query_text and not req.query_url:
        raise HTTPException(
            status_code=400,
            detail="Either query_text or query_url must be provided",
        )

    # Enforce 5–10
    top_k = max(5, min(req.top_k, 10))

    # -------- get query --------
    if req.query_text:
        query = req.query_text
        query_used = "text"
    else:
        try:
            query = extract_text_from_url(req.query_url)
            query_used = "url"
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch URL: {str(e)}",
            )

    # -------- vector search --------
    query_embedding = model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)

    # -------- build table --------
    table = []
    for idx, dist in zip(indices[0], distances[0]):
        item = metadata[idx]

        duration = item.get("duration_minutes")
        
        table.append({
            "Assessment Name": item.get("name"),
            "Test Type": item.get("test_type", "N/A"),
            "Job Levels": ", ".join(item.get("job_levels", [])) or "N/A",
            "Duration (min)": duration if duration is not None else "N/A",
            "Score": round(float(dist), 4),
        })

    return {
        "query_used": query_used,
        "results_count": len(table),
        "table": table,
    }
