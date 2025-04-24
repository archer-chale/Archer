FROM python:3.10-slim
WORKDIR /app

# Copy requirements first
COPY main/bots/SCALE_T/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Debug utilities - remove later
RUN apt-get update && apt-get install -y \
    vim-tiny \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire SCALE_T directory to preserve imports
COPY main/bots/SCALE_T /app/main/bots/SCALE_T
COPY data/SCALE_T/templates /app/data/templates
COPY main/utils /app/main/utils/
COPY main/__init__.py /app/main/__init__.py 
COPY configs/ /app/configs

# Set the entrypoint to run the engine
ENTRYPOINT ["python", "-m", "main.bots.SCALE_T.engine"]
# ENTRYPOINT [ "tail", "-f", "/dev/null" ]
# Default arguments if none provided
CMD ["SOXL", "paper"]
