FROM python:3.11-slim

WORKDIR /app

COPY apps/worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/worker/app /app/app
COPY services /app/services

CMD ["python", "-u", "app/main.py"]