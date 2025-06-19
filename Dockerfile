FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/app/src"

WORKDIR /app/src
CMD ["python", "app.py"]
