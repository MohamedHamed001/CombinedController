FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
PORT=${PORT:-5000}\n\
PORT2=$((PORT + 1))\n\
gunicorn diabetes_companion.app:app --bind 0.0.0.0:$PORT &\n\
gunicorn PID-NN-main.app:app --bind 0.0.0.0:$PORT2\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE $PORT $((PORT + 1))

# Start both applications
CMD ["/app/start.sh"] 