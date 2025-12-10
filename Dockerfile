# Multi-stage Docker build for AgentParty MCP Platform

# Base stage with common dependencies
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Development stage
FROM base as development

# Install all dependencies including dev
RUN pip install --no-cache-dir -e ".[dev]"

# Copy source code
COPY . .

# Expose ports
EXPOSE 8000 3000

# Run with hot reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production build stage
FROM base as builder

# Install dependencies
RUN pip install --no-cache-dir --prefix=/install .

# Production stage
FROM python:3.11-slim as production

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy source code
COPY src ./src
COPY agents ./agents
COPY workflows ./workflows

# Create non-root user
RUN useradd -m -u 1000 agentparty && \
    chown -R agentparty:agentparty /app

USER agentparty

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
