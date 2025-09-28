# Production Dockerfile for React + Flask application

# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-build

WORKDIR /frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm install --only=production

# Copy frontend source and build for production
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend with built frontend
FROM python:3.9-slim AS production

WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY app.py .
COPY models.py .
COPY migrate_db.py .

# Install Node.js for serving the frontend
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Copy built React app from frontend stage
COPY --from=frontend-build /frontend/.next ./frontend/.next
COPY --from=frontend-build /frontend/package.json ./frontend/package.json
COPY --from=frontend-build /frontend/next.config.js ./frontend/next.config.js
COPY --from=frontend-build /frontend/node_modules ./frontend/node_modules

# Create startup script
COPY start-prod.sh .
RUN chmod +x start-prod.sh

EXPOSE 8000

CMD ["./start-prod.sh"]