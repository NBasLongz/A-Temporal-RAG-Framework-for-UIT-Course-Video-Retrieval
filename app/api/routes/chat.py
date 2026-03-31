"""
Routes cho chatbot RAG.
POST /api/chat — Nhận câu hỏi, truy xuất context, sinh câu trả lời.
"""
import asyncio
import logging

from fastapi import APIRouter

from app.api.schemas import ChatRequest, ChatResponse, Source

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

router = APIRouter(prefix="/api", tags=["Chat"])

# ==================== RAG Integration ====================
# TODO: Khi RAG pipeline sẵn sàng, uncomment và sử dụng code thật bên dưới.
#
# from src.rag.vector_db import VectorStore
# from src.rag.retriever import HybridRetriever
# from src.generation.llm_client import LLMClient
#
# vector_store = VectorStore()
# llm_client = LLMClient()
# retriever = HybridRetriever(vector_store=vector_store, llm=llm_client.get_llm())


async def mock_rag_query(query: str) -> ChatResponse:
    """
    Mock RAG query — giả lập độ trễ và trả kết quả mẫu.
    Sẽ được thay thế bằng HybridRetriever + LLMClient thật.
    """
    # Giả lập thời gian xử lý RAG
    await asyncio.sleep(1.2)

    if "machine learning" in query.lower() or "ml" in query.lower():
        return ChatResponse(
            answer=(
                "**Machine Learning** (Học máy) là một nhánh của Trí tuệ nhân tạo (AI), "
                "cho phép máy tính tự động học hỏi và cải thiện từ dữ liệu mà không cần "
                "lập trình rõ ràng từng quy tắc.\n\n"
                "Có **3 loại hình chính**:\n"
                "1. **Supervised Learning** — Học có giám sát (cần labeled data)\n"
                "2. **Unsupervised Learning** — Học không giám sát\n"
                "3. **Reinforcement Learning** — Học tăng cường\n\n"
                "📌 *Được nhắc đến tại mốc 03:15 trong video.*"
            ),
            sources=[
                Source(
                    video_title="ML là gì? Tại sao cần ML?",
                    timestamp="03:15",
                    content_snippet="Machine Learning là một nhánh của AI, cho phép máy tính tự động học từ dữ liệu.",
                ),
            ],
        )

    if "supervised" in query.lower():
        return ChatResponse(
            answer=(
                "**Supervised Learning** (Học có giám sát) là phương pháp học máy "
                "sử dụng dữ liệu đã được gán nhãn (labeled data) để huấn luyện mô hình.\n\n"
                "Gồm 2 bài toán chính:\n"
                "- **Classification** — Phân loại (đầu ra rời rạc)\n"
                "- **Regression** — Hồi quy (đầu ra liên tục)\n\n"
                "📌 *Được giải thích chi tiết tại mốc 05:45.*"
            ),
            sources=[
                Source(
                    video_title="ML là gì? Tại sao cần ML?",
                    timestamp="05:45",
                    content_snippet="Trong Supervised Learning, chúng ta cần dữ liệu đã được gán nhãn sẵn.",
                ),
            ],
        )

    # Fallback
    return ChatResponse(
        answer=(
            f'Đã trích xuất thông tin liên quan đến **"{query}"** từ cơ sở dữ liệu bài giảng.\n\n'
            "Vui lòng xem các đoạn video gợi ý bên dưới để tìm hiểu thêm chi tiết."
        ),
        sources=[
            Source(
                video_title="ML là gì? Tại sao cần ML?",
                timestamp="00:00",
                content_snippet="Chào mừng các bạn đến với bài giảng đầu tiên về Machine Learning.",
            ),
        ],
    )


# ==================== Real RAG Query (uncomment khi sẵn sàng) ====================

# async def real_rag_query(query: str) -> ChatResponse:
#     """Truy xuất RAG thật từ ChromaDB + LLM."""
#     # Chạy trong thread pool vì retriever và LLM đều là sync
#     loop = asyncio.get_event_loop()
#
#     # Retrieve context
#     docs = await loop.run_in_executor(None, retriever.retrieve, query, 5, True)
#     context = "\n\n".join([
#         f"[Video: {d.metadata.get('video_name', 'N/A')} | Timestamp: {d.metadata.get('timestamp', 'N/A')}]\n{d.page_content}"
#         for d in docs
#     ])
#
#     # Generate answer
#     answer = await loop.run_in_executor(None, llm_client.generate_answer, query, context)
#
#     sources = [
#         Source(
#             video_title=d.metadata.get("video_name", "N/A"),
#             timestamp=d.metadata.get("timestamp", "00:00"),
#             content_snippet=d.page_content[:150] + "...",
#         )
#         for d in docs
#     ]
#
#     return ChatResponse(answer=answer, sources=sources)


# ==================== Endpoint ====================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint chat RAG: nhận câu hỏi, truy xuất context từ vector DB,
    sinh câu trả lời bằng LLM.
    """
    logging.info(f"Chat query: '{request.query}'")

    # Dùng mock (thay bằng real_rag_query khi sẵn sàng)
    response = await mock_rag_query(request.query)

    return response
