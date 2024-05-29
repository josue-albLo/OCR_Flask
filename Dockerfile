# Usar una imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar las dependencias del sistema necesarias para Tesseract y OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar los archivos de requisitos primero para aprovechar la caché de Docker
COPY requirements.txt /app/requirements.txt

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos necesarios a la imagen
COPY . /app

# Exponer el puerto en el que corre la aplicación Flask
EXPOSE 5000

# Definir variables de entorno
ENV FLASK_ENV=development
ENV GUNICORN_CMD_ARGS="--workers=2 --threads=4 --bind=0.0.0.0:5000 --timeout 120 --log-level=debug --capture-output"

# Definir el comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "app:app"]
