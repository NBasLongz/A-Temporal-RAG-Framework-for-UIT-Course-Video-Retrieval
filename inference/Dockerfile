# Use the official PyTorch image that already bundles CUDA + cuDNN
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

WORKDIR /app

# Install only the packages needed for this service
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    transformers \
    huggingface-hub \
    pydantic

ENV HF_HOME=/models

COPY inference/main.py ./main.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
