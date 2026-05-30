# Modeling Agent Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agents/base/ ./agents/base/
COPY agents/modeling/ ./agents/modeling/
COPY config/ ./config/

# Expose port
EXPOSE 8000

# Run the agent
CMD ["python", "agents/modeling/main.py"]
