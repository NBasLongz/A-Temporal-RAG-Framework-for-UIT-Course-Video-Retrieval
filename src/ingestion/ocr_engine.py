import os
import json
import logging
from paddleocr import PaddleOCR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class OCREngine:
    """
    Mô-đun OCR: Nhận diện chữ viết, công thức từ các khung hình (frames) của video.
    """
    def __init__(self, lang='vi', output_dir="data/transcripts"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        logging.info(f"Đang tải mô hình PaddleOCR (ngôn ngữ: {lang})...")
        # use_angle_cls=True giúp lật lại chữ nếu ảnh bị nghiêng
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)

    def extract_text(self, frames_metadata: list, video_name: str) -> str:
        """Thực hiện OCR trên danh sách các khung hình và lưu kết quả JSON.

        Trả về đường dẫn file JSON để có thể sử dụng trong pipeline (ví dụ: xây dựng index, truy vấn nội dung).
        frames_metadata là list các dictionary: [{"timestamp": 10, "image_path": "..."}]
        """
        logging.info(f"Đang chạy OCR trên {len(frames_metadata)} khung hình của video {video_name}...")
        
        ocr_results = []
        
        for frame in frames_metadata:
            image_path = frame.get("image_path")
            timestamp = frame.get("timestamp")
            
            if not os.path.exists(image_path):
                logging.warning(f"Không tìm thấy ảnh: {image_path}")
                continue
                
            try:
                # Chạy OCR trên từng ảnh
                result = self.ocr.ocr(image_path, cls=True)
                
                frame_text = []
                # Kiểm tra nếu PaddleOCR tìm thấy chữ (tránh trường hợp frame trống)
                if result and result: 
                    for line in result:
                        text = line[3] # Lấy chuỗi text (Bỏ qua tọa độ bounding box và score)
                        frame_text.append(text)
                        
                # Nối tất cả các dòng chữ tìm được trong frame thành 1 câu dài
                full_text = " ".join(frame_text)
                
                ocr_results.append({
                    "timestamp": timestamp,
                    "image_path": image_path,
                    "text": full_text
                })
                
            except Exception as e:
                logging.error(f"Lỗi OCR tại ảnh {image_path}: {e}")

        # Lưu kết quả toàn bộ video ra file JSON
        output_file = os.path.join(self.output_dir, f"{video_name}_ocr.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ocr_results, f, ensure_ascii=False, indent=4)
            
        logging.info(f"Đã lưu kết quả OCR tại: {output_file}")
        return output_file

# =======================================================
# TEST NHANH
# =======================================================
if __name__ == "__main__":
    ocr_engine = OCREngine(output_dir="../../data/transcripts")
    
    # Giả lập metadata truyền từ video_processor.py (VideoProcessor.extract_frames())
    mock_frames = [
        {"timestamp": 0, "image_path": "../../data/extracted_frames/test_video_frame_0000s.jpg"},
        {"timestamp": 10, "image_path": "../../data/extracted_frames/test_video_frame_0010s.jpg"}
    ]
    
    # ocr_engine.extract_text(mock_frames, "test_video")