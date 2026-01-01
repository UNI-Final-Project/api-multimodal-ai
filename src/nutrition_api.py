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
    BASE_DIR = Path(__file__).resolve().parent.parent  # Sube a raíz
    load_dotenv(BASE_DIR / "config" / ".env", override=False)
    # Fallback: intenta raíz también
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
from pydantic import BaseModel
from typing import Dict

# ==== LangGraph Orchestration ====
from orchestration.graph import invoke_orchestration
from orchestration.state import MediaFile, MediaType

# ==== Supabase ====
from supabase_client import (
    get_user_profile,
    get_user_metrics,
    get_daily_nutrition,
    get_today_nutrition,
    get_conversation_history,
    save_conversation_message,
    clear_conversation_history,
    UserMetrics,
    DailyNutrition,
    UserNutritionProfile,
)

# ==== Nutrition Chatbot ====
from nutrition_chatbot import NutritionChatbot

# ==== LangChain para JSON ====
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel as PydanticModel, Field

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

# ============================
# Modelo para JsonOutputParser de LangChain
# ============================
class MealAnalysisModel(PydanticModel):
    """Modelo estructurado para análisis de comida - SOLO VALORES NUTRICIONALES"""
    calories: float = Field(description="Calorías totales en kcal")
    protein_g: float = Field(description="Proteína en gramos")
    carbs_g: float = Field(description="Carbohidratos en gramos")
    fat_g: float = Field(description="Grasas en gramos")
    fiber_g: float = Field(default=0, description="Fibra en gramos")
    sugar_g: float = Field(default=0, description="Azúcar en gramos")
    sodium_mg: float = Field(default=0, description="Sodio en miligramos")

class MealNutrients(BaseModel):
    """Estructura simplificada de nutrientes - SOLO LOS VALORES QUE NECESITAS"""
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float = 0
    sugar_g: float = 0
    sodium_mg: float = 0

class MealAnalysisResponse(BaseModel):
    """Respuesta de análisis de comida"""
    ok: bool
    nutrients: MealNutrients
    metadata: Dict[str, Any] = {}

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

# ===========================
# Análisis directo con LangChain + JsonOutputParser
# ===========================

