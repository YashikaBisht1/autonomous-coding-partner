FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including curl for health checks)
# System dependencies removed to avoid network hang
# RUN apt-get update && apt-get install -y \
#     gcc \
#     git \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create workspace directory and ensure it is writable by the app user
RUN mkdir -p /app/workspace

# Create a non-root user and take ownership of the app directory
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV WORKSPACE_PATH=/app/workspace

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]