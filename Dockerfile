# Multi-stage build for Next.js frontend + Python backend
FROM node:18-alpine AS frontend-builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Python backend stage
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python backend
COPY python-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY python-backend/app ./app

# Copy built frontend
COPY --from=frontend-builder /app/.next ./.next
COPY --from=frontend-builder /app/public ./public
COPY --from=frontend-builder /app/package*.json ./

# Install only production dependencies for runtime
RUN npm ci --only=production

EXPOSE 8080

# Start both services
CMD ["sh", "-c", "npm start & uvicorn app.main:app --host 0.0.0.0 --port 8080"]
