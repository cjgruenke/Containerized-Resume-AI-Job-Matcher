# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Metadata
LABEL maintainer="you@example.com" \
      org.opencontainers.image.source="your-repo-url"

# Avoid Python writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create app user and group (non-root)
RUN groupadd -r jobmatcher && useradd -r -g jobmatcher jobmatcher

# Set working directory
WORKDIR /app

# Copy only necessary files for pip install first to leverage caching
COPY requirements.txt /app/requirements.txt

# Install system deps (for PyPDF2 nothing special usually needed),
# but include build-essential in case some pip libs need it (keep small).
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      && pip install --no-cache-dir -r /app/requirements.txt \
      && apt-get purge -y --auto-remove build-essential \
      && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app

# Fix permissions
RUN chown -R jobmatcher:jobmatcher /app

# Switch to non-root user
USER jobmatcher

# Expose a working directory for outputs
VOLUME ["/app/output", "/app/data"]

# Default command:
# - By default, run with mock embedder to avoid accidental API calls.
# - Users can override CMD with docker run <image> python -m src.cli --resume /data/resume.pdf
CMD ["python", "-m", "JobMatcher.cli", "--use-mock-embedder"]
