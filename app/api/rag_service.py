import os
import sqlite3
import logging
import re
from langchain_core.documents import Document
from src.rag.embedder import Embedder
from src.rag.vector_db import VectorStore
from src.rag.retriever import HybridRetriever
from src.generation.llm_client import LLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class RagService:
    """
    Service Singleton quản lý toàn bộ AI Pipeline (Vector DB, Schema SQLite, Hybrid Search, LLM)
    Gọi 1 lần duy nhất khi server khởi động để load model vào RAM.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RagService, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
        
    def __init__(self):
        if self.initialized: return
        self.initialized = True
        
        # Đảm bảo các biến môi trường (như GOOGLE_API_KEY) đã sẵn sàng
        from dotenv import load_dotenv
        load_dotenv()
        
        logging.info("Khởi tạo RAG Service (Embedder, LLM, VectorDB)...")
        # 1. Khởi tạo LLM & Embedder (Google Gemini đã setup trong config)
        self.embedder = Embedder()
        self.llm_client = LLMClient()
        
        # 2. Kết nối ChromaDB
        db_dir = "data/vector_store"
        self.vector_store = VectorStore(
            embedder=self.embedder,
            persist_directory=os.path.join(db_dir, "chroma_langchain"),
            collection_name="default"  # Khớp với local build của notebook
        )
        
        # 3. Load Documents từ SQLite để build BM25
        self.documents = self._load_documents_from_sqlite(os.path.join(db_dir, "database.db"))
        
        # 4. Tạo Retriever cho Hybrid Search
        self.retriever = HybridRetriever(
            vector_store=self.vector_store,
            documents=self.documents,
            llm=self.llm_client.get_llm() # truyền LLM vào để cho phép query rewrite
        )
        
    def _load_documents_from_sqlite(self, db_path: str) -> list:
        """Đọc và join bảng sqlite để chuyển thành Langchain Documents (phục vụ BM25)"""
        docs = []
        if not os.path.exists(db_path):
            logging.error(f"Không tìm thấy SQLite DB tại {db_path}!")
            return docs
            
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            # Join 3 bảng để lấy ra context, timestamp và video source
            query = """
                SELECT c.content, c.timestamp, c.duration, v.video_name, v.video_url, c.chunk_uuid
                FROM chunks c
                JOIN video_chunks vc ON c.chunk_uuid = vc.chunk_uuid
                JOIN videos v ON vc.video_uuid = v.video_uuid
            """
            c.execute(query)
            rows = c.fetchall()
            
            for row in rows:
                content, ts, duration, video_name, video_url, chunk_uuid = row
                docs.append(Document(
                    page_content=content,
                    metadata={
                        "timestamp": ts,
                        "duration": duration,
                        "video_name": video_name,
                        "video_url": video_url,
                        "chunk_uuid": chunk_uuid
                    }
                ))
            conn.close()
            logging.info(f"Đã load {len(docs)} documents từ SQLite cho BM25 index.")
        except Exception as e:
            logging.error(f"Lỗi đọc DB: {e}")
            
        return docs
        
    def query(self, user_query: str, top_k: int = 5) -> dict:
        """Thực hiện tìm kiếm câu trả lời"""
        try:
            # Retriever sẽ tự gọi query_rewrite -> bm25 + chroma -> RRF fusion
            results = self.retriever.retrieve(query=user_query, top_k=top_k, rewrite=True)
            
            if not results:
                return {
                    "answer": "Xin lỗi, tôi không tìm thấy thông tin nào phù hợp trong các bài giảng.",
                    "related_videos": []
                }
                
            # Đưa nội dung các kết quả vào Context cho Prompt bằng list/markdown
            context_text = ""
            for i, doc in enumerate(results, 1):
                v_name = doc.metadata.get("video_name", "Unknown")
                ts = doc.metadata.get("timestamp", 0)
                context_text += f"\n--- TÀI LIỆU {i} ---\nNguồn: Video '{v_name}' (Phút thứ {ts//60}:{ts%60:02d})\nNội dung:\n{doc.page_content}\n"
                
            # Sinh câu trả lời logic, trôi chảy bằng Gemini
            answer = self.llm_client.generate_answer(query=user_query, context=context_text)
            
            # Map kết quả video để trả về Frontend (video ID để redirect)
            related_vids = []
            seen = set() # Tránh trùng video name
            
            for doc in results:
                v_name = doc.metadata.get("video_name", "")
                ts = doc.metadata.get("timestamp", 0)
                
                # Cần trích xuất "Chuong X Part Y..." vì frontend map
                key = f"{v_name}_{ts}"
                if key not in seen:
                    seen.add(key)
                    
                    # Format title giống hệt UI parse_video_filename
                    formatted_title = v_name
                    if "]" in v_name:
                        parts = v_name.split("]", 1)
                        if len(parts) == 2:
                            formatted_title = parts[1].strip().replace('_', ':')

                    # Tác file là video_name + .mp4
                    filename = v_name + ".mp4" if not v_name.endswith(".mp4") else v_name

                    related_vids.append({
                        "filename": filename, # Tên file video để frontend so khớp
                        "title": formatted_title,
                        "timestamp": ts,
                        "relevance_score": 0.99  # Mock score or mapping from RRF 
                    })
                    
            return {
                "answer": answer,
                "related_videos": related_vids
            }
            
        except Exception as e:
            logging.error(f"Lỗi khi query RAG: {e}")
            return {
                "answer": f"Đã xảy ra lỗi nội bộ trong hệ thống AI: {e}",
                "related_videos": []
            }
