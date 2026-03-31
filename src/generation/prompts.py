"""
Tập hợp các prompt templates dùng trong pipeline RAG.
"""


def get_refine_prompt(prev_content: str, current_content: str, next_content: str) -> str:
    """
    Prompt refine nội dung ASR + OCR bằng LLM.
    Sử dụng ngữ cảnh 3 thời điểm liên tiếp để chỉnh sửa.
    """
    return f"""
Dưới đây là nội dung bài giảng tại 3 thời điểm liên tiếp (bao gồm Slide và Lời giảng):

[TRƯỚC ĐÓ]
{prev_content}

[HIỆN TẠI - CẦN TINH CHỈNH TOÀN BỘ]
{current_content}

[TIẾP THEO]
{next_content}

### Nhiệm vụ:
Dựa vào ngữ cảnh trước và sau, hãy biên tập lại toàn bộ nội dung của thời điểm [HIỆN TẠI] bao gồm cả phần nội dung Slide và Lời giảng của giảng viên.

### Yêu cầu cụ thể:
1. **Đối với Nội dung Slide:**
   - Sửa các lỗi chính tả do nhận diện hình ảnh (OCR) sai.
   - Trình bày lại các ý trên slide dưới dạng danh sách (bullet points) để rõ ràng, rành mạch.
   - Đảm bảo các thuật ngữ trên Slide đồng nhất với Lời giảng.

2. **Đối với Lời giảng của Giảng viên:**
   - Khắc phục lỗi nhận diện giọng nói (ASR) và các từ nối thừa (à, ừm...).
   - Đảm bảo câu văn trôi chảy, có sự kết nối logic với phần [TRƯỚC ĐÓ] và dẫn dắt mượt mà sang phần [TIẾP THEO].
   - Giữ nguyên phong cách của giảng viên nhưng làm cho câu từ gãy gọn hơn.

3. **Định dạng đầu ra (MARKDOWN):**
   - Sử dụng tiêu đề `### Nội dung Slide` và `### Lời giảng của Giảng viên`.
   - **Bôi đậm (bold)** các thuật ngữ chuyên môn hoặc từ khóa quan trọng.
   - Sử dụng các ký hiệu Markdown (-, *, 1., 2.) để phân tách các ý.
   - **Chỉ trả về duy nhất nội dung đã tinh chỉnh**, không có lời dẫn giải thêm.
"""


def get_query_rewrite_prompt(query: str) -> str:
    """
    Prompt viết lại câu truy vấn để tối ưu tìm kiếm.
    """
    return f"""
Nhiệm vụ của bạn là viết lại câu truy vấn (query) của người dùng để tối ưu hóa việc tìm kiếm trong Vector Database chứa nội dung bài giảng (bao gồm Slide và Lời giảng).

### Hướng dẫn thực hiện:
1. **Phân tích ý định:** Xác định xem người dùng đang tìm kiếm thông tin trên Slide (dạng liệt kê, định nghĩa) hay trong Lời giảng (dạng giải thích, ví dụ).
2. **Mở rộng thuật ngữ:** Thêm các từ đồng nghĩa hoặc thuật ngữ chuyên môn liên quan.
   - Ví dụ: "đồ án" -> "bài tập lớn", "project", "nhiệm vụ cuối kỳ".
   - Ví dụ: "giới thiệu môn học" -> "mục tiêu học tập", "đề cương bài giảng", "chuẩn đầu ra".
3. **Cấu trúc lại:** Chuyển câu hỏi ngắn thành một đoạn mô tả súc tích chứa các từ khóa quan trọng mà cả Slide và Giảng viên có khả năng sẽ đề cập tới.
4. **Ngôn ngữ:** Nếu query là tiếng Việt, hãy cung cấp phiên bản mở rộng bằng tiếng Việt (có thể kèm thuật ngữ tiếng Anh chuyên ngành nếu cần).

### Yêu cầu đầu ra:
- Chỉ trả về nội dung câu query đã được viết lại.
- Không kèm theo lời giải thích "Tôi đã viết lại là...".
- Đảm bảo câu văn mang tính học thuật và sát với ngữ cảnh bài giảng.

### Đây là câu truy vấn ban đầu:
{query}
"""


def get_answer_prompt(query: str, context: str) -> str:
    """
    Prompt sinh câu trả lời dựa trên context từ retrieval.
    """
    return f"""
Bạn là trợ lý ảo hỗ trợ sinh viên UIT tìm kiếm và tóm tắt nội dung bài giảng.

Dựa trên các tài liệu bài giảng được truy xuất bên dưới, hãy trả lời câu hỏi của sinh viên.

### Quy tắc:
1. **Chỉ trả lời dựa trên nội dung được cung cấp.** Nếu không tìm thấy thông tin, hãy nói rõ.
2. **Không tự trích dẫn nguồn:** Tuyệt đối KHÔNG ĐƯỢC viết thêm các câu trích dẫn có dạng `(Nguồn: Video...)` hay `Phút thứ...` vào câu trả lời vì giao diện frontend đã tự động xử lý phần nguồn video tách biệt.
3. **Định dạng:** Sử dụng định dạng văn bản Markdown chuẩn (bôi đậm, in nghiêng, chia bullet points thật đẹp và sạch sẽ, không trả về raw text).
4. **Ngôn ngữ:** Trả lời trực tiếp, ngôn ngữ tự nhiên, trôi chảy bằng tiếng Việt.

### Tài liệu bài giảng:
{context}

### Câu hỏi sinh viên:
{query}

### Câu trả lời:
"""
