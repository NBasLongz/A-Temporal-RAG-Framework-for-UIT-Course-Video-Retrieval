"""
Utility functions cho dự án UIT Multimodal Video RAG.
"""

import os
import json
import yaml
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_yaml_config(config_path: str) -> dict:
    """Đọc file YAML config."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(json_path: str) -> dict:
    """Đọc file JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, json_path: str):
    """Lưu dữ liệu ra file JSON."""
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def ensure_dirs(*dirs):
    """Tạo các thư mục nếu chưa tồn tại."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def format_context_for_llm(results: list) -> str:
    """
    Format danh sách kết quả retrieval thành context string cho LLM.

    Args:
        results: List[Document] — kết quả từ retriever.

    Returns:
        String context cho prompt.
    """
    context = ""
    for i, doc in enumerate(results, 1):
        context += f"##======Kết quả {i}======\n"
        context += f"###Video: {doc.metadata.get('video_name', 'N/A')}\n"
        context += f"###Timestamp: {doc.metadata.get('timestamp', 'N/A')} - Duration: {doc.metadata.get('duration', 'N/A')}\n"
        context += f"{doc.page_content}\n"
    return context
