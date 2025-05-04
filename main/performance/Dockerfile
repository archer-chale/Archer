FROM python:3.10-slim
WORKDIR /app

# install dependencies
RUN pip install --no-cache-dir redis

COPY main/__init__.py ./main/__init__.py
COPY main/utils/redis ./main/utils/redis
COPY main/performance ./main/performance

# hold the container open
CMD ["tail", "-f", "/dev/null"]
# ENTRYPOINT [ "python", "-m", "main.performance.main" ]
