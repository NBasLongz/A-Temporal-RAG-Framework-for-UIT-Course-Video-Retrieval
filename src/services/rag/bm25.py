import re
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
import pickle
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")

def custom_preprocess(text: str) -> list[str]:
    return re.sub(r'[^\w\s]', '', text).lower().split()

def make_bm25_retriever() -> BM25Retriever:
    """Factory function to create a BM25Service instance."""
    try:
        with open(os.path.join(DATA_DIR, 'vector_data_export.pkl'), 'rb') as f:
            loaded_data = pickle.load(f)

        bm25_retriever = BM25Retriever.from_documents(
            documents=[
                Document(
                    id=loaded_data['ids'][i],
                    page_content=loaded_data['documents'][i],
                    metadata=loaded_data['metadatas'][i]
                )
                for i in range(len(loaded_data['ids']))
            ],
            preprocess=custom_preprocess
        )

        return bm25_retriever
    except Exception as e:
        print(f"Error creating BM25 retriever: {e}")
        raise