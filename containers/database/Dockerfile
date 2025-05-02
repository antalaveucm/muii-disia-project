# containers/database/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY containers/database/requirements.txt .

# Instalar dependencias del sistema (¡AÑADE gcc y python3-dev!)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY application/api/database_api.py .

EXPOSE 5000
CMD ["python", "database_api.py"]