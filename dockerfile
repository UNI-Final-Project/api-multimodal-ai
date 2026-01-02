FROM python:3.12-slim

# Evitar .pyc y usar stdout sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copiamos requisitos e instalamos (cacheable)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos aplicación
COPY main.py ./
COPY src/ ./src/

# Exponer puerto por defecto (Cloud Run usa $PORT)
EXPOSE 8080

# Usar shell para permitir expansión de ${PORT}
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
