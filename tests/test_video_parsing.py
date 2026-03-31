import sys
import os
import re

# Thêm thư mục gốc vào path để import được app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.routes.videos import parse_video_filename

def test_parsing():
    test_cases = [
        # Format chuẩn
        ("[CS431 - Chương 1] Intro.mp4", 1, "Intro"),
        ("[CS431 - Chương 10] Transformer.mp4", 10, "Transformer"),
        # Format không có chữ Chương
        ("[CS431 - 7] RNN.mp4", 7, "RNN"),
        # Format dấu ngoặc khác
        ("[CS431] Chương 10 - Encoder.mp4", 10, "Encoder"),
        # Format NFD (Unicode tổ hợp)
        ("[CS431 - Chương 10] Part 2.mp4", 10, "Part 2"),
        # Format có chứa CS431 và số khác
        ("[CS431 - Chuang 9] Part 2_2.mp4", 9, "Part 2:2"),
    ]

    print("\n" + "="*50)
    print("START: Testing Backend Video Parsing")
    print("="*50)
    
    success_count = 0
    for filename, expected_ch, expected_title in test_cases:
        try:
            result = parse_video_filename(filename)
            if result and result["chapter_num"] == expected_ch:
                # In ra an toàn cho Windows Console (tránh UnicodeEncodeError)
                safe_name = filename.encode('ascii', 'ignore').decode()
                print(f"[PASS] {safe_name}")
                print(f"    -> Chapter: {result['chapter_num']}, Title: '{result['title'].encode('ascii', 'ignore').decode()}'")
                success_count += 1
            else:
                safe_name = filename.encode('ascii', 'ignore').decode()
                print(f"[FAIL] {safe_name}")
                if result:
                    print(f"    -> Got: Chapter {result['chapter_num']}, Title: '{result['title'].encode('ascii', 'ignore').decode()}'")
                    print(f"    -> Expected: Chapter {expected_ch}")
                else:
                    print(f"    -> Got: None")
        except Exception as e:
            print(f"[ERROR] Error processing {filename}: {e}")
    
    print("="*50)
    print(f"SUMMARY: {success_count}/{len(test_cases)} tests passed.")
    print("="*50 + "\n")

if __name__ == "__main__":
    test_parsing()
