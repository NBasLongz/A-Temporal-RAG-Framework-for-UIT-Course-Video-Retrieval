"""
Routes cho chatbot RAG.
POST /api/chat — Nhận câu hỏi, truy xuất context (từ Vector DB), sinh câu trả lời.
"""
import logging
from fastapi import APIRouter
from app.api.schemas import ChatRequest, ChatResponse, Source
from app.api.rag_service import RagService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

router = APIRouter(prefix="/api", tags=["Chat"])

# Sinh tồn tại mức module để tái sử dụng
rag_service = RagService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint chat RAG: nhận câu hỏi, truy xuất context từ vector DB,
    sinh câu trả lời bằng LLM (Hybrid Search + Gemini).
    """
    logging.info(f"Chat query nhận được: '{request.query}'")

    # Gọi hàm đồng bộ qua thread pool (nếu request lớn có thể dùng run_in_executor)
    # Tạm thời FastAPI xử lý sync cho RagService vì nó block nhẹ chờ LLM.
    result = rag_service.query(request.query)
    
    # Map kết quả từ RagService ("answer", "related_videos") -> ChatResponse Schema
    answer = result.get("answer", "Xin lỗi, đã có lỗi ở backend.")
    related_videos = result.get("related_videos", [])
    
    sources = []
    for vid in related_videos:
        ts = vid["timestamp"]
        # Format TS to MM:SS
        ts_str = f"{ts // 60:02d}:{ts % 60:02d}"
        
        sources.append(
            Source(
                video_title=vid.get("title", "Bài giảng UIT"),
                timestamp=ts_str,
                content_snippet="[Xem video để biết chi tiết]" # Có thể pass nội dung thật nếu cần
            )
        )

    return ChatResponse(answer=answer, sources=sources)
