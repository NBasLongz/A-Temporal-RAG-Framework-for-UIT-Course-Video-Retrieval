import logging
from rank_bm25 import BM25Okapi
from src.rag.vector_store import VectorStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class HybridRetriever:
    """
    Truy xuất hỗn hợp (Hybrid Search) sử dụng Vector Search (Dense) và BM25 (Sparse)
    kết hợp bằng thuật toán Reciprocal Rank Fusion (RRF).
    """
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.collection = vector_store.collection
        
        # Lấy toàn bộ document hiện có trong DB để build BM25 Index
        all_docs = self.collection.get()
        self.doc_ids = all_docs['ids']
        self.documents = all_docs['documents']
        self.metadatas = all_docs['metadatas']
        
        if self.documents:
            # Tokenize đơn giản (tách theo khoảng trắng) cho BM25
            tokenized_corpus = [doc.lower().split() for doc in self.documents]
            self.bm25 = BM25Okapi(tokenized_corpus)
        else:
            self.bm25 = None

    def retrieve(self, query: str, top_k: int = 3) -> list:
        logging.info(f"Đang tìm kiếm cho câu hỏi: '{query}'")
        
        # 1. DENSE RETRIEVAL (Tìm kiếm ngữ nghĩa bằng E5)
        # Nhớ thêm tiền tố "query: " theo chuẩn của E5 model
        query_embedding = self.vector_store.embed_model.encode(f"query: {query}").tolist()
        
        dense_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2 # Lấy dư ra để kết hợp RRF
        )
        
        dense_hits = {}
        if dense_results['ids']:
            for rank, doc_id in enumerate(dense_results['ids']):
                dense_hits[doc_id] = rank + 1 # Rank 1, 2, 3...

        # 2. SPARSE RETRIEVAL (Tìm kiếm từ khóa bằng BM25)
        sparse_hits = {}
        if self.bm25:
            tokenized_query = query.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            
            # Sắp xếp điểm BM25 giảm dần và lấy top_k * 2
            sorted_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k*2]
            for rank, idx in enumerate(sorted_indices):
                if bm25_scores[idx] > 0: # Chỉ lấy các doc có chứa từ khóa
                    doc_id = self.doc_ids[idx]
                    sparse_hits[doc_id] = rank + 1

        # 3. RECIPROCAL RANK FUSION (RRF) - Kết hợp 2 kết quả
        rrf_scores = {}
        k_const = 60 # Hằng số làm mịn chuẩn của RRF
        
        # Hợp nhất tất cả ID tài liệu tìm được
        all_retrieved_ids = set(dense_hits.keys()) | set(sparse_hits.keys())
        
        for doc_id in all_retrieved_ids:
            dense_rank = dense_hits.get(doc_id, 1000) # Nếu không có trong Dense, cho rank thấp (1000)
            sparse_rank = sparse_hits.get(doc_id, 1000)
            
            # Công thức RRF
            rrf_score = (1.0 / (k_const + dense_rank)) + (1.0 / (k_const + sparse_rank))
            rrf_scores[doc_id] = rrf_score
            
        # Sắp xếp lại theo điểm RRF giảm dần
        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[10], reverse=True)[:top_k]
        
        # 4. TRẢ VỀ KẾT QUẢ CÙNG METADATA (ĐỂ HIỂN THỊ LÊN UI)
        final_results = []
        for doc_id, score in sorted_rrf:
            idx = self.doc_ids.index(doc_id)
            final_results.append({
                "content": self.documents[idx],
                "metadata": self.metadatas[idx],
                "rrf_score": score
            })
            
        return final_results