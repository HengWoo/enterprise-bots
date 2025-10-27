# Campfire AI Bot - Production Docker Image
# Multi-stage build with Claude Agent SDK + Multi-MCP Support
# Author: Wu Heng | Date: 2025-10-14
# v0.2.1: FastAPI + Stateful sessions + Real-time progress milestones (Beta)

# Stage 1: Builder - Build Campfire AI Bot
FROM python:3.11-slim AS builder

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Copy source code for dependency resolution
COPY src/ ./src/
COPY bots/ ./bots/

# Install dependencies using uv (creates .venv)
RUN uv sync --frozen

# Stage 2: Runtime
FROM python:3.11-slim

LABEL maintainer="heng.woo@gmail.com"
LABEL description="Campfire AI Bot with Multi-Bot Collaboration + Document Processing (PDF/DOCX/PPTX/Images) (FastAPI)"
LABEL version="0.4.0.1"

# Install uv in runtime (CRITICAL: needed for Financial MCP subprocess)
RUN pip install --no-cache-dir uv

# Install Node.js 20.x (Required for full Claude CLI with MCP support)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && NODE_MAJOR=20 \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install sqlite3, pandoc, libreoffice, and poppler for document processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    pandoc \
    libreoffice \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI via npm (Full version with MCP support)
# This is needed by claude-agent-sdk for SubprocessCLITransport
# Standalone binary (curl install.sh) does NOT support custom MCP servers
RUN npm install -g @anthropic-ai/claude-code

# Create app user (security: non-root)
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser bots/ ./bots/
COPY --chown=appuser:appuser scripts/ ./scripts/
COPY --chown=appuser:appuser .claude/ ./.claude/

# Copy Financial MCP and install dependencies
COPY financial-mcp/ /app/financial-mcp/
WORKDIR /app/financial-mcp
# Remove broken .venv if it exists
RUN rm -rf .venv
# Install Financial MCP dependencies using system Python 3.11
ENV UV_PYTHON=/usr/local/bin/python3
RUN uv sync
# Go back to app directory
WORKDIR /app

# Change ownership of Financial MCP to appuser
RUN chown -R appuser:appuser /app/financial-mcp

# Create directories for AI knowledge and session cache
RUN mkdir -p /app/ai-knowledge/user_contexts \
             /app/ai-knowledge/processed_files \
             /app/session_cache && \
    chown -R appuser:appuser /app/ai-knowledge /app/session_cache

# Switch to app user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Environment variables
ENV FASTAPI_PORT=8000 \
    FASTAPI_HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI app via uvicorn
CMD ["uvicorn", "src.app_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
