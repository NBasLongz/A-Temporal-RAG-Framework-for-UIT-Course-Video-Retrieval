"""
Routes cho danh sách video/chapters.
GET /api/chapters — Trả về danh sách chương + video bài giảng.
"""
from fastapi import APIRouter

from app.api.schemas import Chapter, Video

router = APIRouter(prefix="/api", tags=["Videos"])

# ==================== Mock Data ====================
# TODO: Thay bằng query từ database thật khi sẵn sàng

CHAPTERS_DATA: list[Chapter] = [
    Chapter(
        id=1,
        title="Chương 1: Giới thiệu Machine Learning",
        videos=[
            Video(id=101, title="ML là gì? Tại sao cần ML?", duration="12:30", completed=True, active=True),
            Video(id=102, title="Các loại hình học máy", duration="18:45", completed=True),
            Video(id=103, title="Quy trình xây dựng mô hình ML", duration="22:10"),
            Video(id=104, title="Công cụ và framework phổ biến", duration="15:20"),
        ],
    ),
    Chapter(
        id=2,
        title="Chương 2: Supervised Learning",
        videos=[
            Video(id=201, title="Classification vs Regression", duration="20:15"),
            Video(id=202, title="Linear Regression chi tiết", duration="25:30"),
            Video(id=203, title="Logistic Regression", duration="22:45"),
            Video(id=204, title="Decision Trees", duration="18:20"),
            Video(id=205, title="Support Vector Machines", duration="28:00"),
        ],
    ),
    Chapter(
        id=3,
        title="Chương 3: Unsupervised Learning",
        videos=[
            Video(id=301, title="K-Means Clustering", duration="19:45"),
            Video(id=302, title="Hierarchical Clustering", duration="16:30"),
            Video(id=303, title="Principal Component Analysis", duration="24:15"),
        ],
    ),
]


# ==================== Endpoints ====================

@router.get("/chapters", response_model=list[Chapter])
async def get_chapters():
    """Lấy danh sách tất cả chương và video bài giảng."""
    return CHAPTERS_DATA
