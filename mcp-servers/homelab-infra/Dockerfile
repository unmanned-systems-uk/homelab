FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install dependencies (including PostgreSQL client libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY homelab_server.py .

# Copy encryption module for credential decryption
COPY infrastructure/ /app/infrastructure/

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# PostgreSQL connection settings (can be overridden)
ENV HOMELAB_DB_HOST=10.0.1.251
ENV HOMELAB_DB_PORT=5433
ENV HOMELAB_DB_NAME=homelab_db
ENV HOMELAB_DB_USER=ccpm
# Password should be set via Docker secrets or environment

CMD ["python", "homelab_server.py"]
