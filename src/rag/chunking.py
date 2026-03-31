import os
import json
import logging
import pandas as pd
from sqlalchemy import create_engine
from langchain_core.documents import Document

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class MultimodalChunker:
    """
    Phân đoạn dựa trên cấu trúc Slide (Slide-aligned Chunking).
    Ghép nối transcript (ASR) và text trên slide (OCR) theo mốc thời gian,
    sau đó dùng LLM refine để chỉnh sửa lỗi ASR/OCR.
    """

    def __init__(self, llm=None, db_path=None):
        """
        Args:
            llm: LLM client (ChatGoogleGenerativeAI) dùng để refine nội dung. None = bỏ qua refine.
            db_path: Đường dẫn SQLite DB để cache documents đã xử lý.
        """
        self.llm = llm
        self.db_path = db_path
        if db_path:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.engine = create_engine(f"sqlite:///{db_path}")
        else:
            self.engine = None

    def fuse_asr_ocr(self, asr_data: list, ocr_data: list, video_name: str) -> list:
        """
        Gộp dữ liệu ASR và OCR theo timestamp (slide-aligned).
        Mỗi slide OCR sẽ trở thành 1 chunk, kèm phần lời giảng ASR tương ứng.

        Args:
            asr_data: [{"start": float, "end": float, "text": str}, ...]
            ocr_data: [{"ts": int, "image": str, "text": str}, ...]
            video_name: Tên video.

        Returns:
            List[Document] — raw documents chưa refine.
        """
        raw_documents = []

        for i in range(len(ocr_data)):
            current_ocr = ocr_data[i]
            start_time = current_ocr["ts"]

            if i + 1 < len(ocr_data):
                end_time = ocr_data[i + 1]["ts"]
            else:
                end_time = asr_data[-1]["end"] if asr_data else start_time + 60

            # Tìm ASR trong khoảng thời gian (bao gồm buffer trước/sau 1 câu)
            inside_indices = [
                j for j, item in enumerate(asr_data)
                if start_time <= item["start"] < end_time
            ]

            relevant_asr = ""
            if inside_indices:
                start_idx = max(0, inside_indices[0] - 1)
                end_idx = min(len(asr_data) - 1, inside_indices[-1] + 1)
                relevant_asr = " ".join(
                    [asr_data[idx]["text"] for idx in range(start_idx, end_idx + 1)]
                )

            fused_text = (
                f"NỘI DUNG SLIDE: {current_ocr['text']}\n"
                f"NỘI DUNG GIẢNG VIÊN NÓI: {relevant_asr}"
            )

            raw_documents.append(
                Document(
                    page_content=fused_text,
                    metadata={
                        "timestamp": start_time,
                        "duration": end_time - start_time,
                        "video_name": video_name,
                    },
                )
            )

        return raw_documents

    def refine_with_llm(self, raw_documents: list) -> list:
        """
        Dùng LLM để refine nội dung từng chunk (sửa lỗi OCR/ASR, chuẩn hóa).
        Nếu self.llm is None → trả về documents gốc.
        """
        if self.llm is None:
            logging.info("Không có LLM → bỏ qua bước refine.")
            return raw_documents

        from src.generation.prompts import get_refine_prompt

        refined_results = []
        logging.info(f"Đang refine {len(raw_documents)} docs...")

        for i in range(len(raw_documents)):
            prev_content = (
                raw_documents[i - 1].page_content
                if i > 0
                else "Không có dữ liệu (Bắt đầu video)"
            )
            current_content = raw_documents[i].page_content
            next_content = (
                raw_documents[i + 1].page_content
                if i < len(raw_documents) - 1
                else "Không có dữ liệu (Kết thúc video)"
            )

            context_prompt = get_refine_prompt(prev_content, current_content, next_content)

            try:
                refined_content = self.llm.invoke(context_prompt).content
                refined_results.append(
                    Document(
                        page_content=refined_content,
                        metadata=raw_documents[i].metadata,
                    )
                )
            except Exception as e:
                logging.error(f"Lỗi refine tại index {i}: {e}")
                refined_results.append(raw_documents[i])

        return refined_results

    def process_video(self, asr_json_path: str, ocr_json_path: str, video_name: str) -> list:
        """
        Pipeline hoàn chỉnh: Load data → Fusion → Refine → Documents.
        """
        with open(asr_json_path, "r", encoding="utf-8") as f:
            asr_data = json.load(f)

        with open(ocr_json_path, "r", encoding="utf-8") as f:
            ocr_data = json.load(f)

        # Sắp xếp theo thời gian
        ocr_data.sort(key=lambda x: x["ts"])
        asr_data.sort(key=lambda x: x["start"])

        # Fusion + Refine
        raw_docs = self.fuse_asr_ocr(asr_data, ocr_data, video_name)
        refined_docs = self.refine_with_llm(raw_docs)

        return refined_docs

    def save_to_db(self, documents: list):
        """Lưu documents vào SQLite DB để cache."""
        if self.engine is None:
            logging.warning("Không có DB engine → bỏ qua lưu DB.")
            return

        data_to_save = []
        for doc in documents:
            data_to_save.append({
                "video_name": doc.metadata.get("video_name"),
                "timestamp": doc.metadata.get("timestamp"),
                "duration": doc.metadata.get("duration"),
                "content": doc.page_content,
            })

        df_docs = pd.DataFrame(data_to_save)
        df_docs.to_sql("documents", con=self.engine, if_exists="append", index=False)
        logging.info(f"Đã lưu {len(documents)} documents vào DB.")

    def load_from_db(self) -> list:
        """Đọc documents từ SQLite DB."""
        if self.engine is None:
            return []

        try:
            docs = pd.read_sql("SELECT * FROM documents", con=self.engine)
            documents = []
            for _, row in docs.iterrows():
                documents.append(
                    Document(
                        page_content=row["content"],
                        metadata={
                            "video_name": row["video_name"],
                            "timestamp": row["timestamp"],
                            "duration": row["duration"],
                        },
                    )
                )
            logging.info(f"Đã tải {len(documents)} documents từ DB.")
            return documents
        except Exception:
            return []