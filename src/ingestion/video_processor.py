import os
import cv2
import math
import subprocess
import logging
import numpy as np
from skimage.metrics import structural_similarity as ssim

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class VideoProcessor:
    """
    Mô-đun Xử lý Video cốt lõi: Phân tách video (.mp4) thành âm thanh và hình ảnh.
    Sử dụng SSIM để phát hiện slide mới (tránh trùng lặp frame).
    """

    def __init__(self, video_path: str, output_audio_dir: str, output_frame_dir: str):
        self.video_path = video_path
        self.output_audio_dir = output_audio_dir
        self.output_frame_dir = output_frame_dir

        self.base_name = os.path.splitext(os.path.basename(video_path))[0]

        os.makedirs(self.output_audio_dir, exist_ok=True)
        os.makedirs(self.output_frame_dir, exist_ok=True)

    def extract_audio(self) -> str:
        """
        Trích xuất âm thanh từ video bằng ffmpeg.
        Output: file .wav, 16kHz, mono (tối ưu cho Whisper).
        """
        audio_path = os.path.join(self.output_audio_dir, f"{self.base_name}.wav")

        if os.path.exists(audio_path):
            logging.info(f"Đã có audio cho '{self.base_name}', bỏ qua.")
            return audio_path

        logging.info(f"   > Đang tách audio: {os.path.basename(audio_path)}")

        try:
            command = [
                "ffmpeg", "-y", "-i", self.video_path,
                "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1",
                audio_path
            ]
            subprocess.run(command, capture_output=True, text=True, check=True)
            logging.info(f"Đã lưu file âm thanh tại: {audio_path}")
            return audio_path
        except Exception as e:
            logging.error(f"Lỗi khi trích xuất âm thanh: {e}")
            return None

    @staticmethod
    def is_new_slide(imgA, imgB, threshold=0.96):
        """
        So sánh 2 frame bằng SSIM để xác định xem đây có phải slide mới không.
        Nếu SSIM < threshold → là slide mới.
        """
        if imgB is None:
            return True
        grayA = cv2.cvtColor(imgA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imgB, cv2.COLOR_BGR2GRAY)
        if grayA.shape != grayB.shape:
            grayB = cv2.resize(grayB, (grayA.shape[1], grayA.shape[0]))
        score, _ = ssim(grayA, grayB, full=True)
        return score < threshold

    def extract_frames(self, interval_sec: int = 20) -> list:
        """
        Trích xuất keyframes từ video với slide detection (SSIM).
        Chỉ lưu frame khi phát hiện slide mới.

        Args:
            interval_sec: Khoảng cách thời gian (giây) giữa các lần kiểm tra.

        Returns:
            List metadata: [{"timestamp": int, "image_path": str}, ...]
        """
        logging.info(f">>>> ĐANG TRÍCH XUẤT FRAME: {self.base_name}")

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            logging.error("Không thể mở file video.")
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = int(total_frames / fps)

        extracted_frames_info = []
        prev_frame = None

        for ts in range(0, duration, interval_sec):
            frame_id = int(fps * ts)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
            ret, frame = cap.read()
            if not ret:
                break

            if self.is_new_slide(frame, prev_frame):
                frame_filename = f"{self.base_name}_frame_{ts}s.jpg"
                frame_path = os.path.join(self.output_frame_dir, frame_filename)
                cv2.imwrite(frame_path, frame)

                extracted_frames_info.append({
                    "timestamp": ts,
                    "image_path": frame_path
                })
                prev_frame = frame.copy()

        cap.release()
        logging.info(f" Đã trích xuất thành công {len(extracted_frames_info)} khung hình.")
        return extracted_frames_info

    def process(self, interval_sec: int = 20):
        """
        Chạy toàn bộ pipeline tiền xử lý (Audio + Frames).
        """
        audio_path = self.extract_audio()
        frames_info = self.extract_frames(interval_sec=interval_sec)

        return {
            "video_name": self.base_name,
            "audio_path": audio_path,
            "frames_extracted": len(frames_info),
            "frames_metadata": frames_info
        }


if __name__ == "__main__":
    TEST_VIDEO = "../../data/raw_videos/test_video.mp4"
    AUDIO_OUT = "../../data/extracted_audio"
    FRAME_OUT = "../../data/extracted_frames"

    processor = VideoProcessor(
        video_path=TEST_VIDEO,
        output_audio_dir=AUDIO_OUT,
        output_frame_dir=FRAME_OUT
    )

    result = processor.process(interval_sec=20)

    print("\n[KẾT QUẢ XỬ LÝ]")
    print(f"- Audio: {result['audio_path']}")
    print(f"- Số khung hình thu được: {result['frames_extracted']}")