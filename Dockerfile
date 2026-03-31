FROM python:3.10-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các dependencies hệ thống cơ bản cần thiết cho AI/CV (nếu có dùng OpenCV/Tesseract)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container (ngoại trừ các file trong .dockerignore)
COPY . .

# Expose port 8000
EXPOSE 8000

# Chỉ định lệnh chạy FastAPI server
CMD ["python", "-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
