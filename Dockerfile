FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY . /app

# Expose port
ENV PORT=80
EXPOSE ${PORT}

# Default command to run uvicorn
# Run update script first (safe to run even if no UPSTREAM_REPO set), then start uvicorn
CMD ["/bin/sh", "-c", "python update.py || true; uvicorn web:app --host 0.0.0.0 --port ${PORT}"]

