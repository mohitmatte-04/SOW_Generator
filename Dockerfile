# Build stage with uv for fast dependency installation
FROM python:3.12-slim AS builder

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files and source code
COPY pyproject.toml uv.lock ./
COPY src ./src

# Install dependencies in a virtual environment
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.12-slim

# Install minimal runtime dependencies
# Note: PPTX to PDF conversion now uses Google Slides API (no LibreOffice needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create non-root user for security first
RUN useradd -m -u 1000 appuser

# Copy virtual environment from builder and set ownership
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code and set ownership
COPY --chown=appuser:appuser src ./src

# Create logs directory with proper permissions for appuser
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Copy service account file (if using file-based auth)
# NOTE: In production, prefer using Workload Identity or default service account
# COPY --chown=appuser:appuser service_account.json ./

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0
# Note: PORT is not set here to allow runtime override (e.g., Cloud Run sets this dynamically)
# Default port 8080 is handled in server.py via os.getenv("PORT", "8080")

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8080}/health')"

# Expose port (Cloud Run will override with PORT env var)
EXPOSE 8080

# Run the application
CMD ["python", "-m", "sow_generator.server"]
