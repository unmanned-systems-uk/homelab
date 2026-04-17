# SCPI Instruments MCP Server
# Provides MCP tool access to SCPI-enabled test equipment

FROM python:3.11-slim

LABEL maintainer="HomeLab"
LABEL description="SCPI Instruments MCP Server for test equipment control"

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scpi_transport.py .
COPY connection_pool.py .
COPY scpi_mcp.py .
COPY instruments/ ./instruments/

# Environment configuration - Instrument IPs
ENV RSA5065N_IP=10.0.1.85
ENV MSO8204_IP=10.0.1.106
ENV DMM6500_IP=10.0.1.101
ENV DL3021A_IP=10.0.1.105
ENV DG2052_IP=10.0.1.120
ENV DP932A_1_IP=10.0.1.111
ENV DP932A_2_IP=10.0.1.138
# Ports
ENV SCPI_PORT=5555
ENV DMM_PORT=5025
ENV PSU_PORT=5025
ENV MCP_PORT=8081
ENV PYTHONUNBUFFERED=1

# Expose MCP SSE port
EXPOSE 8081

# Health check - verify server is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('localhost', 8081)); s.close()" || exit 1

# Run MCP server
CMD ["python", "scpi_mcp.py"]
