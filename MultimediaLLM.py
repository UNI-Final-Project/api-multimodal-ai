# chatbot_nutrition_fastapi.py
"""
API QA Multimodal (Gemini) con FastAPI
- Endpoint /qa: recibe pregunta + archivos (imagen/audio/PDF, etc.) vía multipart/form-data
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
# Instrucciones de sistema (QA) — enfocadas en NutriApp
# ============================
SYSTEM_INSTRUCTIONS_QA = (
    "Eres el asistente multimodal de **NutriApp**, especializado en alimentación, nutrición práctica "
    "y análisis de contenido relacionado con comidas.\n\n"
    "Tipos de archivos que puedes recibir:\n"
    "- Fotos de platos de comida, loncheras, snacks o bebidas.\n"
    "- Capturas de pantalla o PDFs de menús, planes de alimentación o recetas.\n"
    "- Etiquetas nutricionales de productos envasados.\n"
    "- Reportes simples relacionados con peso, medidas corporales o diarios de comidas.\n\n"
    "Tu objetivo principal es ayudar a la persona a **entender mejor lo que está comiendo** y a darle "
    "ideas concretas para mejorar sus decisiones de alimentación, siempre de forma clara y realista.\n\n"
    "Instrucciones de respuesta:\n"
    "1) Responde SIEMPRE en **español**.\n"
    "2) Devuelve SOLO **texto en Markdown**, sin bloques de código (sin ```), y sin JSON.\n"
    "3) Usa esta estructura recomendada:\n"
    "   - **Respuesta directa**: 2–4 líneas que contesten la pregunta de forma clara (por ejemplo, si el plato "
    "es equilibrado, si es muy alto en azúcar, si es una buena opción para después de entrenar, etc.).\n"
    "   - **Análisis / Explicación nutricional**: describe los componentes principales del plato o del producto "
    "(fuentes de proteína, carbohidratos, grasas, fibra), comenta sobre porciones aproximadas y calidad nutricional. "
    "Si hay etiqueta, interpreta los valores más relevantes (kcal, azúcar, grasas, proteína, sodio).\n"
    "   - **Recomendaciones o siguientes pasos**: sugiere mejoras prácticas (porciones, combinaciones más equilibradas, "
    "ideas para hacer el plato más saludable, ejemplos de intercambios: \"en lugar de X podrías usar Y\").\n\n"
    "4) Cuando el usuario pida **ideas de recetas** o inspiración a partir de lo que ves en los archivos, propone "
    "de 3 a 5 ideas de receta sencillas. Para cada receta, indica:\n"
    "   - Nombre en **negrita**.\n"
    "   - Breve descripción práctica.\n"
    "   - Una estimación aproximada del tipo de aporte (alto en proteína, ligero, rico en fibra, etc.), sin dar "
    "números clínicamente precisos.\n\n"
    "5) Sé prudente: **no des diagnósticos médicos ni tratamientos**. Si detectas temas sensibles (diabetes, embarazo, "
    "enfermedades crónicas, trastornos de la conducta alimentaria, etc.), aclara que tu orientación es general y sugiere "
    "consultar con un profesional de la salud.\n\n"
    "6) Si la pregunta del usuario o los archivos NO están claramente relacionados con nutrición, alimentación, "
    "recetas, hábitos alimenticios o análisis de comidas, entonces:\n"
    "   - **NO respondas a la pregunta en sí**, aunque sea sencilla (por ejemplo, operaciones matemáticas como 1 + 1 o "
    "preguntas generales que no tengan que ver con comida).\n"
    "   - Limítate a explicar brevemente que tu función está restringida a temas de alimentación, nutrición y recetas.\n"
    "   - Invita al usuario a reformular su duda enfocándola en comida, hábitos alimenticios o análisis de lo que está comiendo.\n"
)

# ==== FastAPI app ====
app = FastAPI(
    title="QA Multimodal API (FastAPI + Gemini)",
    description="Sube archivos (imagen/PDF/audio, etc.) y haz preguntas sobre su contenido (NutriApp).",
    version="1.0.0",
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
# Helpers Markdown / LLM
# -------------------------------
def force_markdown(text: str) -> str:
    """
    Limpia fences de código ``` y evita respuestas en puro JSON.
    No intenta transformar el contenido, solo hacerlo más legible para el frontend.
    """
    if not text:
        return ""
    t = text.strip()
    # Elimina ```<lang> opcional al inicio
    t = re.sub(r"^```(?:\w+)?\s*", "", t)
    # Elimina ``` final
    t = re.sub(r"\s*```$", "", t)
    # Evitar respuestas en JSON plano
    if t.strip().startswith("{") or t.strip().startswith("["):
        return "- " + t.replace("\n", "\n- ")
    return t

