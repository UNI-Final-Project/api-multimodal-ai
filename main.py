"""
🍽️ NutriApp API - Punto de Entrada
API de nutrición con análisis de imágenes y chatbot de recomendaciones
"""
import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.nutrition_api import app
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 NutriApp API iniciando...")
    print(f"📚 Swagger docs: http://localhost:{port}/docs")
    print(f"🔧 ReDoc: http://localhost:{port}/redoc")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=os.environ.get("ENVIRONMENT") == "development",
    )
