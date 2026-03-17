import os
import cv2
import math
import logging
from moviepy.editor import VideoFileClip

# Cấu hình logging để dễ theo dõi quá trình chạy
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class VideoProcessor:
    """
    Mô-đun Xử lý Video cốt lõi: Phân tách video (.mp4) thành âm thanh và hình ảnh.
    """
    def __init__(self, video_path: str, output_audio_dir: str, output_frame_dir: str):
        self.video_path = video_path
        self.output_audio_dir = output_audio_dir
        self.output_frame_dir = output_frame_dir
        
        # Lấy tên file gốc (không có đuôi .mp4) để đặt tên cho các file output
        self.base_name = os.path.splitext(os.path.basename(video_path))[0]
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(self.output_audio_dir, exist_ok=True)
        os.makedirs(self.output_frame_dir, exist_ok=True)

    def extract_audio(self) -> str:
        """
        Trích xuất luồng âm thanh từ video và lưu thành file .wav.
        Tối ưu hóa: Trích xuất với tần số 16000Hz (16kHz) để tương thích tốt nhất với Whisper.
        """
        audio_path = os.path.join(self.output_audio_dir, f"{self.base_name}.wav")
        logging.info(f"Đang trích xuất âm thanh từ video: {self.base_name}...")
        
        try:
            video = VideoFileClip(self.video_path)
            # Trích xuất audio với sampling rate 16kHz (chuẩn cho Whisper)
            video.audio.write_audiofile(audio_path, fps=16000, codec='pcm_s16le', verbose=False, logger=None)
            video.close()
            logging.info(f"Đã lưu file âm thanh tại: {audio_path}")
            return audio_path
        except Exception as e:
            logging.error(f"Lỗi khi trích xuất âm thanh: {e}")
            return None

    def extract_frames(self, interval_sec: int = 10) -> list:
        """
        Trích xuất khung hình từ video với chu kỳ cố định (Mặc định: 10 giây/khung hình).
        """
        logging.info(f"Đang trích xuất khung hình (mỗi {interval_sec}s) từ video: {self.base_name}...")
        
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            logging.error("Không thể mở file video.")
            return []

        fps = cap.get(cv2.CAP_PROP_FPS) # Lấy số khung hình trên giây (FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) # Tổng số khung hình
        duration = total_frames / fps # Độ dài video (giây)
        
        extracted_frames_info = []

        # Chạy vòng lặp từ 0 đến hết độ dài video, mỗi bước nhảy là interval_sec (10s)
        for current_sec in range(0, math.ceil(duration), interval_sec):
            # Tính toán vị trí của Frame tại giây thứ current_sec
            frame_id = int(current_sec * fps)
            
            # Yêu cầu OpenCV nhảy đến đúng frame_id đó
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
            ret, frame = cap.read()
            
            if ret:
                # Đặt tên file ảnh chứa timestamp để dễ đồng bộ sau này (VD: bai_1_frame_0010s.jpg)
                frame_filename = f"{self.base_name}_frame_{current_sec:04d}s.jpg"
                frame_path = os.path.join(self.output_frame_dir, frame_filename)
                
                # Lưu ảnh xuống đĩa
                cv2.imwrite(frame_path, frame)
                
                # Lưu thông tin metadata để chuyển qua module OCR/Embedding
                extracted_frames_info.append({
                    "timestamp": current_sec,
                    "image_path": frame_path
                })
            else:
                logging.warning(f"Không thể đọc khung hình tại giây thứ {current_sec}.")

        cap.release()
        logging.info(f" Đã trích xuất thành công {len(extracted_frames_info)} khung hình.")
        return extracted_frames_info

    def process(self, interval_sec: int = 10):
        """Chạy toàn bộ pipeline tiền xử lý (Audio + Frames).

        Kết quả:
        - audio_path: đường dẫn file .wav để nạp vào `ASREngine.transcribe()`.
        - frames_metadata: danh sách metadata (timestamp + image_path) để nạp vào
          `OCREngine.extract_text()`.
        """
        audio_path = self.extract_audio()
        frames_info = self.extract_frames(interval_sec=interval_sec)
        
        return {
            "video_name": self.base_name,
            "audio_path": audio_path,
            "frames_extracted": len(frames_info),
            "frames_metadata": frames_info
        }

# =======================================================
# KHỐI LỆNH TEST (Sẽ chỉ chạy khi bạn chạy trực tiếp file này)
# =======================================================
if __name__ == "__main__":
    # Khai báo đường dẫn giả định (Bạn cần có 1 file test_video.mp4 trong data/raw_videos/)
    TEST_VIDEO = "../../data/raw_videos/test_video.mp4" 
    AUDIO_OUT = "../../data/extracted_audio"
    FRAME_OUT = "../../data/extracted_frames"
    
    # Khởi tạo processor
    processor = VideoProcessor(
        video_path=TEST_VIDEO,
        output_audio_dir=AUDIO_OUT,
        output_frame_dir=FRAME_OUT
    )
    
    # Chạy trích xuất (Cắt 10s một lần)
    result = processor.process(interval_sec=10)
    
    print("\n[KẾT QUẢ XỬ LÝ]")
    print(f"- Audio: {result['audio_path']}")
    print(f"- Số khung hình thu được: {result['frames_extracted']}")
    print("\n# Lưu ý: output này có thể được dùng làm input cho ASREngine.transcribe() và OCREngine.extract_text()")