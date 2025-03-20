# Use Alpine-based Python image
FROM python:3.9-alpine

# Set working directory
WORKDIR /app

# Install system dependencies with better SSL support for Alpine
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    ca-certificates \
    openssl \
    curl \
    && update-ca-certificates \
    && pip install --upgrade pip certifi

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

RUN chmod 777 /app/.spotify_cache

# The actual command will be provided by docker-compose
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]