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

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies in stages
RUN pip install --no-cache-dir flask==3.1.1 flask-cors>=3.0.0 gunicorn==21.2.0 python-dotenv==1.1.0 requests==2.31.0 && \
    pip install --no-cache-dir torch==2.1.0+cpu --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
# Start the backend services\n\
gunicorn diabetes_companion.app:app --bind 0.0.0.0:5000 &\n\
gunicorn PID-NN-main.app:app --bind 0.0.0.0:5001 &\n\
# Start the main router\n\
gunicorn app:app --bind 0.0.0.0:$PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the main port
EXPOSE $PORT

# Start the application
CMD ["/app/start.sh"] 