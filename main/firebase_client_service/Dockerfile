 # Docker build configuration for Firebase Client Service
FROM python:3.9-alpine

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps gcc musl-dev

# Copy requirements file
COPY main/firebase_client_service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

# Copy source code
COPY main/firebase_client_service/src ./src
COPY configs/adminsdk.json ./configs/adminsdk.json

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FIREBASE_CREDENTIALS=/app/configs/adminsdk.json
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV LOG_LEVEL=INFO

# Create non-root user for security
RUN adduser -D appuser
USER appuser

# Run the application
CMD ["python", "-m", "src.main"]