# Production Dockerfile for React + Flask application

# Stage 1: Build React frontend
FROM node:18-bullseye-slim AS frontend-build

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
COPY backend/ backend/
COPY migrations/ migrations/
COPY helpers/ helpers/

# Copy Node.js runtime from the frontend build stage
COPY --from=frontend-build /usr/local/bin/node /usr/local/bin/node
COPY --from=frontend-build /usr/local/bin/npm /usr/local/bin/npm
COPY --from=frontend-build /usr/local/bin/npx /usr/local/bin/npx
COPY --from=frontend-build /usr/local/lib/node_modules /usr/local/lib/node_modules

# Copy built Next.js app (standalone output expects server.js at project root)
COPY --from=frontend-build /frontend/.next/standalone ./frontend
COPY --from=frontend-build /frontend/.next/static ./frontend/.next/static

# Create startup script
COPY scripts/start-prod.sh ./start-prod.sh
RUN chmod +x start-prod.sh

ENV FLASK_APP=backend.app:create_app

EXPOSE 8000

CMD ["./start-prod.sh"]
