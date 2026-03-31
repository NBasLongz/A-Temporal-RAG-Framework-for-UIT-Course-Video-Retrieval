"""
Routes cho sơ đồ tư duy.
GET /api/mindmap/{video_id} — Trả về dữ liệu mindmap cho video.
"""
from fastapi import APIRouter

from app.api.schemas import MindmapResponse, MindmapNode

router = APIRouter(prefix="/api", tags=["Mindmap"])

# ==================== Mock Data ====================
# TODO: Thay bằng dữ liệu LLM sinh tự động từ transcript

MINDMAP_DATA: dict[int, MindmapResponse] = {
    101: MindmapResponse(
        title="Tổng quan Machine Learning",
        children=[
            MindmapNode(
                title="Định nghĩa & Ứng dụng",
                children=[
                    MindmapNode(title="Thuộc lĩnh vực Trí tuệ nhân tạo (AI)"),
                    MindmapNode(title="Tự động trích xuất quy luật từ dữ liệu"),
                    MindmapNode(title="Nhận diện ảnh, Xử lý NLP, Chatbot..."),
                ],
            ),
            MindmapNode(
                title="Phân loại Học máy",
                children=[
                    MindmapNode(title="Supervised Learning (Có giám sát)"),
                    MindmapNode(title="Unsupervised Learning (Không giám sát)"),
                    MindmapNode(title="Reinforcement Learning (Tăng cường)"),
                ],
            ),
        ],
    ),
}


# ==================== Endpoints ====================

@router.get("/mindmap/{video_id}", response_model=MindmapResponse)
async def get_mindmap(video_id: int):
    """Lấy sơ đồ tư duy cho một video bài giảng."""
    return MINDMAP_DATA.get(
        video_id,
        MindmapResponse(title="Chưa có dữ liệu", children=[]),
    )
