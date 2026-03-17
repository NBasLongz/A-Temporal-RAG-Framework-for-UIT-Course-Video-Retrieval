import os
import json
import torch
import logging
from transformers import pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ASREngine:
    """
    Mô-đun ASR: Chuyển đổi âm thanh (.wav) thành văn bản (Transcript) kèm mốc thời gian.
    """
    def __init__(self, model_id="vinai/PhoWhisper-small", output_dir="data/transcripts"):
        self.model_id = model_id
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Tự động nhận diện GPU nếu có, nếu không dùng CPU
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        logging.info(f"Đang tải mô hình ASR {self.model_id} trên {self.device}...")
        
        # Khởi tạo pipeline ASR
        self.pipe = pipeline(
            "automatic-speech-recognition", 
            model=self.model_id, 
            device=self.device
        )

    def transcribe(self, audio_path: str) -> str:
        """Thực hiện bóc băng âm thanh và lưu kết quả ra file JSON.

        Trả về đường dẫn file JSON để có thể sử dụng trong pipeline (ví dụ: xây dựng index, truy vấn nội dung).
        """
        logging.info(f"Đang bóc băng âm thanh: {audio_path}...")
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        
        try:
            # Chạy model với return_timestamps=True để lấy mốc thời gian cho từng đoạn
            result = self.pipe(audio_path, return_timestamps=True)
            
            # Lưu kết quả ra file JSON
            output_file = os.path.join(self.output_dir, f"{base_name}_audio.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
                
            logging.info(f"Đã lưu transcript âm thanh tại: {output_file}")
            return output_file
            
        except Exception as e:
            logging.error(f"Lỗi khi chạy ASR: {e}")
            return None


if __name__ == "__main__":
    asr = ASREngine(output_dir="../../data/transcripts")
    # Thay bằng đường dẫn file wav sinh ra từ video_processor.py
    # Ví dụ: dùng VideoProcessor.extract_audio() để tạo file .wav, sau đó chạy ASR.
    # asr.transcribe("../../data/extracted_audio/test_video.wav")