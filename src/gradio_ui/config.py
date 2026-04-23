from __future__ import annotations

import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
APP_TITLE = "Agentic RAG Assistant"
DEFAULT_PORT = 7860
MAX_PORT_ATTEMPTS = 10
REQUEST_TIMEOUT = 120.0
GRADIO_PORT = os.getenv("GRADIO_PORT")