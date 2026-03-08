FROM python:3.11-slim

WORKDIR /app

COPY apps/orchestrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/orchestrator/app /app/app
COPY services /app/services
COPY config /app/config

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]