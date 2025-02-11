# Use an official Python image as the base
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies (including PostgreSQL client)
RUN apt-get update && apt-get install -y libpq-dev gcc postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure logs directory exists with correct permissions
RUN mkdir -p /app/logs && chmod -R 777 /app/logs

# Copy the entire project into the container
COPY . .

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Default command (API container)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
