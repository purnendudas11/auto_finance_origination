# Use uv package manager, ARM64 compatible architecture
FROM --platform=linux/arm64 ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Add your DB variables directly into the image environment
ENV DB_HOST="originationdb.cqn0ge686n65.us-east-1.rds.amazonaws.com"
ENV DB_NAME="postgres"
ENV DB_USER="postgres"
ENV DB_PASSWORD="local1234"
ENV DB_PORT=5432

# Install build tools for compiling dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt .

# Use uv pip to install dependencies 
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --no-cache -r requirements.txt

# Copy app source code and pyproject.toml
COPY src/ ./src/
COPY pyproject.toml .

# Expose port
EXPOSE 8080

# 1. Set the Python path to the root application directory
ENV PYTHONPATH=/app

# 2. Startup command - Runs the app as a package module instead of a raw file
CMD ["python", "-m", "src.auto_finance_origination.crew"]
