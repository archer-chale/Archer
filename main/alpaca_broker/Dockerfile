FROM python:3.10-slim

# Run from project root to make relative imports work
WORKDIR /app

# Copy requirements first
COPY main/alpaca_broker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy environment configuration
COPY configs/.env ./configs/

# Copy necessary modules
COPY main/bots/SCALE_T/common ./main/bots/SCALE_T/common
COPY main/utils/redis ./main/utils/redis
COPY main/alpaca_broker ./main/alpaca_broker

# hold the container open
# CMD ["tail", "-f", "/dev/null"]
CMD ["python", "-m", "main.alpaca_broker.main"]
