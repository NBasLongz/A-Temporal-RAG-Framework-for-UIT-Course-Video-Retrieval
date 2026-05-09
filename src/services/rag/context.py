from dataclasses import dataclass
from langchain.chat_models import init_chat_model, BaseChatModel

@dataclass
class Context:
    """Runtime context for agent dependencies.

    This contains immutable dependencies that nodes need but don't modify during runtime.

    """
    llm_model: str = "gemini-2.5-flash-lite"
    model_provider: str = "google-genai"
    temperature: float = 0.0
    retriever_top_k: int = 20
    reranker_top_k: int = 10
    reranker_url: str = "http://localhost:8001"
    n_iterations: int = 3