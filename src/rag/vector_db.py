import os
import logging
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.rag.embedder import E5Embedder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class VectorStore:
    """
    Interface với Vector Database (LangChain Chroma + Multilingual-E5).
    """

    def __init__(
        self,
        embedder: E5Embedder = None,
        persist_directory: str = "data/vector_store",
        collection_name: str = "uit_lectures",
    ):
        if embedder is None:
            embedder = E5Embedder()

        self.embedder = embedder
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        os.makedirs(persist_directory, exist_ok=True)

        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedder.get_embedding_function(),
            persist_directory=persist_directory,
        )

    def add_documents(self, documents: list):
        """
        Thêm danh sách LangChain Documents vào Chroma DB.

        Args:
            documents: List[Document] — mỗi document có page_content và metadata.
        """
        if not documents:
            logging.warning("Không có documents để thêm vào DB.")
            return

        logging.info(f"Đang lưu {len(documents)} documents vào Vector DB...")
        self.vector_store.add_documents(documents)
        logging.info("Hoàn tất lưu Database!")

    def similarity_search(self, query: str, k: int = 5) -> list:
        """
        Tìm kiếm ngữ nghĩa (semantic search).

        Args:
            query: Câu hỏi tìm kiếm.
            k: Số kết quả trả về.

        Returns:
            List[Document]
        """
        return self.vector_store.similarity_search(query=query, k=k)

    def as_retriever(self, search_type="similarity", search_kwargs=None):
        """
        Trả về LangChain Retriever.
        """
        if search_kwargs is None:
            search_kwargs = {"k": 5}
        return self.vector_store.as_retriever(
            search_type=search_type, search_kwargs=search_kwargs
        )

    def get_all_documents(self) -> list:
        """
        Lấy toàn bộ documents trong DB (cho BM25).
        """
        result = self.vector_store.get()
        documents = []
        if result and "documents" in result and result["documents"]:
            for i, doc_text in enumerate(result["documents"]):
                metadata = result["metadatas"][i] if result.get("metadatas") else {}
                documents.append(
                    Document(page_content=doc_text, metadata=metadata)
                )
        return documents