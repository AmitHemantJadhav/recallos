FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy credentials
COPY speech-key.json /app/speech-key.json

# Copy all application code
COPY . .

# Set environment
ENV PYTHONPATH=/app
ENV PORT=8080
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/speech-key.json

# Expose port
EXPOSE 8080

# Run server
CMD ["python", "agents/orchestrator/server.py"]