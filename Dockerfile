# Use official Python 3.12 slim image
FROM python:3.12-slim
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /home/saku0/threat-intel-dashboard

# Install system dependencies (optional but recommended)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .
# Expose Flask port
EXPOSE 5000

# Default command to run your app
CMD ["python", "run.py"]
