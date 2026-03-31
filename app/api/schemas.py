"""
Pydantic models cho Request/Response của REST API.
"""
from pydantic import BaseModel, Field
from typing import Optional


# ==================== Request Models ====================

class ChatRequest(BaseModel):
    """Request body cho endpoint chat."""
    query: str = Field(..., min_length=1, description="Câu hỏi của người dùng")
    video_id: Optional[int] = Field(None, description="ID video đang xem (để lọc ngữ cảnh)")


# ==================== Response Models ====================

class Source(BaseModel):
    """Nguồn trích dẫn từ RAG."""
    video_title: str
    timestamp: str
    content_snippet: str


class ChatResponse(BaseModel):
    """Response từ endpoint chat."""
    answer: str
    sources: list[Source] = []


class Video(BaseModel):
    """Thông tin một video bài giảng."""
    id: int
    title: str
    duration: str
    completed: bool = False
    active: bool = False
    filename: str = ""  # Tên file video trong data/raw_videos/


class Chapter(BaseModel):
    """Một chương gồm nhiều videos."""
    id: int
    title: str
    videos: list[Video]


class TranscriptItem(BaseModel):
    """Một dòng phụ đề."""
    time: str
    text: str


class MindmapNode(BaseModel):
    """Một node trong sơ đồ tư duy."""
    title: str
    children: list["MindmapNode"] = []


# Cho phép self-referencing model
MindmapNode.model_rebuild()


class MindmapResponse(BaseModel):
    """Response sơ đồ tư duy."""
    title: str
    children: list[MindmapNode] = []
