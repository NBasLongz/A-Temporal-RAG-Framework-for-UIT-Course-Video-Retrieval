"""
FastAPI server chính — VideoLearn REST API.
Cung cấp REST API cho frontend và serve static files.

Chạy:
    uvicorn app.api.main:app --reload --port 8000
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes import chat, videos, mindmap, transcript

# ==================== App Init ====================

app = FastAPI(
    title="VideoLearn API",
    description="REST API cho hệ thống học tập thông minh UIT Multimodal Video RAG",
    version="1.0.0",
)

# ==================== CORS Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins (dev mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Include Routers ====================

app.include_router(chat.router)
app.include_router(videos.router)
app.include_router(mindmap.router)
app.include_router(transcript.router)

# ==================== Serve Frontend Static Files ====================

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve trang chính index.html."""
    return FileResponse(FRONTEND_DIR / "index.html")


# Mount static files (CSS, JS, assets)
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
