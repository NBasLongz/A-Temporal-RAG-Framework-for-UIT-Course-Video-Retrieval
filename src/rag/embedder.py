import os
import yaml
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Embedder:
    """
    Mô-đun Embedding linh hoạt:
    - Hỗ trợ Google Gemini Embeddings (ví dụ: gemini-embedding-2-preview)
    - Hỗ trợ HuggingFace (ví dụ: Multilingual-E5)
    Tự động đọc cấu hình từ 'config/model_config.yaml'.
    """

    def __init__(self, config_path: str = "config/model_config.yaml"):
        # Đọc cấu hình
        self.provider = "huggingface"
        self.model_name = "intfloat/multilingual-e5-large"
        
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if "embedding" in config:
                    self.provider = config["embedding"].get("provider", "huggingface")
                    self.model_name = config["embedding"].get("model_name", self.model_name)

        logging.info(f"Đang khởi tạo mô hình nhúng [{self.provider}]: {self.model_name}...")

        if self.provider == "google":
            # Yêu cầu GOOGLE_API_KEY trong biến môi trường
            self.embeddings = GoogleGenerativeAIEmbeddings(model=self.model_name)
        else:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

    def get_embedding_function(self):
        """Trả về embedding function tương thích LangChain Chroma."""
        return self.embeddings

    def embed_passage(self, text: str) -> list:
        if self.provider == "google":
            return self.embeddings.embed_query(text)
        return self.embeddings.embed_query(f"passage: {text}")

    def embed_query(self, text: str) -> list:
        if self.provider == "google":
            return self.embeddings.embed_query(text)
        return self.embeddings.embed_query(f"query: {text}")

# Backward compatibility
E5Embedder = Embedder
