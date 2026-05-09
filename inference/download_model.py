"""
One-time script to download and cache the reranker model weights to ./models.

Run this ONCE on the host before starting the Docker services:

    python inference/download_model.py

The cached files will be stored in ./models/hub/ following the standard
HuggingFace cache layout (same as HF_HOME). The reranker container mounts
./models as /models and sets HF_HOME=/models, so it reads from here instead
of downloading anything at startup.
"""

import os
from pathlib import Path

# Mirror the HF_HOME that the container uses
MODELS_DIR = Path(__file__).parent.parent / "models"
os.environ["HF_HOME"] = str(MODELS_DIR)

MODEL_NAME = os.getenv("MODEL_NAME", "BAAI/bge-reranker-v2-m3")

print(f"Downloading model '{MODEL_NAME}' into '{MODELS_DIR}' ...")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

from transformers import AutoTokenizer, AutoModelForSequenceClassification

AutoTokenizer.from_pretrained(MODEL_NAME)
AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

print(f"\n✅  Model cached successfully at: {MODELS_DIR}")
print("You can now start the reranker service with:")
print("  docker compose up -d --build reranker")
