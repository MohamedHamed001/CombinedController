FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    pkg-config \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for memory optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:64 \
    PYTHONPATH=/app \
    TF_FORCE_GPU_ALLOW_GROWTH=true \
    TF_MEMORY_ALLOCATION=0.5 \
    TRANSFORMERS_CACHE=/tmp/transformers \
    TORCH_HOME=/tmp/torch \
    HF_HOME=/tmp/huggingface

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies in stages with memory optimization
RUN pip install --no-cache-dir flask==3.1.1 flask-cors>=3.0.0 gunicorn==21.2.0 python-dotenv==1.1.0 requests==2.31.0 && \
    pip install --no-cache-dir numpy==1.26.4 pandas==2.2.0 scikit-learn==1.6.1 && \
    pip install --no-cache-dir torch==2.1.0+cpu --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir tensorflow-cpu==2.15.0 && \
    pip install --no-cache-dir langchain==0.3.25 langchain-huggingface==0.2.0 langchain-community==0.3.24 langchain-groq==0.3.2 && \
    pip install --no-cache-dir transformers==4.43.0 sentence-transformers==2.6.1 faiss-cpu==1.11.0 && \
    pip install --no-cache-dir langdetect==1.0.9 deep-translator==1.11.4 && \
    pip install --no-cache-dir matplotlib==3.10.0 control==0.10.1 xmltodict==0.14.2

# Copy the rest of the application
COPY . .

# Create a startup script with strict memory limits
RUN echo '#!/bin/bash\n\
# Start the backend services with strict memory limits\n\
cd /app && gunicorn diabetes_companion.app:app --bind 0.0.0.0:5000 --workers 1 --threads 1 --worker-class gthread --worker-tmp-dir /dev/shm --max-requests 1000 --max-requests-jitter 50 --timeout 30 &\n\
cd /app && gunicorn PID-NN-main.app:app --bind 0.0.0.0:5001 --workers 1 --threads 1 --worker-class gthread --worker-tmp-dir /dev/shm --max-requests 1000 --max-requests-jitter 50 --timeout 30 &\n\
# Start the main router\n\
cd /app && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 1 --worker-class gthread --worker-tmp-dir /dev/shm --max-requests 1000 --max-requests-jitter 50 --timeout 30\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the main port
EXPOSE $PORT

# Start the application
CMD ["/app/start.sh"] 