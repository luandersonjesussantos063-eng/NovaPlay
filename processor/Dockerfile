FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY process.py process_worker.py ./
RUN useradd --create-home --uid 10001 nplay
USER nplay
ENTRYPOINT ["python", "process_worker.py"]
