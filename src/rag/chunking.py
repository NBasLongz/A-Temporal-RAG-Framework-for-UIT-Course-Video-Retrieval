import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MultimodalChunker:
    """
    Phân đoạn dựa trên cấu trúc Slide (Slide-aligned Chunking).
    Ghép nối transcript (âm thanh) và text trên slide (OCR) theo mốc thời gian.
    """
    def __init__(self):
        pass

    def align_and_chunk(self, asr_json_path: str, ocr_json_path: str) -> list:
        logging.info("Đang đồng bộ hóa dữ liệu ASR và OCR thành các chunks...")
        
        with open(asr_json_path, 'r', encoding='utf-8') as f:
            asr_data = json.load(f) # Dữ liệu từ PhoWhisper
            
        with open(ocr_json_path, 'r', encoding='utf-8') as f:
            ocr_data = json.load(f) # Dữ liệu từ PaddleOCR

        chunks = []
        audio_chunks = asr_data.get('chunks', [])

        # Duyệt qua từng khung hình slide (Mỗi slide sẽ là 1 chunk)
        for i, slide in enumerate(ocr_data):
            start_time = slide['timestamp']
            # End time là timestamp của slide tiếp theo, hoặc vô cực nếu là slide cuối
            end_time = ocr_data[i+1]['timestamp'] if i + 1 < len(ocr_data) else 999999
            
            slide_text = slide.get('text', '')
            slide_image = slide.get('image_path', '')
            
            # Gom tất cả các câu nói nằm trong khoảng thời gian slide này hiển thị
            spoken_texts = []
            for audio in audio_chunks:
                # audio['timestamp'] là tuple (start, end)
                if audio['timestamp'] >= start_time and audio['timestamp'] < end_time:
                    spoken_texts.append(audio['text'])
            
            full_spoken_text = " ".join(spoken_texts)
            
            # Tạo Chunk kết hợp: [NỘI DUNG SLIDE] + [LỜI GIẢNG]
            combined_content = f"Nội dung Slide: {slide_text}\nLời giảng: {full_spoken_text}"
            
            chunks.append({
                "chunk_id": f"chunk_{i}",
                "start_time": start_time,
                "end_time": end_time if end_time != 999999 else start_time + 60,
                "image_path": slide_image,
                "content": combined_content
            })
            
        logging.info(f" Đã tạo thành công {len(chunks)} chunks đa phương thức.")
        return chunks