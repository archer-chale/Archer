FROM python:3.10-slim
WORKDIR /app

# Copy requirements first
COPY main/bots/SCALE_T/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire SCALE_T directory to preserve imports
COPY main/bots/SCALE_T /app/SCALE_T
COPY data/SCALE_T/templates /app/data/templates
COPY configs/ /app/configs

# Set the entrypoint to run the engine
ENTRYPOINT ["python", "-m", "SCALE_T.engine"]
# Default arguments if none provided
CMD ["SOXL", "paper"]
