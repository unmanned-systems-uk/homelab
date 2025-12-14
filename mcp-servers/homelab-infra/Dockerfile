FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY homelab_server.py .

# Copy encryption module for credential decryption
COPY infrastructure/ /app/infrastructure/

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

# Database will be mounted at /data/homelab.db
RUN mkdir -p /data && chown mcpuser:mcpuser /data

USER mcpuser

# Environment variables (can be overridden)
ENV HOMELAB_DB_PATH=/data/homelab.db

CMD ["python", "homelab_server.py"]
