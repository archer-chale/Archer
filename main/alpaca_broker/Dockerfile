FROM python:3.10-slim
WORKDIR /app

# Copy requirements first
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire main directory
COPY main/alpaca_broker ./aplaca_broker

# Set the entrypoint to run the broker service
ENTRYPOINT ["tail", "-f", "/dev/null"]
