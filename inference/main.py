from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import logging

import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Model configuration — controlled via compose.yaml env vars
# ---------------------------------------------------------------------------
MODEL_NAME = os.getenv("MODEL_NAME", "BAAI/bge-reranker-v2-m3")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------------------------------------------------------------------
# Global model state (loaded once at startup)
# ---------------------------------------------------------------------------
tokenizer = None
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tokenizer, model
    logger.info(f"Loading cross-encoder model '{MODEL_NAME}' on device '{DEVICE}' ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.to(DEVICE)
    model.eval()
    logger.info("Cross-encoder model loaded and ready.")
    yield
    # Nothing to clean up for a pure-CPU/GPU model


app = FastAPI(title="Reranker Inference Service", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class RerankRequest(BaseModel):
    query: str
    passages: List[str]


class ScoredPassage(BaseModel):
    passage: str
    score: float


class RerankResponse(BaseModel):
    results: List[ScoredPassage]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "device": DEVICE, "model": MODEL_NAME}


@app.post("/rerank", response_model=RerankResponse)
def rerank(request: RerankRequest):
    """Score each passage against the query and return them sorted descending."""
    if not request.passages:
        return RerankResponse(results=[])

    pairs = [[request.query, passage] for passage in request.passages]

    encoded = tokenizer(
        pairs,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt",
    ).to(DEVICE)

    with torch.no_grad():
        logits = model(**encoded).logits.squeeze(-1).float()

    scores: List[float] = logits.tolist()
    if isinstance(scores, float):          # single-passage edge-case
        scores = [scores]

    sorted_results = sorted(
        zip(scores, request.passages),
        key=lambda x: x[0],
        reverse=True,
    )

    return RerankResponse(
        results=[
            ScoredPassage(passage=passage, score=score)
            for score, passage in sorted_results
        ]
    )
