FROM python:3.9-slim

# Instalar las dependencias de PostgreSQL necesarias para compilar psycopg2
RUN apt-get update && \
    apt-get install -y gcc libpq-dev

WORKDIR /app

# Copiar el archivo requirements.txt
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install -r requirements.txt

COPY monitoring.py .

# Exponer el puerto 8000
EXPOSE 8000

# Comando para ejecutar la aplicación (ajústalo según tu caso)
CMD ["python", "monitoring.py"]
