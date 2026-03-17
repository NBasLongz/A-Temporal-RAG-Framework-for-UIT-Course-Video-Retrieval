import chromadb
import logging
from src.rag.embedder import Embedder  # <--- Gọi file embedder vào đây

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class VectorStore:
    """
    Interface với Vector Database (ChromaDB).
    """
    def __init__(self, embedder: Embedder, db_path="data/vectordb", collection_name="uit_lectures"):
        self.embedder = embedder # Tiêm (Inject) đối tượng Embedder vào
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)

    def add_chunks(self, chunks: list, video_name: str):
        logging.info(f"Đang lưu {len(chunks)} chunks vào Vector DB...")
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            chunk_id = f"{video_name}_{chunk['chunk_id']}"
            content = chunk['content']
            
            ids.append(chunk_id)
            documents.append(content)
            
            # --- Gọi hàm từ file embedder.py ---
            embeddings.append(self.embedder.embed_passage(content))
            
            metadatas.append({
                "start_time": chunk["start_time"],
                "image_path": chunk["image_path"]
            })
            
        self.collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)
        logging.info(" Hoàn tất lưu Database!")