FROM python:3.10-slim
WORKDIR /app

# Copy requirements first
COPY main/alpaca_broker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy environment configuration - Removed ENV_FILE directive
COPY configs/.env ./configs/

# Copy the bot module
COPY main/bots/SCALE_T/common ./main/bots/SCALE_T/common
COPY main/alpaca_broker ./main/alpaca_broker

# Run from project root to make relative imports work
WORKDIR /app
# hold the container open
# CMD ["tail", "-f", "/dev/null"]
CMD ["python", "-m", "main.alpaca_broker.main"]
