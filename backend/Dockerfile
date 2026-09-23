FROM python:3.11-slim

WORKDIR /app

# Install system utilities (libmagic for file type detection, curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    file \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose FastAPI port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