async def analyze_meal_direct(media_file: MediaFile) -> MealNutrients:
    """
    Analiza comida usando LangChain con JsonOutputParser.
    Retorna SOLO los valores nutricionales - sin texto.
    """
    try:
        # Usar LangChain con ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=DEFAULT_MODEL,
            temperature=0.0,
            google_api_key=GOOGLE_API_KEY,
        )
        
        # Parser JSON
        parser = JsonOutputParser(pydantic_object=MealAnalysisModel)
        
        # Instrucciones de formato
        format_instructions = parser.get_format_instructions()
        
        # Crear mensaje con imagen
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": (
                        "Analiza esta imagen de comida y extrae SOLO estos valores nutricionales.\n"
                        "Sé preciso con los números estimados basándote en el tamaño de las porciones.\n\n"
                        f"{format_instructions}"
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{media_file.mime_type};base64,{__import__('base64').b64encode(media_file.data).decode('utf-8')}"
                    },
                },
            ],
        )
        
        # Invocar modelo
        print("[DEBUG] Invocando LangChain ChatGoogleGenerativeAI...")
        response = llm.invoke([message])
        response_text = response.content
        
        print(f"[DEBUG] Respuesta: {response_text[:300]}")
        
        # Parsear JSON
        parsed_data = parser.parse(response_text)
        print("[DEBUG] ✓ JSON parseado correctamente")
        
        # Retornar solo los valores
        return MealNutrients(
            calories=float(parsed_data.get("calories", 0)),
            protein_g=float(parsed_data.get("protein_g", 0)),
            carbs_g=float(parsed_data.get("carbs_g", 0)),
            fat_g=float(parsed_data.get("fat_g", 0)),
            fiber_g=float(parsed_data.get("fiber_g", 0)),
            sugar_g=float(parsed_data.get("sugar_g", 0)),
            sodium_mg=float(parsed_data.get("sodium_mg", 0)),
        )
    
    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Error: {str(e)}")


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
# Meal Analysis endpoint (solo imagen, JSON estructurado)
# -------------------------------
@app.post("/analyze-meal", tags=["meal"], response_model=MealAnalysisResponse)
async def analyze_meal(file: UploadFile = File(...)):
    """
    Analiza una comida desde una imagen y retorna nutrientes en JSON estructurado.
    Usa Gemini SDK directamente (sin LangGraph) para obtener JSON puro.
    
    - `file`: una única imagen (JPG, PNG, etc.)
    
    Retorna estructura JSON con:
    - `ok`: True si fue exitoso
    - `nutrients`: Objeto con macronutrientes, calorías, etc.
    - `metadata`: Información del procesamiento
    """
    try:
        if not file:
            raise HTTPException(status_code=400, detail="Se requiere una imagen")
        
        # Convertir UploadFile a MediaFile
        media_file = await uploadfile_to_media_file(file)
        
        # Analizar directamente con Gemini SDK (sin LangGraph)
        start_time = time.time()
        nutrients = await analyze_meal_direct(media_file)
        processing_time = (time.time() - start_time) * 1000
        
        metadata = {
            "method": "direct_gemini_sdk",
            "model": DEFAULT_MODEL,
            "processing_time_ms": processing_time,
        }
        
        return MealAnalysisResponse(
            ok=True,
            nutrients=nutrients,
            metadata=metadata,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        return MealAnalysisResponse(
            ok=False,
            nutrients=MealNutrients(
                food_name="Error",
                description=f"{type(e).__name__}: {e}",
                calories=0,
                protein_g=0,
                carbs_g=0,
                fat_g=0,
                fiber_g=0,
                sugar_g=0,
                sodium_mg=0,
            ),
            metadata={"error": str(e)},
        )


# ===========================
# Supabase Nutrition Endpoints
# ===========================

@app.get("/user/{user_id}/profile", tags=["nutrition"])
async def get_user_profile_endpoint(user_id: str):
    """
    Obtiene el perfil completo del usuario desde Supabase:
    - Métricas personales (peso, altura, objetivos de nutrición)
    - Últimos 30 días de registro de nutrición
    
    Args:
        user_id: UUID del usuario
    
    Returns:
        {
            "ok": true,
            "profile": {
                "metrics": { ... },
                "daily_nutrition": [ ... ]
            },
            "metadata": { ... }
        }
    """
    try:
        profile = await get_user_profile(user_id)
        return {
            "ok": True,
            "profile": profile,
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
            }
        }


@app.get("/user/{user_id}/metrics", tags=["nutrition"])
async def get_user_metrics_endpoint(user_id: str):
    """
    Obtiene solo las métricas personales del usuario.
    
    Args:
        user_id: UUID del usuario
    
    Returns:
        {
            "ok": true,
            "metrics": { weight, height, calorie_goal, ... },
            "metadata": { ... }
        }
    """
    try:
        metrics = await get_user_metrics(user_id)
        if not metrics:
            return {
                "ok": False,
                "error": f"User {user_id} not found",
            }
        return {
            "ok": True,
            "metrics": metrics,
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
            }
        }


@app.get("/user/{user_id}/nutrition/history", tags=["nutrition"])
async def get_nutrition_history(user_id: str, limit: int = 30):
    """
    Obtiene el historial de nutrición diaria del usuario (últimos N días).
    
    Args:
        user_id: UUID del usuario
        limit: Número máximo de días a retornar (default: 30)
    
    Returns:
        {
            "ok": true,
            "daily_nutrition": [ ... ],
            "metadata": { ... }
        }
    """
    try:
        daily_nutrition = await get_daily_nutrition(user_id, limit=limit)
        return {
            "ok": True,
            "daily_nutrition": daily_nutrition,
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
                "count": len(daily_nutrition),
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
            }
        }


