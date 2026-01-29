FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY packages/core /app/packages/core
COPY apps/worker/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY apps/api /app/apps/api
COPY apps/worker /app

ENV PYTHONPATH="${PYTHONPATH}:/app/apps/api"

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "worker.py"]