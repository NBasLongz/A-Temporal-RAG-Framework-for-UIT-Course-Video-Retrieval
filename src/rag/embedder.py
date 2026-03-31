import logging
from langchain_huggingface import HuggingFaceEmbeddings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Model name mặc định: Multilingual-E5-large
DEFAULT_MODEL_NAME = "intfloat/multilingual-e5-large"


class E5Embedder:
    """
    Mô-đun Embedding sử dụng Multilingual-E5-large.
    Tương thích với LangChain (HuggingFaceEmbeddings).

    Lưu ý E5 model yêu cầu:
    - passage: prefix cho document text
    - query: prefix cho query text
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        logging.info(f"Đang khởi tạo mô hình nhúng {self.model_name}...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    def get_embedding_function(self):
        """
        Trả về embedding function tương thích LangChain Chroma.
        """
        return self.embeddings

    def embed_passage(self, text: str) -> list:
        """
        Nhúng đoạn văn bản (passage) để lưu vào DB.
        E5 yêu cầu tiền tố 'passage: '.
        """
        return self.embeddings.embed_query(f"passage: {text}")

    def embed_query(self, text: str) -> list:
        """
        Nhúng câu hỏi (query) để tìm kiếm.
        E5 yêu cầu tiền tố 'query: '.
        """
        return self.embeddings.embed_query(f"query: {text}")


# Backward compatibility
Embedder = E5Embedder
