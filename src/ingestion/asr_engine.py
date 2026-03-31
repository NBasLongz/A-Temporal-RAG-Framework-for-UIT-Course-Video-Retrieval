import os
import json
import torch
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ASREngine:
    """
    Mô-đun ASR: Chuyển đổi âm thanh (.wav) thành văn bản (Transcript) kèm mốc thời gian.
    Sử dụng faster-whisper (large-v3) — tối ưu cho nhận dạng tiếng Việt.
    """

    def __init__(self, model_size="large-v3", output_dir="data/transcripts"):
        self.model_size = model_size
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"

        logging.info(f"Đang tải mô hình ASR faster-whisper ({self.model_size}) trên {self.device}...")

        from faster_whisper import WhisperModel
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type
        )

    def transcribe(self, audio_path: str, video_name: str = None) -> str:
        """
        Thực hiện bóc băng âm thanh và lưu kết quả ra file JSON.
        Output format: [{"start": float, "end": float, "text": str}, ...]

        Returns:
            Đường dẫn file JSON kết quả ASR.
        """
        if video_name is None:
            video_name = os.path.splitext(os.path.basename(audio_path))[0]

        output_file = os.path.join(self.output_dir, f"{video_name}_asr.json")

        # Bỏ qua nếu đã xử lý
        if os.path.exists(output_file):
            logging.info(f"Đã có transcript cho '{video_name}', bỏ qua.")
            return output_file

        logging.info(f">>>> ĐANG ASR: {video_name}")

        try:
            segments, _ = self.model.transcribe(
                audio_path,
                language="vi",
                beam_size=5,
                vad_filter=True,
            )

            transcript_result = [
                {
                    "start": round(s.start, 2),
                    "end": round(s.end, 2),
                    "text": s.text.strip()
                }
                for s in segments
            ]

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(transcript_result, f, ensure_ascii=False, indent=4)

            logging.info(f"Đã lưu transcript ASR tại: {output_file}")
            return output_file

        except Exception as e:
            logging.error(f"Lỗi khi chạy ASR: {e}")
            return None


if __name__ == "__main__":
    asr = ASREngine(output_dir="../../data/transcripts")
    # Ví dụ:
    # asr.transcribe("../../data/extracted_audio/test_video.wav", "test_video")