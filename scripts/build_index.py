"""
Script build_index.py — Pipeline hoàn chỉnh:
1. Scan videos trong data/raw_videos/
2. Extract audio + keyframes (VideoProcessor)
3. ASR (faster-whisper) + OCR (Qwen2-VL)
4. Fusion ASR+OCR + LLM refine (MultimodalChunker)
5. Embedding (M-E5) + lưu vào Chroma DB

Chạy: python scripts/build_index.py
"""

import os
import sys
import logging

# Thêm root project vào path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ingestion.video_processor import VideoProcessor
from src.ingestion.asr_engine import ASREngine
from src.ingestion.ocr_engine import OCREngine
from src.rag.chunking import MultimodalChunker
from src.rag.embedder import E5Embedder
from src.rag.vector_db import VectorStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ====== CẤU HÌNH ĐƯỜNG DẪN ======
INPUT_FOLDER = "data/raw_videos"
AUDIO_DIR = "data/extracted_audio"
FRAME_DIR = "data/extracted_frames"
TRANSCRIPT_DIR = "data/transcripts"
VECTOR_DB_DIR = "data/vector_store"
SQLITE_DB_PATH = "data/vector_store/documents.db"

# ====== CẤU HÌNH TÙY CHỌN ======
USE_LLM_REFINE = False  # Bật/tắt LLM refine (cần GOOGLE_API_KEY)
FRAME_INTERVAL_SEC = 20  # Khoảng cách trích xuất frame (giây)


def get_video_files(input_folder: str) -> list:
    """Lấy danh sách video files."""
    if not os.path.exists(input_folder):
        logging.error(f"Không tìm thấy thư mục: {input_folder}")
        return []
    return [
        f for f in os.listdir(input_folder)
        if f.lower().endswith((".mp4", ".avi", ".mkv"))
    ]


def main():
    logging.info("=" * 60)
    logging.info("BẮT ĐẦU PIPELINE BUILD INDEX")
    logging.info("=" * 60)

    # 0. Scan video files
    video_files = get_video_files(INPUT_FOLDER)
    if not video_files:
        logging.error("Không tìm thấy video nào trong thư mục data/raw_videos/")
        return

    logging.info(f"Tìm thấy {len(video_files)} video(s).")

    # 1. Khởi tạo LLM (nếu cần refine)
    llm = None
    if USE_LLM_REFINE:
        try:
            from src.generation.llm_client import LLMClient
            llm_client = LLMClient()
            llm = llm_client.get_llm()
            logging.info("Đã khởi tạo LLM cho refine.")
        except Exception as e:
            logging.warning(f"Không thể khởi tạo LLM: {e}. Bỏ qua bước refine.")

    # 2. Khởi tạo Chunker
    chunker = MultimodalChunker(llm=llm, db_path=SQLITE_DB_PATH)

    # 3. Khởi tạo Embedder + VectorStore
    logging.info("Đang khởi tạo Multilingual-E5 Embedder...")
    embedder = E5Embedder()
    vector_store = VectorStore(
        embedder=embedder,
        persist_directory=VECTOR_DB_DIR,
        collection_name="uit_lectures",
    )

    # 4. Pipeline cho từng video
    all_documents = []

    for video_file in video_files:
        video_name = os.path.splitext(video_file)[0]
        video_path = os.path.join(INPUT_FOLDER, video_file)

        logging.info(f"\n{'=' * 40}")
        logging.info(f"Đang xử lý: {video_name}")
        logging.info(f"{'=' * 40}")

        # 4a. Extract audio + frames
        processor = VideoProcessor(
            video_path=video_path,
            output_audio_dir=AUDIO_DIR,
            output_frame_dir=FRAME_DIR,
        )
        result = processor.process(interval_sec=FRAME_INTERVAL_SEC)

        audio_path = result["audio_path"]
        frames_metadata = result["frames_metadata"]

        if audio_path is None:
            logging.error(f"Không trích xuất được audio từ {video_name}. Bỏ qua.")
            continue

        # 4b. ASR
        logging.info("--- BƯỚC ASR ---")
        asr_engine = ASREngine(output_dir=TRANSCRIPT_DIR)
        asr_json = asr_engine.transcribe(audio_path, video_name=video_name)

        if asr_json is None:
            logging.error(f"ASR thất bại cho {video_name}. Bỏ qua.")
            continue

        # 4c. OCR
        logging.info("--- BƯỚC OCR ---")
        ocr_engine = OCREngine(output_dir=TRANSCRIPT_DIR)
        ocr_json = ocr_engine.extract_text(frames_metadata, video_name)

        if ocr_json is None:
            logging.error(f"OCR thất bại cho {video_name}. Bỏ qua.")
            continue

        # 4d. Fusion + Refine
        logging.info("--- BƯỚC CHUNKING (FUSION + REFINE) ---")
        documents = chunker.process_video(asr_json, ocr_json, video_name)

        if documents:
            all_documents.extend(documents)
            chunker.save_to_db(documents)
            logging.info(f"Đã xử lý {len(documents)} chunks cho {video_name}.")

    # 5. embedding + lưu vào Chroma DB
    if all_documents:
        logging.info(f"\n--- BƯỚC EMBEDDING + LƯU VECTOR DB ---")
        logging.info(f"Tổng cộng {len(all_documents)} documents cần nhúng.")
        vector_store.add_documents(all_documents)
        logging.info("HOÀN TẤT BUILD INDEX!")
    else:
        logging.warning("Không có documents nào được tạo.")

    logging.info("=" * 60)
    logging.info("KẾT THÚC PIPELINE")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
