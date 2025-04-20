# build imagen local:
# docker build -f containers/prediction/Dockerfile -t predicion_image .

# Imagen base de Python
FROM python:3.13

# Crear directorio de trabajo
WORKDIR /application

# Instalar dependencias del sistema
#RUN apt-get update 
#RUN apt-get install

# Copiar los archivos necesarios
COPY containers/prediction/requirements.txt .
COPY application/api/prediction_api.py .
COPY application/model/ application/model
# TODO quitar si se pasa a BBDD SQL
COPY output_data/ output_data

# Instalar dependencias
RUN pip3 install -r requirements.txt

# Exponer el puerto que Flask va a usar
EXPOSE 5000

# Comando por defecto para ejecutar la aplicación
CMD ["python", "prediction_api.py"]