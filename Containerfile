# syntax=docker/dockerfile:1

# --- Stage 1: Frontend build ---
FROM node:20-slim AS frontend_builder
WORKDIR /app

# Only copy what we need for npm ci
COPY package.json package-lock.json ./
COPY src/frontend ./src/frontend

RUN npm ci && npm run build


# --- Stage 2: Python runtime ---
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/home/app/.local/bin:${PATH}"

WORKDIR /app

# System deps (kept minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better cache
COPY requirements.txt ./
RUN pip install --user -r requirements.txt

# Copy backend and templates
COPY src/backend ./src/backend
COPY templates ./templates

# Copy built frontend assets from builder
COPY --from=frontend_builder /app/src/backend/static/react ./src/backend/static/react

# Create non-root user (rootless-friendly)
RUN groupadd --system app && useradd --system --home /home/app --gid app app \
    && mkdir -p /home/app && chown -R app:app /home/app /app

USER app

EXPOSE 8000

# Healthcheck (optional): simple TCP connect to port 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ["python","-c","import socket; socket.create_connection(('127.0.0.1',8000),3)"]

# Default envs (override in runtime)
ENV SECURE_COOKIE=true

# Start server
CMD ["python", "-m", "uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
