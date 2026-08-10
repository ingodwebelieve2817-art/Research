# Single-stage build using Python Django Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies & Node.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install npm requirements
COPY package*.json ./
RUN npm ci --ignore-scripts

# Copy project files including precompiled frontend assets
COPY . .

# Copy bootstrap icons assets locally
RUN node scripts/setup_assets.js

# Download self-hosted fonts
RUN python scripts/download_fonts.py

# Build production Tailwind CSS file
RUN npm run build:css

# Run Django static file collection
ENV SECRET_KEY=prod-collectstatic-key
RUN python manage.py collectstatic --noinput

# Expose port and run Gunicorn
EXPOSE 8080
CMD exec gunicorn localservices.wsgi:application --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0
