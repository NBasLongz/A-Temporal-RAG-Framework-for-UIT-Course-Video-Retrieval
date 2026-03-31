<p align="center">

<a href="https://www.uit.edu.vn/" title="University of Information Technology">

<img src="https://i.imgur.com/WmMnSRt.png" alt="University of Information Technology (UIT)" width="400">

</a>

</p>

<h1 align="center"\><b\>CS431 - Deep Learning Techniques and Applications</b\></h1\>

## Student Information

| Student ID | Full Name        | GitHub                                  | Email                  |
|:----------:|------------------|-----------------------------------------|------------------------|
| 23521106   | Duong Thai Y Nhi | [dtynhi](https://github.com/dtynhi)     | 23521106@gm.uit.edu.vn |
| 23520368   | Luong Quang Duy  | [duylw](https://github.com/duylw)       | 23520368@gm.uit.edu.vn |
| 23520880   | Nguyen Ba Long   | [NBasLongz](https://github.com/NBasLongz) | 23520880@gm.uit.edu.vn |

-----

# UIT Multimodal Video RAG - VideoLearn

A Multimodal Retrieval-Augmented Generation (RAG) system that helps university students (specifically at UIT) easily search and summarize video lecture content.

## Introduction

In a university environment, the growing number of video lectures makes it very time-consuming to find a specific formula, definition, or explanation.

**VideoLearn** is built to turn your collection of video lectures into an interactive "knowledge library." The system can "read" presentation slides and "listen" to the lecture at the same time. Based on this, it answers students' questions and provides clear visual evidence (video name, timestamps, and direct links to the exact video segment).

## Key Features

  * **Multimodal Extraction:** Automatically recognizes Vietnamese speech (ASR) and extracts text and formulas from slides (OCR) in the videos.
  * **Hybrid Search:** Combines semantic search and keyword search (BM25) to provide the most accurate results.
  * **Smart Responses:** Generates natural-sounding answers using a Large Language Model (LLM), removes unnecessary citations, and presents the text beautifully using Markdown.
  * **Direct Navigation:** Displays a list of related video segments. Users can click on them, and the video player will automatically load the video and jump to the exact timestamp.
  * **Modern Interface:** Supports Dark/Light mode, a custom video player, and a fully responsive design.

##  Technologies Used

  * **ASR (Speech-to-Text):** `faster-whisper (large-v3)` (Optimized for Vietnamese speech recognition).
  * **OCR:** `Qwen/Qwen2-VL-2B-Instruct`.
  * **Embedding:** `bge-m3 /  multilingual-e5-large/ gemini-embedding-2-preview.
  * **Vector Database:** `ChromaDB`.
  * **LLM Generation:** `Gemini 1.5 Flash` / `Gemini 2.0 Flash Lite`.
  * **Backend:** `FastAPI` (Python).
  * **Frontend:** Vanilla HTML/JS + Tailwind CSS (Native).

## Folder Structure

```text
uit_multimodal_video_rag/
├── app/                        # Web Application
│   ├── api/                    # FastAPI Backend (Routes, RAG Service, Schemas)
│   └── frontend/               # Frontend (HTML, CSS, JS)
├── config/                     # System & Database Configuration
├── data/                       # Data (Videos, Audio, Vector Store, SQLite)
│   ├── raw_videos/             # Contains .mp4 lecture files
│   └── vector_store/           # Contains ChromaDB and database.db
├── src/                        # AI Processing Source Code (Ingestion, RAG, Generation)
├── notebooks/                  # Sample deployment notebooks
├── requirements.txt            # List of required dependencies
└── .env                        # Environment variables (API Keys)
```

## Setup & Usage Guide

### 1\. Environment Setup

```bash
# Clone the repository
git clone https://github.com/NBasLongz/A-Temporal-RAG-Framework-for-UIT-Course-Video-Retrieval.git
cd A-Temporal-RAG-Framework-for-UIT-Course-Video-Retrieval

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # For Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2\. Configuration

Create a `.env` file in the root directory and add your Google API Key:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3\. Run the Application

```bash
# Run the Web Server (FastAPI + Uvicorn)
python -m uvicorn app.api.main:app --reload --port 8500
```

After starting the server, open your web browser and go to **`http://127.0.0.1:8500`**.

## License

This project is distributed under the MIT License.

-----

<p align="center"\>Made with 🐳 by UIT Students\</p\>
