# Stage 1: Build React Frontend (Upgraded to Node 20 for styleText utility support)
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend_pricing/package*.json ./
RUN npm install
COPY frontend_pricing/ ./
RUN npm run build

# Stage 2: Build Python Django Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY . .

# Copy compiled React static assets from Stage 1
COPY --from=frontend-builder /app/static/pricing_app/dist/ /app/static/pricing_app/dist/

# Run Django static file collection
ENV SECRET_KEY=prod-collectstatic-key
RUN python manage.py collectstatic --noinput

# Expose port and run Gunicorn
EXPOSE 8080
CMD exec gunicorn localservices.wsgi:application --bind 0.0.0.0:8080 --workers 1 --threads 8 --timeout 0
