"""
Routes cho sơ đồ tư duy.
GET /api/mindmap/{video_id} — Sinh sơ đồ tư duy bằng LLM từ nội dung video.
"""
import json
import logging
import re
from fastapi import APIRouter

from app.api.schemas import MindmapResponse, MindmapNode
from app.api.routes.videos import get_chapters

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

router = APIRouter(prefix="/api", tags=["Mindmap"])


def get_video_info_by_id(video_id: int) -> dict | None:
    """Tìm thông tin video theo ID từ danh sách chapters."""
    chapters = get_chapters()
    for chapter in chapters:
        for video in chapter.videos:
            if video.id == video_id:
                return {
                    "title": video.title,
                    "filename": video.filename,
                    "chapter_title": chapter.title,
                    "chapter_id": chapter.id,
                }
    return None


def get_video_content_from_db(video_filename: str) -> str:
    """Lấy nội dung transcript/chunks từ SQLite cho video."""
    import sqlite3
    import os

    db_path = os.path.join("data", "vector_store", "database.db")
    if not os.path.exists(db_path):
        logging.warning(f"[Mindmap] Database không tồn tại: {db_path}")
        return ""

    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        # Khắc phục lỗi unicode SQLite NFD/NFC
        c.execute("SELECT video_name FROM videos")
        all_videos = c.fetchall()
        
        import unicodedata
        # Tìm lại target title từ filename để khớp với title
        import re
        match = re.match(r'^\[(.*?)\]\s*(.*)\.mp4$', video_filename)
        title = match.group(2).strip() if match else video_filename.replace(".mp4", "")
        
        target = unicodedata.normalize('NFC', title).lower()
        matched_video_name = None
        for (v_name,) in all_videos:
            v_name_norm = unicodedata.normalize('NFC', v_name).lower()
            if target in v_name_norm:
                matched_video_name = v_name
                break
                
        if not matched_video_name:
            matched_video_name = video_filename.replace(".mp4", "")

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
            logging.warning(f"[Mindmap] Không tìm thấy nội dung cho video: {video_name}")
            return ""

        # Gộp các chunks thành một chuỗi content
        content_parts = []
        for content, ts in rows:
            ts_min = ts // 60 if isinstance(ts, int) else 0
            ts_sec = ts % 60 if isinstance(ts, int) else 0
            content_parts.append(f"[{ts_min:02d}:{ts_sec:02d}] {content}")

        full_content = "\n\n".join(content_parts)

        # Giới hạn content (tránh quá dài cho LLM)
        if len(full_content) > 15000:
            full_content = full_content[:15000] + "\n\n[... nội dung còn lại bị cắt bớt ...]"

        logging.info(f"[Mindmap] Lấy được {len(rows)} chunks cho video: {video_name}")
        return full_content

    except Exception as e:
        logging.error(f"[Mindmap] Lỗi đọc DB: {e}")
        return ""


def generate_mindmap_with_llm(video_title: str, chapter_title: str, content: str) -> MindmapResponse:
    """Gọi LLM để sinh sơ đồ tư duy từ nội dung video."""
    from app.api.rag_service import RagService

    rag_service = RagService()

    prompt = f"""Bạn là trợ lý giáo dục. Hãy tạo một sơ đồ tư duy (mind map) cho bài giảng sau đây.

### Thông tin bài giảng:
- Chương: {chapter_title}
- Bài: {video_title}

### Nội dung bài giảng:
{content}

### Yêu cầu:
1. Tạo sơ đồ tư duy dưới dạng JSON cấu trúc cây (tree).
2. Mỗi node có "title" (tiêu đề ngắn gọn) và "children" (mảng các node con, có thể rỗng).  
3. Node gốc là tên chủ đề chính của bài giảng.
4. Tối đa 3 cấp độ sâu, mỗi node cha tối đa 5 node con.
5. Tiêu đề mỗi node nên ngắn gọn (dưới 50 ký tự) nhưng đủ ý.
6. Bao gồm các khái niệm chính, phương pháp, ví dụ quan trọng.

### Định dạng trả về (CHỈ trả về JSON, không kèm text giải thích):
{{
    "title": "Tên chủ đề chính",
    "children": [
        {{
            "title": "Khái niệm 1",
            "children": [
                {{"title": "Chi tiết 1.1", "children": []}},
                {{"title": "Chi tiết 1.2", "children": []}}
            ]
        }},
        {{
            "title": "Khái niệm 2",
            "children": []
        }}
    ]
}}
"""

    try:
        response = rag_service.llm_client.invoke(prompt)
        response_text = response.content.strip()

        # Extract JSON từ response (có thể có markdown code block)
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response_text)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # Thử parse trực tiếp
            json_str = response_text

        data = json.loads(json_str)

        def parse_node(node_data) -> MindmapNode:
            children = []
            for child in node_data.get("children", []):
                children.append(parse_node(child))
            return MindmapNode(title=node_data.get("title", ""), children=children)

        root_children = [parse_node(c) for c in data.get("children", [])]
        return MindmapResponse(title=data.get("title", video_title), children=root_children)

    except json.JSONDecodeError as e:
        logging.error(f"[Mindmap] LLM trả về JSON không hợp lệ: {e}")
        logging.error(f"[Mindmap] Response text: {response_text[:500]}")
        return MindmapResponse(title=video_title, children=[
            MindmapNode(title="⚠️ Lỗi parse dữ liệu từ AI", children=[
                MindmapNode(title="Vui lòng thử lại")
            ])
        ])
    except Exception as e:
        logging.error(f"[Mindmap] Lỗi sinh mindmap: {e}")
        return MindmapResponse(title=video_title, children=[
            MindmapNode(title="⚠️ Lỗi khi tạo sơ đồ tư duy", children=[
                MindmapNode(title=str(e))
            ])
        ])


# ==================== Endpoints ====================

@router.get("/mindmap/{video_id}", response_model=MindmapResponse)
async def get_mindmap(video_id: int):
    """Sinh sơ đồ tư duy cho một video bài giảng bằng LLM."""
    logging.info(f"[Mindmap] Yêu cầu mindmap cho video_id={video_id}")

    # 1. Tìm thông tin video
    video_info = get_video_info_by_id(video_id)
    if not video_info:
        logging.warning(f"[Mindmap] Không tìm thấy video_id={video_id}")
        return MindmapResponse(
            title="Không tìm thấy video",
            children=[MindmapNode(title="Video ID không tồn tại trong hệ thống")]
        )

    # 2. Lấy nội dung bài giảng từ DB
    content = get_video_content_from_db(video_info["filename"])

    if not content:
        # Fallback: Sinh mindmap chung cho chapter dù không có nội dung chi tiết
        logging.info(f"[Mindmap] Không có transcript, dùng thông tin cơ bản")
        return generate_mindmap_with_llm(
            video_title=video_info["title"],
            chapter_title=video_info["chapter_title"],
            content=f"Bài giảng '{video_info['title']}' thuộc {video_info['chapter_title']}. Hãy tạo sơ đồ tư duy tổng quát dựa trên tên bài giảng."
        )

    # 3. Sinh mindmap bằng LLM
    return generate_mindmap_with_llm(
        video_title=video_info["title"],
        chapter_title=video_info["chapter_title"],
        content=content
    )
