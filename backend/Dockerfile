# ==============================================================================
# WindWise UK — FastAPI Backend Dockerfile
# ==============================================================================
FROM python:3.13-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Create non-root user and persistent data directory
RUN useradd -m -u 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

# Install Python dependencies using trusted responsive mirror
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

# Copy application source code
COPY app/ app/
COPY verify_live_january.py .

# Ensure appropriate permissions on the data directory for the non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose FastAPI application port
EXPOSE 8000

# Health check using Python's built-in urllib to avoid external curl dependency
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; port = os.getenv('PORT', '8000'); urllib.request.urlopen(f'http://localhost:{port}/api/health')" || exit 1

# Start Uvicorn ASGI server bound to 0.0.0.0, dynamically binding to $PORT or default 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
