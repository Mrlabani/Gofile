# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Expose port for Koyeb health check
EXPOSE 8000

# Run both bot and web app
CMD ["sh", "-c", "uvicorn web:app --host 0.0.0.0 --port 8000 & python main.py"]