@app.get("/user/{user_id}/nutrition/today", tags=["nutrition"])
async def get_today_nutrition_endpoint(user_id: str, date: str):
    """
    Obtiene el registro de nutrición de un día específico.
    
    Args:
        user_id: UUID del usuario
        date: Fecha en formato YYYY-MM-DD
    
    Returns:
        {
            "ok": true,
            "daily_nutrition": { ... },
            "metadata": { ... }
        }
    """
    try:
        nutrition = await get_today_nutrition(user_id, date)
        if not nutrition:
            return {
                "ok": False,
                "error": f"No nutrition record found for {date}",
            }
        return {
            "ok": True,
            "daily_nutrition": nutrition,
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
                "date": date,
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
            }
        }


# ===========================
# Nutrition Chatbot Endpoint
# ===========================

class ChatRequest(BaseModel):
    """Estructura de solicitud para el chatbot"""
    message: str
    user_name: Optional[str] = "Usuario"


class ChatResponse(BaseModel):
    """Estructura de respuesta del chatbot"""
    ok: bool
    response: str
    metadata: Dict[str, Any] = {}


@app.post("/chat/{user_id}", tags=["chatbot"], response_model=ChatResponse)
async def nutrition_chatbot(user_id: str, request: ChatRequest):
    """
    Chatbot de recomendaciones nutricionales con memory y contexto del usuario.
    
    El chatbot:
    - Recuerda el nombre del usuario
    - Mantiene historial de conversación
    - Recomienda comidas basado en objetivos nutricionales
    - Sugiere alimentos para cumplir metas diarias
    - Proporciona recomendaciones personalizadas
    
    Args:
        user_id: UUID del usuario
        request: {
            "message": "Tu pregunta o solicitud",
            "user_name": "Tu nombre (opcional)"
        }
    
    Returns:
        {
            "ok": true,
            "response": "Respuesta del chatbot",
            "metadata": { ... }
        }
    """
    try:
        if not request.message.strip():
            return ChatResponse(
                ok=False,
                response="El mensaje no puede estar vacío",
            )
        
        # Crear instancia del chatbot
        chatbot = NutritionChatbot(
            user_id=user_id,
            user_name=request.user_name or "Usuario",
        )
        
        # Procesar mensaje
        response_text, metadata = await chatbot.chat(request.message)
        
        return ChatResponse(
            ok=True,
            response=response_text,
            metadata=metadata,
        )
    
    except Exception as e:
        print(f"[ERROR] nutrition_chatbot: {str(e)}")
        return ChatResponse(
            ok=False,
            response=f"Error en el chatbot: {str(e)}",
            metadata={"error": str(e)},
        )


@app.get("/chat/{user_id}/history", tags=["chatbot"])
async def get_chat_history(user_id: str, limit: int = 50):
    """
    Obtiene el historial de conversación del usuario.
    
    Args:
        user_id: UUID del usuario
        limit: Número máximo de mensajes a retornar (default: 50)
    
    Returns:
        {
            "ok": true,
            "history": [ ... ],
            "metadata": { ... }
        }
    """
    try:
        history = await get_conversation_history(user_id, limit=limit)
        return {
            "ok": True,
            "history": history,
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
                "message_count": len(history),
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
            }
        }


@app.delete("/chat/{user_id}/history", tags=["chatbot"])
async def clear_chat_history(user_id: str):
    """
    Limpia el historial de conversación del usuario.
    
    Args:
        user_id: UUID del usuario
    
    Returns:
        {
            "ok": true,
            "message": "Historial eliminado",
            "metadata": { ... }
        }
    """
    try:
        await clear_conversation_history(user_id)
        return {
            "ok": True,
            "message": "Historial de conversación eliminado",
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "metadata": {
                "timestamp": time.time(),
                "user_id": user_id,
            }
        }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    print(f"[Swagger] http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)
