# Multi-stage build for production-ready FastAPI backend
FROM python:3.11-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv and dependencies in single RUN command
RUN curl -LsSf https://astral.sh/uv/0.7.2/install.sh | sh && \
    export PATH="/root/.local/bin:$PATH" && \
    uv sync --frozen --no-dev

# Production stage
FROM python:3.11-slim AS production

# Create non-root user for security
RUN groupadd -r hitoq && useradd -r -g hitoq hitoq

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/
COPY alembic.ini ./
COPY alembic/ ./alembic/

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV ENVIRONMENT=production

# Change ownership to non-root user
RUN chown -R hitoq:hitoq /app
USER hitoq

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers"]