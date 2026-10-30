FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY TgBot/ ./TgBot/

WORKDIR /app/TgBot

CMD ["python", "main.py"]
