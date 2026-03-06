#  UIT Multimodal Video RAG 

Hệ thống RAG đa phương thức (Multimodal Retrieval-Augmented Generation) hỗ trợ truy vấn và tóm tắt nội dung bài giảng video dành cho sinh viên đại học (cụ thể tại UIT).

##  Giới thiệu
Trong môi trường đại học, số lượng video bài giảng ngày càng tăng khiến việc tìm kiếm lại một công thức, định nghĩa hay lời giải thích cụ thể trở nên vô cùng mất thời gian. 

**UIT Multimodal Video RAG** được xây dựng để biến kho video bài giảng thành một "thư viện kiến thức" có thể tương tác trực tiếp. Hệ thống có khả năng "đọc" slide và "nghe" lời giảng đồng thời, từ đó trả lời câu hỏi của sinh viên kèm theo bằng chứng trích dẫn trực quan (tên video, mốc thời gian, và ảnh slide).

##  Tính năng chính
- **Trích xuất đa phương thức:** Tự động nhận dạng giọng nói tiếng Việt (ASR) và trích xuất văn bản/công thức từ slide (OCR) trong video.
- **Truy vấn thông minh:** Tìm kiếm chính xác phân đoạn video chứa nội dung liên quan nhất đến câu hỏi của người dùng từ kho dữ liệu đa video.
- **Phản hồi có kiểm chứng:** Sinh câu trả lời tự nhiên kèm theo **mốc thời gian (timestamp)** và **đường dẫn video**, giúp sinh viên bấm vào xem lại ngay lập tức.

##  Công nghệ sử dụng
- **Data Ingestion:** `OpenCV` / `MoviePy` (Trích xuất frame/audio).
- **ASR (Speech-to-Text):** `PhoWhisper` (Tối ưu cho nhận dạng tiếng Việt).
- **OCR:** `PaddleOCR` (Đọc chữ và công thức trên slide).
- **Embedding:** `Multilingual-E5`.
- **Vector Database:** `ChromaDB` / `LanceDB`.
- **LLM Generation:** `Llama-3` (Local) hoặc `Gemini 1.5 Flash` (API).
- **User Interface:** `Streamlit`.

## 📂 Cấu trúc thư mục
```text
uit_multimodal_video_rag/
├── config/                     # Cấu hình model, database
├── data/                       # Dữ liệu (Raw video, audio, frames, transcripts) - Đã được ignore
├── src/                        # Mã nguồn chính
│   ├── ingestion/              # Xử lý đa phương thức (Video, ASR, OCR)
│   ├── rag/                    # Xử lý RAG (Chunking, Embedding, Vector DB, Retriever)
│   ├── generation/             # Giao tiếp LLM và Prompts
│   └── utils/                  # Các hàm hỗ trợ
├── app/                        # Giao diện web Streamlit
├── notebooks/                  # Notebook thử nghiệm, EDA
├── docs/                       # Tài liệu thiết lập
├── scripts/                    # Script tự động hóa (build index...)
├── .env.example                # File mẫu biến môi trường
├── .gitignore                  # Cấu hình Git ignore
└── requirements.txt            # Danh sách thư viện phụ thuộc
```

##  Hướng dẫn cài đặt

**1. Clone repository**
```bash
git clone https://github.com/your-username/uit_multimodal_video_rag.git
cd uit_multimodal_video_rag
```

**2. Tạo môi trường ảo và cài đặt thư viện**
```bash
python -m venv .venv
source .venv/bin/activate  # (Trên Windows dùng: .venv\Scripts\activate)
pip install -r requirements.txt
```

**3. Thiết lập biến môi trường**
- Copy file `.env.example` thành `.env`
- Điền các thông tin API Key (nếu dùng LLM qua API như OpenAI/Gemini) vào file `.env`.

##  Hướng dẫn sử dụng

**Bước 1: Chuẩn bị dữ liệu**
- Đặt các video bài giảng (`.mp4`) vào thư mục `data/raw_videos/`.

**Bước 2: Chạy Pipeline xử lý dữ liệu (Data Ingestion & Indexing)**
Script này sẽ tự động tách âm thanh, nhận diện giọng nói (ASR), trích xuất ảnh slide (OCR), nhúng (embed) và lưu vào Vector Database.
```bash
python scripts/build_index.py
```

**Bước 3: Khởi chạy Giao diện Chatbot**
```bash
streamlit run app/streamlit_app.py
```

## 👥 Tác giả
- **[Tên của bạn/Nhóm của bạn]** - *Sinh viên trường Đại học Công nghệ Thông tin (UIT)*.
- Liên hệ: [Email của bạn]

## 📜 Giấy phép
Dự án được phân phối dưới giấy phép MIT - xem chi tiết tại file [LICENSE](LICENSE).
