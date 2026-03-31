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
    Parse tên file video một cách linh hoạt.
    Hỗ trợ: '[CS431 - Chương 1] ...', '[CS431 - Chuang 10] ...', v.v.
    """
    if not filename.endswith(".mp4"):
        return None

    # Lấy phần trong ngoặc vuông đầu tiên
    if "]" not in filename:
        return None
    
    # Loại bỏ mã môn học CS431 để tránh nhầm lẫn (ví dụ: [CS431] -> [)
    temp_name = re.sub(r'\[\s*CS\s*431\s*[-]*\s*', '[', filename, flags=re.IGNORECASE)
    
    # Tìm số đầu tiên xuất hiện sau khi đã loại bỏ CS431
    match = re.search(r'(\d+)', temp_name)
    if match:
        chapter_num = int(match.group(1))
    else:
        return None
        
    # Tiêu đề là phần sau dấu ]
    title = filename.split("]", 1)[-1].replace(".mp4", "").strip() if "]" in filename else filename.replace(".mp4", "")
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