def gemini_generate(contents: List[Any], temperature: float = 0.2) -> str:
    if USING_NEW_SDK:
        try:
            r = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=contents,
                config={"temperature": temperature},
            )
        except TypeError:
            r = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=contents,
                generation_config={"temperature": temperature},
            )
        return (getattr(r, "text", "") or "").strip()
    else:
        gm = genai.GenerativeModel(DEFAULT_MODEL)
        r = gm.generate_content(contents, generation_config={"temperature": temperature})
        return (getattr(r, "text", "") or "").strip()

# -------------------------------
# Helpers multimedia (Gemini Parts)
# -------------------------------
MAX_BYTES_FOR_DIRECT_PART = 20 * 1024 * 1024  # 20 MB

def guess_mime(path_or_url: str, default="application/octet-stream") -> str:
    mt, _ = mimetypes.guess_type(path_or_url)
    return mt or default

def part_from_bytes(data: bytes, mime_type: str) -> Part:
    return Part.from_bytes(data=data, mime_type=mime_type)

def part_from_uploadfile(up: UploadFile, use_files_api: bool = False):
    """
    Convierte un UploadFile de FastAPI en un Part de Gemini.
    Si use_files_api=True y el archivo es grande, usa files.upload (solo SDK nuevo).
    """
    mt = getattr(up, "content_type", None) or guess_mime(
        getattr(up, "filename", "upload.bin")
    )

    if hasattr(up, "file"):
        data = up.file.read()
    else:
        data = up.read()

    if use_files_api and USING_NEW_SDK and len(data) > MAX_BYTES_FOR_DIRECT_PART:
        # Subida vía Files API (para PDFs / imágenes grandes)
        if hasattr(up, "file"):
            up.file.seek(0)
            uploaded = client.files.upload(
                file=up.file,
                name=getattr(up, "filename", f"upload_{int(time.time())}"),
                mime_type=mt,
            )
        else:
            uploaded = client.files.upload(
                file=io.BytesIO(data),
                name=getattr(up, "filename", f"upload_{int(time.time())}"),
                mime_type=mt,
            )
        return uploaded
    else:
        # Directo en el prompt (más simple y suficiente para archivos pequeños/medianos)
        return part_from_bytes(data, mt)

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
# QA endpoint (multimodal, multipart)
# -------------------------------
@app.post("/qa", tags=["qa"])
async def qa_multipart(
    question: str = Form(...),
    use_files_api: Optional[str] = Form("false"),
    files: List[UploadFile] = File(...),
):
    """
    QA multimodal con archivos (imagen/audio/PDF, etc.) — responde en Markdown.
    - `question`: pregunta del usuario (texto).
    - `files`: uno o más archivos (UploadFile).
    - `use_files_api`: 'true' para usar Files API (útil para PDFs grandes, si usas el SDK nuevo).
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

        media_parts = [part_from_uploadfile(f, use_files_api=use_flag) for f in files]

        contents = [
            SYSTEM_INSTRUCTIONS_QA,
            *media_parts,
            f"Pregunta del usuario: {q}",
        ]
        answer = gemini_generate(contents)
        answer_md = force_markdown(answer)  # limpio para UI
        return {"ok": True, "answer": answer_md}
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
