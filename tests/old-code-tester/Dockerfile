FROM python:3.10-slim
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service account key first (this should be in .dockerignore for security)
COPY configs/adminsdk.json ./

# Copy the rest of the source code
COPY . .

# Set the entrypoint to run the service with a ticker argument
ENTRYPOINT ["python", "service.py"]
# Default ticker if none provided
CMD ["AAPL"]
