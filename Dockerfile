# Imagen base de Python
FROM python:3.12-slim

# Evita .pyc y usa stdout sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiamos solo requisitos primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY requirements.txt MultimediaLLM.py ./

# Puerto interno de la app
EXPOSE 8080

# Comando de arranque:
#   MultimediaLLM = nombre del archivo  (MultimediaLLM.py)
#   app           = objeto FastAPI definido en ese archivo
CMD ["uvicorn", "MultimediaLLM:app", "--host", "0.0.0.0", "--port", "8080"]
