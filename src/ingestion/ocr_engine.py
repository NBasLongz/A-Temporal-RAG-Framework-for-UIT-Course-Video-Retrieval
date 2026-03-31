import os
import json
import torch
import logging
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class OCREngine:
    """
    Mô-đun OCR: Nhận diện văn bản từ các khung hình (frames) của video.
    Sử dụng Qwen2-VL-2B-Instruct cho khả năng đọc slide tiếng Việt chính xác.
    """

    def __init__(self, model_id="Qwen/Qwen2-VL-2B-Instruct", output_dir="data/transcripts"):
        self.model_id = model_id
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        logging.info(f"Đang tải mô hình OCR {self.model_id}...")

        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            self.model_id, torch_dtype="auto", device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(self.model_id)

    def extract_text(self, frames_metadata: list, video_name: str) -> str:
        """
        Thực hiện OCR trên danh sách các khung hình và lưu kết quả JSON.
        frames_metadata: [{"timestamp": int, "image_path": str}, ...]

        Returns:
            Đường dẫn file JSON kết quả OCR.
        """
        output_file = os.path.join(self.output_dir, f"{video_name}_ocr.json")

        # Bỏ qua nếu đã xử lý
        if os.path.exists(output_file):
            logging.info(f"Đã có OCR cho '{video_name}', bỏ qua.")
            return output_file

        logging.info(f">>>> ĐANG CHẠY OCR: {video_name}")

        ocr_results = []

        for frame in frames_metadata:
            image_path = frame.get("image_path")
            timestamp = frame.get("timestamp")

            if not os.path.exists(image_path):
                logging.warning(f"Không tìm thấy ảnh: {image_path}")
                continue

            try:
                image = Image.open(image_path)
                f_name = os.path.basename(image_path)

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": image_path},
                            {"type": "text", "text": "Trích xuất văn bản tiếng Việt."}
                        ]
                    }
                ]

                text = self.processor.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                inputs = self.processor(
                    text=[text], images=[image], padding=True, return_tensors="pt"
                ).to(self.model.device)

                with torch.no_grad():
                    ids = self.model.generate(**inputs, max_new_tokens=512)
                    res = self.processor.batch_decode(
                        ids[:, inputs.input_ids.shape[1]:],
                        skip_special_tokens=True
                    )[0]

                ocr_results.append({
                    "ts": timestamp,
                    "image": f_name,
                    "text": res
                })

            except Exception as e:
                logging.error(f"Lỗi OCR tại ảnh {image_path}: {e}")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(ocr_results, f, ensure_ascii=False, indent=4)

        logging.info(f"Đã lưu kết quả OCR tại: {output_file}")
        return output_file


if __name__ == "__main__":
    ocr_engine = OCREngine(output_dir="../../data/transcripts")

    mock_frames = [
        {"timestamp": 0, "image_path": "../../data/extracted_frames/test_video_frame_0000s.jpg"},
        {"timestamp": 10, "image_path": "../../data/extracted_frames/test_video_frame_0010s.jpg"}
    ]
    # ocr_engine.extract_text(mock_frames, "test_video")