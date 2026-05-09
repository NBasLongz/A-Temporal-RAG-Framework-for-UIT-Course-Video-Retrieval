# Đồ án CS431 - Các kỹ thuật học sâu và ứng dụng

Dự án này là hệ thống Hỏi/Đáp (Q&A) nâng cao dựa trên kiến trúc RAG (Retrieval-Augmented Generation) và LangGraph, được xây dựng trên nền tảng FastAPI.

## Thành viên nhóm

| STT | Họ và Tên | MSSV | GitHub |
| :---: | :--- | :---: | :--- |
| 1 | Lương Quang Duy | 23520368 | [duylw](https://github.com/duylw) |
| 2 | Nguyễn Bá Long | 23520880 | [NBasLongz](https://github.com/NBasLongz) |
| 3 | Dương Thái Ý Nhi | 23521106 | [dtynhi](https://github.com/dtynhi) |

## Giới thiệu dự án

Hệ thống được thiết kế để tìm kiếm, trích xuất thông tin tư liệu (text, video) thông qua AI tự động định tuyến. Hệ thống kết hợp các công nghệ:
- **Service/API**: FastAPI, Uvicorn, Pydantic, SQLAlchemy, PostgreSQL (asyncpg).
- **Deep Learning / AI**: LangChain, LangGraph.
- **Lưu trữ & RAG**: VectorDB (Chroma/Elasticsearch), thuật toán tính toán từ khóa BM25.
- **Giao diện & Đánh giá**: Gradio UI, Langfuse, RAGAS.

## Cấu trúc thư mục thuật

- `src/api/`: Các router xử lý API endpoints.
- `src/services/rag/`: Chứa các đồ thị tác vụ LangGraph, Agent xử lý truy vấn, xếp hạng, kiểm duyệt thông tin.
- `src/models/`, `src/schemas/`: Cấu trúc dữ liệu Database và API theo kiến trúc phân tầng.
- `scripts/`: Chứa mã chuẩn bị dữ liệu và kiểm định (Evaluating RAG).
- `data/`: Dữ liệu đầu vào, kết hợp lưu trữ file text và thông tin mapping cho nội dung đa phương tiện.

## Cài đặt và Khởi chạy

Dự án được khuyến nghị chạy bằng Docker Compose để đồng bộ môi trường.

**Khởi chạy với Docker**:
```sh
docker compose up -d
docker compose watch  # Hỗ trợ Hot-reload
```
- **Dashboard cho dữ liệu** sẽ hoạt động tại: `http://localhost:8000`

Sau khi các container Docker đã khởi chạy thành công, hãy bật giao diện người dùng (User Interface) bằng lệnh sau:
```sh
uv run gradio gradio_app.py
```

- Kết nối đến giao diện tại `http://localhost:7861`

**Khởi chạy tự thủ công (dev mode)**:
Yêu cầu Python >= 3.12 và công cụ quản lý thư viện `uv`:
```sh
# Chạy server FastAPI
fastapi run main.py # Hoặc uvicorn
```

## Lưu ý
Các thiết lập biến môi trường như API Keys của LLM/VectorDB, thông tin DataBase cần được cấu hình theo template tại thư mục gốc.
