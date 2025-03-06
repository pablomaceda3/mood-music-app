# Use Alpine-based Python image
FROM python:3.9-alpine

# Set working directory
WORKDIR /app

# Install system dependencies needed for PostgreSQL and Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# The actual command will be provided by docker-compose
# This is just a fallback if you run the container directly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]