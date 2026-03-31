import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class LLMClient:
    """
    Client tương tác LLM (Google Gemini) cho các tác vụ:
    - Refine nội dung ASR/OCR
    - Query Rewrite
    - Sinh câu trả lời (Generation)
    """

    def __init__(self, model_name: str = "gemini-2.5-flash-lite", api_key: str = None):
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key

        self.model_name = model_name
        logging.info(f"Đang khởi tạo LLM: {self.model_name}")

        self.llm = ChatGoogleGenerativeAI(model=self.model_name)

    def invoke(self, prompt: str) -> object:
        """
        Gọi LLM với prompt và trả về response.
        """
        return self.llm.invoke(prompt)

    def generate_answer(self, query: str, context: str) -> str:
        """
        Sinh câu trả lời dựa trên context từ retrieval.

        Args:
            query: Câu hỏi của người dùng.
            context: Nội dung context từ retrieval.

        Returns:
            Câu trả lời text.
        """
        from src.generation.prompts import get_answer_prompt

        prompt = get_answer_prompt(query, context)
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logging.error(f"Lỗi khi sinh câu trả lời: {e}")
            return f"Xin lỗi, đã xảy ra lỗi: {e}"

    def get_llm(self):
        """Trả về LLM instance (cho chunking, retriever)."""
        return self.llm
