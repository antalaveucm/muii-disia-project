# containers/prediction/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY containers/prediction/requirements.txt .

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Copiar toda la estructura de la aplicación
COPY application/ ./application/

EXPOSE 5000

# Añadir el directorio al PYTHONPATH
ENV PYTHONPATH=/app

CMD ["python", "./application/api/prediction_api.py"]