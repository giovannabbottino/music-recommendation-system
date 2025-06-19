FROM python:3.11-slim

# Install Java (required for owlready2's Pellet reasoner)
RUN apt-get update && apt-get install -y \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/app/src"

CMD ["bash", "-c", "pytest tests && python src/app.py"]
