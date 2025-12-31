# chatbot_nutrition_fastapi.py
"""
API QA Multimodal (Gemini) con FastAPI + LangGraph
- Endpoint /qa: recibe pregunta + archivos (imagen/audio/PDF, etc.) vía multipart/form-data
- Orquestación de flujos con LangGraph para mejor manejo de estados y escalabilidad
- Responde SIEMPRE en texto Markdown, sin bloques de código ni JSON
"""

from __future__ import annotations
import os, io, time, mimetypes, re
from typing import List, Optional, Any
from pathlib import Path

# === .env ===
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parent
    load_dotenv(BASE_DIR / ".env", override=False)
except Exception:
    pass

# ==== FastAPI ====
from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware

# ==== LangGraph Orchestration ====
from orchestration_graph import invoke_orchestration
from orchestration_state import MediaFile, MediaType

# ==== Gemini SDK (nuevo con fallback al anterior) ====
USING_NEW_SDK = False
try:
    from google import genai
    from google.genai.types import Part
    USING_NEW_SDK = True
except Exception:
    import google.generativeai as genai
    from google.generativeai.types import Part

# ==== Config ====
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

if USING_NEW_SDK:
    if not GOOGLE_API_KEY:
        print("[AVISO] Falta GOOGLE_API_KEY")
    client = genai.Client(api_key=GOOGLE_API_KEY)
else:
    if not GOOGLE_API_KEY:
        print("[AVISO] Falta GOOGLE_API_KEY")
    genai.configure(api_key=GOOGLE_API_KEY)
    client = None

# ============================
# Sistema de Orquestación - Sistema Instrucciones movido a orchestration_graph.py
# ============================
# NOTA: Las instrucciones de sistema ahora se gestionan en el módulo de orquestación
# para mejor mantenibilidad y adaptabilidad según tipo de análisis detectado.

# ==== FastAPI app ====
app = FastAPI(
    title="QA Multimodal API (FastAPI + Gemini + LangGraph)",
    description="Sube archivos (imagen/PDF/audio, etc.) y haz preguntas sobre su contenido (NutriApp). "
                "Orquestación con LangGraph para mejor escalabilidad.",
    version="2.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Helpers: Conversión de archivos
# -------------------------------
MAX_BYTES_FOR_DIRECT_PART = 20 * 1024 * 1024  # 20 MB

def guess_mime(path_or_url: str, default="application/octet-stream") -> str:
    """Adivina MIME type de una ruta o nombre de archivo"""
    mt, _ = mimetypes.guess_type(path_or_url)
    return mt or default

async def uploadfile_to_media_file(up: UploadFile) -> MediaFile:
    """
    Convierte un UploadFile de FastAPI a MediaFile para el orquestador
    """
    mt = getattr(up, "content_type", None) or guess_mime(
        getattr(up, "filename", "upload.bin")
    )
    
    if hasattr(up, "file"):
        data = up.file.read()
    else:
        data = await up.read()
    
    return MediaFile(
        filename=getattr(up, "filename", "upload.bin"),
        mime_type=mt,
        data=data,
        size_bytes=len(data),
    )

# -------------------------------
# Endpoints utilitarios
# -------------------------------
@app.get("/env-check", tags=["health"])
def env_check():
    """
    Confirma carga de variables (.env)
    """
    return {
        "google_api_key_loaded": bool(os.environ.get("GOOGLE_API_KEY")),
        "model": os.environ.get("GEMINI_MODEL", DEFAULT_MODEL),
    }

@app.get("/health", tags=["health"])
def health():
    """
    Health check simple
    """
    return {"status": "ok"}

# -------------------------------
# QA endpoint (multimodal con LangGraph)
# -------------------------------
@app.post("/qa", tags=["qa"])
async def qa_multipart(
    question: str = Form(...),
    use_files_api: Optional[str] = Form("false"),
    files: List[UploadFile] = File(...),
):
    """
    QA multimodal con archivos (imagen/audio/PDF, etc.) orquestado con LangGraph.
    - `question`: pregunta del usuario (texto).
    - `files`: uno o más archivos (UploadFile).
    - `use_files_api`: 'true' para usar Files API (útil para PDFs grandes, si usas el SDK nuevo).
    
    Retorna:
    - `ok`: True si fue exitoso
    - `answer`: Respuesta en Markdown
    - `metadata`: Información sobre el procesamiento (tipos de análisis, logs, tiempo)
    """
    try:
        q = (question or "").strip()
        use_flag = str(use_files_api).lower() in ("1", "true", "yes", "y")

        if not q:
            raise HTTPException(status_code=400, detail="Falta 'question'")
        if not files:
            raise HTTPException(
                status_code=400,
                detail="Adjunta al menos un archivo en 'files'",
            )

        # Convertir UploadFiles a MediaFile
        media_files = [await uploadfile_to_media_file(f) for f in files]
        
        # Invocar orquestación LangGraph
        answer_md, metadata = invoke_orchestration(
            question=q,
            media_files=media_files,
            use_files_api=use_flag,
        )
        
        return {
            "ok": True,
            "answer": answer_md,
            "metadata": metadata,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        return {
            "ok": False,
            "detail": f"{type(e).__name__}: {e}",
        }

# -------------------------------
# Main (uvicorn)
# -------------------------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    print(f"[Swagger] http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)
