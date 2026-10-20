# Multi-stage Dockerfile for Phishing Email ML Classification App
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8050

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download required NLTK corpora ahead of time
RUN python -c "import nltk; nltk.download('wordnet'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('omw-1.4')"

# Copy application source code and assets
COPY . .

# Generate initial ML bundle if not already bundled
RUN python -c "from predictor import predictor; print('Initialized models:', len(predictor.models))"

# Expose server port
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8050/api/status || exit 1

# Start FastAPI server
CMD ["python", "server.py"]
