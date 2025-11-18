# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (useful for psycopg2, Pillow, etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set default port (many platforms override this with $PORT)
ENV PORT=8080

# Collect static files (make sure STATIC_ROOT is set in settings.py)
RUN python manage.py collectstatic --noinput || echo "collectstatic failed (maybe not configured) – skipping"

# Expose the port Gunicorn will run on
EXPOSE 8080

# Start Gunicorn
# If platform provides $PORT, it will use that, otherwise default to 8080
CMD gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8080}
