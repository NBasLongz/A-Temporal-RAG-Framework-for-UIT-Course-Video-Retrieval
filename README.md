<p align="center">
  <a href="https://www.uit.edu.vn/" title="University of Information Technology">
    <img src="https://i.imgur.com/WmMnSRt.png" alt="University of Information Technology (UIT)" width="400">
  </a>
</p>

<h1 align="center"><b>CS431 - Deep Learning Techniques And Applications</b></h1>

## Student information

| Student ID | Full name        | GitHub                                  | Email                  |
|:----------:|------------------|-----------------------------------------|------------------------|
| 23521106   | Dương Thái Ý Nhi | [y-nhi-duong](https://github.com/y-nhi-duong) | 23521106@gm.uit.edu.vn |
| 23520368   | Lương Quang Duy  | [DuyLuong2k5](https://github.com/DuyLuong2k5) | 23520368@gm.uit.edu.vn |
| 23520880   | Nguyễn Bá Long   | [NBasLongz](https://github.com/NBasLongz) | 23520880@gm.uit.edu.vn |

---

# UIT Multimodal Video RAG - VideoLearn

Hệ thống RAG đa phương thức (Multimodal Retrieval-Augmented Generation) hỗ trợ truy vấn và tóm tắt nội dung bài giảng video dành cho sinh viên đại học (cụ thể tại UIT).

## 🌟 Giới thiệu
Trong môi trường đại học, số lượng video bài giảng ngày càng tăng khiến việc tìm kiếm lại một công thức, định nghĩa hay lời giải thích cụ thể trở nên vô cùng mất thời gian. 

**VideoLearn** được xây dựng để biến kho video bài giảng thành một "thư viện kiến thức" có thể tương tác trực tiếp. Hệ thống có khả năng "đọc" slide và "nghe" lời giảng đồng thời, từ đó trả lời câu hỏi của sinh viên kèm theo bằng chứng trích dẫn trực quan (tên video, mốc thời gian, và liên kết trực tiếp đến phân đoạn video).

## ✨ Tính năng chính
- **Trích xuất đa phương thức:** Tự động nhận dạng giọng nói tiếng Việt (ASR) và trích xuất văn bản/công thức từ slide (OCR) trong video.
- **Truy vấn Hybrid Search:** Kết hợp tìm kiếm ngữ nghĩa (Semantic Search) và tìm kiếm từ khóa (BM25) để đạt độ chính xác cao nhất.
- **Phản hồi thông minh:** Sinh câu trả lời tự nhiên bằng LLM, loại bỏ các trích dẫn thừa và trình bày đẹp mắt qua Markdown.
- **Điều hướng trực tiếp:** Hiển thị danh sách các phân đoạn video liên quan, cho phép người dùng nhấn vào để trình phát tự động chuyển video và nhảy đến đúng mốc thời gian (timestamp).
- **Giao diện hiện đại:** Hỗ trợ Dark/Light mode, trình phát video tùy chỉnh, và thiết kế responsive.

## 🛠 Công nghệ sử dụng
- **ASR (Speech-to-Text):** `PhoWhisper` (Tối ưu cho nhận dạng tiếng Việt).
- **OCR:** `PaddleOCR` (Đọc chữ và công thức trên slide).
- **Embedding:** `Google Generative AI` (`gemini-embedding-2-preview`).
- **Vector Database:** `ChromaDB`.
- **LLM Generation:** `Gemini 1.5 Flash` / `Gemini 2.0 Flash Lite`.
- **Backend:** `FastAPI` (Python).
- **Frontend:** Vanilla HTML/JS + Tailwind CSS (Native).

## 📂 Cấu trúc thư mục
```text
uit_multimodal_video_rag/
├── app/                        # Ứng dụng Web
│   ├── api/                    # Backend FastAPI (Routes, RAG Service, Schemas)
│   └── frontend/               # Frontend (HTML, CSS, JS)
├── config/                     # Cấu hình hệ thống & Database
├── data/                       # Dữ liệu (Video, Audio, Vector Store, SQLite)
│   ├── raw_videos/             # Chứa các file bài giảng .mp4
│   └── vector_store/           # Chứa ChromaDB và database.db
├── src/                        # Mã nguồn xử lý AI (Ingestion, RAG, Generation)
├── notebooks/                  # Notebook quy trình triển khai mẫu
├── requirements.txt            # Danh sách thư viện phụ thuộc
└── .env                        # Biến môi trường (API Keys)
```

## 🚀 Hướng dẫn cài đặt & Sử dụng

### 1. Cài đặt môi trường
```bash
# Clone repository
git clone https://github.com/NBasLongz/A-Temporal-RAG-Framework-for-UIT-Course-Video-Retrieval.git
cd A-Temporal-RAG-Framework-for-UIT-Course-Video-Retrieval

# Tạo môi trường ảo
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 2. Cấu hình
Tạo file `.env` và thêm Google API Key của bạn:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Khởi chạy ứng dụng
```bash
# Chạy Web Server (FastAPI + Uvicorn)
python -m uvicorn app.api.main:app --reload --port 8500
```
Sau đó, truy cập **`http://127.0.0.1:8500`** trên trình duyệt.

## 📜 Giấy phép
Dự án được phân phối dưới giấy phép MIT.

---
<p align="center">Made with ❤️ by UIT Students</p>
