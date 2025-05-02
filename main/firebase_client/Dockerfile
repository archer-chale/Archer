FROM python:3.10-slim
WORKDIR /app

# Copy requirements first
COPY main/firebase_client/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Debug utilities - optional, remove if not needed
RUN apt-get update && apt-get install -y \
    vim-tiny \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copy Firebase client service files
COPY main/firebase_client /app/main/firebase_client
COPY main/utils /app/main/utils/
COPY main/__init__.py /app/main/__init__.py
COPY configs/ /app/configs

# Set the entrypoint to run the main module
CMD ["python", "-m", "main.firebase_client.src.main"]
