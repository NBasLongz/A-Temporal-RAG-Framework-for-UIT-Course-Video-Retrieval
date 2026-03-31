"""
Routes cho phụ đề / transcript.
GET /api/transcript/{video_id} — Trả về danh sách phụ đề bóc băng.
"""
from fastapi import APIRouter

from app.api.schemas import TranscriptItem

router = APIRouter(prefix="/api", tags=["Transcript"])

# ==================== Mock Data ====================
# TODO: Thay bằng dữ liệu ASR thật từ data/transcripts/

TRANSCRIPT_DATA: dict[int, list[TranscriptItem]] = {
    101: [
        TranscriptItem(time="0:00", text="Chào mừng các bạn đến với bài giảng đầu tiên về Machine Learning."),
        TranscriptItem(time="1:30", text="Hôm nay chúng ta sẽ tìm hiểu Machine Learning là gì và tại sao nó lại cực kỳ quan trọng hiện nay."),
        TranscriptItem(time="3:15", text="Machine Learning là một nhánh của AI, cho phép máy tính tự động học từ dữ liệu mà không cần lập trình rõ ràng."),
        TranscriptItem(time="5:45", text="Có 3 loại hình chính: Học có giám sát (Supervised), Học không giám sát (Unsupervised) và Học tăng cường."),
        TranscriptItem(time="8:20", text="Trong Supervised Learning, chúng ta cần dữ liệu đã được gán nhãn sẵn (labeled data) để huấn luyện mô hình."),
    ],
}


# ==================== Endpoints ====================

@router.get("/transcript/{video_id}", response_model=list[TranscriptItem])
async def get_transcript(video_id: int):
    """Lấy phụ đề bóc băng cho một video."""
    return TRANSCRIPT_DATA.get(video_id, [])
