FROM postgres:13

USER root

RUN mkdir /app && chmod 777 /app

# Instalar Python, pip y venv
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip3 install --break-system-packages pandas sqlalchemy psycopg2-binary

USER postgres