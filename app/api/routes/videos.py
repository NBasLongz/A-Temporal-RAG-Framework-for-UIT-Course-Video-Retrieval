"""
Routes cho danh sách video/chapters.
GET /api/chapters — Trả về danh sách chương + video bài giảng.

Tự động quét thư mục data/raw_videos/ và phân nhóm theo chương.
"""
import re
from pathlib import Path

from fastapi import APIRouter

from app.api.schemas import Chapter, Video

router = APIRouter(prefix="/api", tags=["Videos"])

# ==================== Scan Video Files ====================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
VIDEOS_DIR = PROJECT_ROOT / "data" / "raw_videos"


def parse_video_filename(filename: str) -> dict | None:
    """
    Parse tên file video để trích xuất chương và tiêu đề.
    VD: '[CS431 - Chương 1] Video 1.1 Giới thiệu môn học.mp4'
         -> chapter_num=1, title='Video 1.1 Giới thiệu môn học'
    
    VD: '[CS431 - Chương 10] Part 3_ Cơ chế Self-Attention.mp4'
         -> chapter_num=10, title='Part 3: Cơ chế Self-Attention'
    """
    # Pattern: [CS431 - Chương X] <title>.mp4
    match = re.match(
        r'\[CS431\s*-\s*Chương\s*(\d+)\]\s*(.+)\.mp4$',
        filename,
        re.IGNORECASE,
    )
    if not match:
        return None

    chapter_num = int(match.group(1))
    title = match.group(2).strip()
    # Thay thế _ bằng : cho đẹp
    title = title.replace('_', ':')

    return {
        "chapter_num": chapter_num,
        "title": title,
        "filename": filename,
    }


def scan_videos() -> list[Chapter]:
    """Quét thư mục raw_videos và tạo danh sách chapters."""
    if not VIDEOS_DIR.exists():
        return []

    # Parse tất cả video files
    video_files = sorted(VIDEOS_DIR.glob("*.mp4"))
    
    # Nhóm theo chương
    chapters_dict: dict[int, list] = {}
    for vf in video_files:
        parsed = parse_video_filename(vf.name)
        if not parsed:
            continue
        ch_num = parsed["chapter_num"]
        if ch_num not in chapters_dict:
            chapters_dict[ch_num] = []
        chapters_dict[ch_num].append(parsed)

    # Tên chương
    CHAPTER_NAMES = {
        1: "Giới thiệu và Nền tảng toán",
        2: "Mô hình học tổng quát",
        3: "Mạng CNN",
        4: "Kiến trúc CNN và biến thể",
        5: "Ứng dụng CNN",
        6: "Xử lý ngôn ngữ tự nhiên (NLP)",
        7: "Mạng RNN",
        8: "Biến thể RNN (LSTM, Bidirectional)",
        9: "Sequence-to-Sequence & Attention",
        10: "Kiến trúc Transformer",
    }

    # Build chapters
    chapters = []
    for ch_num in sorted(chapters_dict.keys()):
        vids = chapters_dict[ch_num]
        ch_name = CHAPTER_NAMES.get(ch_num, f"Chương {ch_num}")
        
        videos = []
        for idx, v in enumerate(vids):
            videos.append(
                Video(
                    id=ch_num * 100 + idx + 1,
                    title=v["title"],
                    duration="",  # Sẽ tính sau nếu cần
                    completed=False,
                    active=(ch_num == 1 and idx == 0),  # Video đầu tiên active
                    filename=v["filename"],
                )
            )

        chapters.append(
            Chapter(
                id=ch_num,
                title=f"Chương {ch_num}: {ch_name}",
                videos=videos,
            )
        )

    return chapters


# Cache kết quả scan
_chapters_cache: list[Chapter] | None = None


def get_chapters() -> list[Chapter]:
    global _chapters_cache
    if _chapters_cache is None:
        _chapters_cache = scan_videos()
    return _chapters_cache


# ==================== Endpoints ====================

@router.get("/chapters", response_model=list[Chapter])
async def list_chapters():
    """Lấy danh sách tất cả chương và video bài giảng."""
    return get_chapters()
