# build imagen local:
# docker build -f containers/database/Dockerfile -t database_image .

# Imagen base de Python
FROM python:3.13-alpine

# Crear directorio de trabajo
WORKDIR /application

# Instalar dependencias del sistema
RUN apt-get update 
RUN apt-get install

# Copiar los archivos necesarios
COPY containers/database/requirements.txt .
COPY application/api/database_api.py .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que Flask va a usar
EXPOSE 5000

# Comando por defecto para ejecutar la aplicación
CMD ["python", "database_api.py"]