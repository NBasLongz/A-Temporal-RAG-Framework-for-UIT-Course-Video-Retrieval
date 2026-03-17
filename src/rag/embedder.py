import logging
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Embedder:
    """
    Mô-đun Embedding: Sinh vector nhúng cho tài liệu (passage) và câu hỏi (query).
    """
    def __init__(self, model_name: str = 'intfloat/multilingual-e5-large'):
        self.model_name = model_name
        logging.info(f"Đang khởi tạo mô hình nhúng {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)

    def embed_passage(self, text: str) -> list:
        """
        Dùng để nhúng các đoạn chunk văn bản trước khi lưu vào Database.
        Lưu ý: E5 model yêu cầu thêm tiền tố 'passage: ' cho văn bản lưu trữ.
        """
        return self.model.encode(f"passage: {text}").tolist()

    def embed_query(self, text: str) -> list:
        """
        Dùng để nhúng câu hỏi của người dùng lúc tìm kiếm.
        Lưu ý: E5 model yêu cầu thêm tiền tố 'query: ' cho câu hỏi.
        """
        return self.model.encode(f"query: {text}").tolist()
