import logging
from langchain_community.retrievers import BM25Retriever
from src.rag.vector_db import VectorStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class HybridRetriever:
    """
    Truy xuất hỗn hợp (Hybrid Search):
    - Dense Retrieval: Tìm kiếm ngữ nghĩa qua Chroma (Multilingual-E5).
    - Sparse Retrieval: Tìm kiếm từ khóa qua BM25.
    - Kết hợp bằng Reciprocal Rank Fusion (RRF).
    - Hỗ trợ Query Rewrite bằng LLM.
    """

    def __init__(self, vector_store: VectorStore, documents: list = None, llm=None):
        """
        Args:
            vector_store: VectorStore instance (LangChain Chroma).
            documents: List[Document] — dùng để build BM25 index.
            llm: LLM client để query rewrite. None = không rewrite.
        """
        self.vector_store = vector_store
        self.llm = llm

        # Load documents cho BM25
        if documents is None:
            documents = vector_store.get_all_documents()

        self.documents = documents

        if self.documents:
            self.bm25_retriever = BM25Retriever.from_documents(self.documents)
        else:
            self.bm25_retriever = None

    def query_rewrite(self, query: str) -> str:
        """
        Viết lại câu truy vấn bằng LLM để tối ưu tìm kiếm.
        """
        if self.llm is None:
            return query

        from src.generation.prompts import get_query_rewrite_prompt

        prompt = get_query_rewrite_prompt(query)
        try:
            refined_query = self.llm.invoke(prompt).content
            logging.info(f"Query rewrite: '{query}' → '{refined_query}'")
            return refined_query
        except Exception as e:
            logging.error(f"Lỗi query rewrite: {e}")
            return query

    def hybrid_search(self, query: str, k: int = 5) -> list:
        """
        Tìm kiếm hybrid: Semantic + BM25 + RRF.

        Args:
            query: Câu hỏi (đã rewrite hoặc chưa).
            k: Số kết quả trả về.

        Returns:
            List[Document] — top-k documents theo điểm RRF.
        """
        logging.info(f"Đang tìm kiếm cho câu hỏi: '{query}'")

        # 1. SEMANTIC SEARCH (Dense)
        semantic_results = self.vector_store.similarity_search(query=query, k=k * 2)

        # 2. BM25 SEARCH (Sparse)
        bm25_results = []
        if self.bm25_retriever:
            self.bm25_retriever.k = k * 2
            bm25_results = self.bm25_retriever.invoke(query)

        # 3. RECIPROCAL RANK FUSION (RRF)
        rrf_scores = {}
        k_const = 60  # Hằng số làm mịn chuẩn RRF

        def add_results_to_rrf(results, weight=1.0):
            for rank, doc in enumerate(results):
                doc_id = doc.page_content  # Dùng nội dung làm key để deduplicate

                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = {"doc": doc, "score": 0.0}

                rrf_scores[doc_id]["score"] += weight * (1.0 / (rank + 1 + k_const))

        add_results_to_rrf(semantic_results)
        add_results_to_rrf(bm25_results)

        # Sắp xếp theo điểm RRF giảm dần
        reranked_docs = sorted(
            rrf_scores.values(), key=lambda x: x["score"], reverse=True
        )

        # Lấy Top K
        final_results = [item["doc"] for item in reranked_docs[:k]]
        return final_results

    def retrieve(self, query: str, top_k: int = 5, rewrite: bool = True) -> list:
        """
        Pipeline retrieval hoàn chỉnh: Query Rewrite → Hybrid Search.

        Args:
            query: Câu hỏi của người dùng.
            top_k: Số kết quả trả về.
            rewrite: Có viết lại query không.

        Returns:
            List[Document]
        """
        if rewrite:
            query = self.query_rewrite(query)

        return self.hybrid_search(query, k=top_k)