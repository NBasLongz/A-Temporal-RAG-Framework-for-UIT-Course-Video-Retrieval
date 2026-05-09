from __future__ import annotations

import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
PUBLIC_API_BASE_URL = os.getenv("PUBLIC_API_BASE_URL", API_BASE_URL)
APP_TITLE = "Agentic RAG Assistant"
DEFAULT_PORT = 7860
MAX_PORT_ATTEMPTS = 10
REQUEST_TIMEOUT = 120.0
GRADIO_PORT = os.getenv("GRADIO_PORT")