FROM python:3.12-slim

# Set environment variables
ENV QP_OFFLINE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash quietpatch

# Install QuietPatch
RUN pip install --no-cache-dir quietpatch==0.3.0

# Create data directory
RUN mkdir -p /home/quietpatch/.quietpatch && \
    chown -R quietpatch:quietpatch /home/quietpatch/.quietpatch

# Switch to non-root user
USER quietpatch
WORKDIR /home/quietpatch

# Set data directory
ENV QP_DATA_DIR=/home/quietpatch/.quietpatch

# Default command
ENTRYPOINT ["quietpatch"]
CMD ["--help"]
