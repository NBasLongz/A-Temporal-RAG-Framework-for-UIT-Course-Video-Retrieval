"""
Routes cho phụ đề / transcript.
GET /api/transcript/{video_id} — Trả về danh sách phụ đề bóc băng.
"""
import os
import re
import sqlite3
import logging
import unicodedata
from fastapi import APIRouter

from app.api.schemas import TranscriptItem
from app.api.routes.videos import get_chapters

router = APIRouter(prefix="/api", tags=["Transcript"])


def get_video_info_by_id(video_id: int) -> dict | None:
    """Tìm thông tin video theo ID từ danh sách chapters."""
    chapters = get_chapters()
    for chapter in chapters:
        for video in chapter.videos:
            if video.id == video_id:
                return {
                    "title": video.title,
                    "filename": video.filename,
                }
    return None


def clean_transcript_text(raw: str) -> str:
    """
    Làm sạch text chunk từ DB:
    - Bỏ block "### Nội dung Slide" và toàn bộ nội dung bên dưới nó
      (nếu chunk có cả 2 section, chỉ giữ phần Lời giảng)
    - Bỏ heading "### Lời giảng của Giảng viên"
    - Bỏ markdown: **bold**, *italic*, `code`, ### heading
    - Bỏ bullet point ký tự: * và dấu - đầu dòng
    - Gộp khoảng trắng thừa
    """

    text = raw

    # 1. Nếu có cả 2 section, chỉ lấy phần sau "### Lời giảng của Giảng viên"
    split_marker = re.split(r'###\s*Lời giảng của Giảng viên', text, maxsplit=1, flags=re.IGNORECASE)
    if len(split_marker) == 2:
        text = split_marker[1]
    else:
        # Không có marker lời giảng → bỏ toàn bộ block "### Nội dung Slide"
        text = re.sub(r'###\s*Nội dung Slide.*?(?=###|$)', '', text, flags=re.DOTALL | re.IGNORECASE)

    # 2. Bỏ các heading Markdown còn sót (##, ###, ####...)
    text = re.sub(r'^#{1,6}\s+.*$', '', text, flags=re.MULTILINE)

    # 3. Bỏ bold/italic: **text** → text, *text* → text, __text__ → text
    text = re.sub(r'\*{2}(.+?)\*{2}', r'\1', text)
    text = re.sub(r'_{2}(.+?)_{2}', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)

    # 4. Bỏ inline code: `code`
    text = re.sub(r'`(.+?)`', r'\1', text)

    # 5. Bỏ bullet point đầu dòng: * item, - item, + item, số. item
    text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # 6. Bỏ link Markdown: [text](url) → text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # 7. Gộp nhiều dòng trống thành 1
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 8. Strip khoảng trắng đầu/cuối
    text = text.strip()

    return text


# ==================== Endpoints ====================

@router.get("/transcript/{video_id}", response_model=list[TranscriptItem])
async def get_transcript(video_id: int):
    """Lấy phụ đề bóc băng cho một video từ database."""

    video_info = get_video_info_by_id(video_id)
    if not video_info:
        logging.warning(f"[Transcript] Không tìm thấy video_id={video_id}")
        return []

    db_path = os.path.join("data", "vector_store", "database.db")
    if not os.path.exists(db_path):
        logging.warning(f"[Transcript] Database không tồn tại: {db_path}")
        return []

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # So sánh tên video bằng NFC để tránh lỗi NFC/NFD Unicode
        c.execute("SELECT video_name FROM videos")
        all_videos = c.fetchall()

        target = unicodedata.normalize('NFC', video_info["title"]).lower()

        matched_video_name = None
        for (v_name,) in all_videos:
            v_name_norm = unicodedata.normalize('NFC', v_name).lower()
            if target in v_name_norm:
                matched_video_name = v_name
                break

        if not matched_video_name:
            matched_video_name = video_info["filename"].replace(".mp4", "")

        query = """
            SELECT c.content, c.timestamp
            FROM chunks c
            JOIN video_chunks vc ON c.chunk_uuid = vc.chunk_uuid
            JOIN videos v ON vc.video_uuid = v.video_uuid
            WHERE v.video_name = ?
            ORDER BY c.timestamp ASC
        """
        c.execute(query, (matched_video_name,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            logging.warning(f"[Transcript] Không tìm thấy chunks cho video: {matched_video_name}")
            return []

        transcript_data = []
        for content, ts in rows:
            cleaned = clean_transcript_text(content)

            # Bỏ qua chunk rỗng sau khi làm sạch
            if not cleaned:
                continue

            ts_int = int(float(ts))
            time_str = f"{ts_int // 60}:{ts_int % 60:02d}"

            transcript_data.append(TranscriptItem(
                time=time_str,
                text=cleaned,
            ))

        return transcript_data

    except Exception as e:
        logging.error(f"[Transcript] Lỗi đọc DB: {e}")
        return []