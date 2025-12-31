"""
Orquestación de flujos multimodales con LangGraph
Gestiona: validación → clasificación → procesamiento → generación
"""

import time
import os
from pathlib import Path
from typing import List, Optional, Tuple, Any, Dict
import io

# Cargar .env si no está ya cargado
try:
    from dotenv import load_dotenv
    # Intenta cargar desde config/.env o .env en raíz
    project_root = Path(__file__).resolve().parent.parent.parent
    load_dotenv(project_root / "config" / ".env", override=False)
    load_dotenv(project_root / ".env", override=False)
except:
    pass

# LangGraph
from langgraph.graph import StateGraph, END

# LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

# Gemini SDK (fallback)
try:
    from google import genai as google_genai
    from google.genai.types import Part
    USING_NEW_SDK = True
except:
    import google.generativeai as google_genai
    USING_NEW_SDK = False

# Local
from .state import (
    OrchestrationState,
    MediaFile,
    MediaType,
    AnalysisType,
)

# Config
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# Cliente Gemini - lazy initialization (se crea cuando sea necesario)
_gemini_client = None

def _get_gemini_client():
    """Obtiene o crea el cliente de Gemini de forma lazy"""
    global _gemini_client
    if _gemini_client is None:
        if USING_NEW_SDK:
            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY no configurada. Verifica config/.env")
            _gemini_client = google_genai.Client(api_key=GOOGLE_API_KEY)
        else:
            if not GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY no configurada. Verifica config/.env")
            google_genai.configure(api_key=GOOGLE_API_KEY)
    return _gemini_client

gemini_client = None  # Placeholder

# System prompts (Spanish and English versions)
SYSTEM_INSTRUCTIONS_QA_ES = (
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
    "   - **Respuesta directa**: 2–4 líneas que contesten la pregunta de forma clara.\n"
    "   - **Análisis / Explicación nutricional**: describe los componentes principales.\n"
    "   - **Recomendaciones o siguientes pasos**: sugiere mejoras prácticas.\n\n"
    "4) Cuando el usuario pida **ideas de recetas**, propone de 3 a 5 ideas sencillas.\n"
    "5) Sé prudente: **no des diagnósticos médicos ni tratamientos**.\n"
    "6) Si la pregunta NO está relacionada con nutrición, aclara tu función.\n"
)

SYSTEM_INSTRUCTIONS_QA_EN = (
    "You are the multimodal assistant for **NutriApp**, specialized in nutrition, practical eating advice, "
    "and analysis of food-related content.\n\n"
    "Types of files you can receive:\n"
    "- Photos of meals, lunch boxes, snacks, or beverages.\n"
    "- Screenshots or PDFs of menus, meal plans, or recipes.\n"
    "- Nutritional labels of packaged products.\n"
    "- Simple reports related to weight, body measurements, or food diaries.\n\n"
    "Your main goal is to help the person **better understand what they are eating** and provide "
    "concrete ideas to improve their eating decisions, always in a clear and realistic way.\n\n"
    "Response instructions:\n"
    "1) Respond ALWAYS in **English**.\n"
    "2) Return ONLY **text in Markdown**, without code blocks (no ```), and no JSON.\n"
    "3) Use this recommended structure:\n"
    "   - **Direct answer**: 2–4 lines that clearly answer the question.\n"
    "   - **Analysis / Nutritional explanation**: describe the main components.\n"
    "   - **Recommendations or next steps**: suggest practical improvements.\n\n"
    "4) When the user asks for **recipe ideas**, propose 3 to 5 simple options.\n"
    "5) Be cautious: **do not provide medical diagnoses or treatments**.\n"
    "6) If the question is NOT related to nutrition, clarify your function.\n"
)


# ===========================
# NODOS DEL GRAFO
# ===========================

def validate_input(state: OrchestrationState) -> OrchestrationState:
    """
    Nodo 1: Validación de entrada (pregunta y archivos)
    """
    start_time = time.time()
    state.add_log("validate_input", "iniciado")
    
    # Validar pregunta
    if not state.question or not state.question.strip():
        state.add_validation_error("La pregunta está vacía")
    
    # Validar archivos
    if not state.media_files:
        state.add_validation_error("No se adjuntaron archivos")
    
    # Validar tamaño total
    total_size = sum(f.size_bytes for f in state.media_files)
    max_total = 500 * 1024 * 1024  # 500 MB
    if total_size > max_total:
        state.add_validation_error(f"Tamaño total de archivos excede {max_total / 1024 / 1024:.0f}MB")
    
    if state.validation_passed:
        state.add_log("validate_input", "success", f"{len(state.media_files)} archivos validados")
    else:
        state.add_log("validate_input", "failed", ", ".join(state.validation_errors))
    
    state.processing_time_ms = (time.time() - start_time) * 1000
    return state


def classify_media(state: OrchestrationState) -> OrchestrationState:
    """
    Nodo 2: Clasificación automática de tipos de medios y análisis
    """
    start_time = time.time()
    state.add_log("classify_media", "iniciado")
    
    if not state.validation_passed:
        state.add_log("classify_media", "skipped", "validación falló")
        return state
    
    mime_type_to_media_type = {
        "image": MediaType.IMAGE,
        "application/pdf": MediaType.PDF,
        "audio": MediaType.AUDIO,
        "video": MediaType.VIDEO,
        "text": MediaType.DOCUMENT,
    }
    
    # Clasificar archivos
    for media_file in state.media_files:
        mime_type = media_file.mime_type.lower()
        for key, mtype in mime_type_to_media_type.items():
            if key in mime_type:
                media_file.media_type = mtype
                break
    
    # Detectar tipos de análisis basado en medios + pregunta
    has_image = any(f.media_type == MediaType.IMAGE for f in state.media_files)
    has_pdf = any(f.media_type == MediaType.PDF for f in state.media_files)
    question_lower = state.question.lower()
    
    analysis_keywords = {
        AnalysisType.NUTRITIONAL: ["nutrición", "caloría", "grasa", "proteína", "carbohidrato", "macronutrientes"],
        AnalysisType.RECIPE_SUGGESTION: ["receta", "idea", "cómo hacer", "preparar", "ingrediente"],
        AnalysisType.PRODUCT_LABEL: ["etiqueta", "producto", "envasado", "composición"],
        AnalysisType.MEAL_PLAN: ["plan", "menú", "semana", "diario"],
        AnalysisType.HABIT_ANALYSIS: ["hábito", "costumbre", "frecuencia"],
    }
    
    for analysis_type, keywords in analysis_keywords.items():
        if any(kw in question_lower for kw in keywords):
            state.detected_analysis_types.append(analysis_type)
    
    # Default si no se detectó nada
    if not state.detected_analysis_types:
        state.detected_analysis_types.append(AnalysisType.GENERAL_NUTRITION)
    
    state.add_log(
        "classify_media",
        "success",
        f"Detectados análisis: {[at.value for at in state.detected_analysis_types]}"
    )
    state.processing_time_ms += (time.time() - start_time) * 1000
    return state


def upload_large_files(state: OrchestrationState) -> OrchestrationState:
    """
    Nodo 3: Sube archivos grandes vía Files API (si está habilitado y es SDK nuevo)
    """
    start_time = time.time()
    state.add_log("upload_large_files", "iniciado")
    
    if not state.validation_passed or not state.use_files_api or not USING_NEW_SDK:
        state.add_log("upload_large_files", "skipped", "No habilitado o SDK viejo")
        return state
    
    try:
        for i, media_file in enumerate(state.media_files):
            if media_file.size_bytes > 20 * 1024 * 1024:  # >20MB
                file_obj = io.BytesIO(media_file.data)
                client = _get_gemini_client()
                uploaded = client.files.upload(
                    file=file_obj,
                    name=media_file.filename,
                    mime_type=media_file.mime_type,
                )
                media_file.file_id = uploaded.name if hasattr(uploaded, 'name') else str(uploaded)
                media_file.is_uploaded = True
                state.uploaded_file_ids.append(media_file.file_id)
                state.add_log("upload_large_files", "success", f"Archivo {i+1} subido: {media_file.filename}")
    except Exception as e:
        state.add_log("upload_large_files", "warning", f"Error al subir: {str(e)}")
    
    state.processing_time_ms += (time.time() - start_time) * 1000
    return state


def enrich_system_prompt(state: OrchestrationState) -> OrchestrationState:
    """
    Nodo 4: Enriquece el prompt del sistema basado en tipos de análisis detectados
    e idioma del usuario
    """
    start_time = time.time()
    state.add_log("enrich_system_prompt", "iniciado")
    
    # Detectar idioma de la pregunta
    detected_lang = _detect_language(state.question)
    state.language = detected_lang
    
    # Seleccionar prompt base según idioma detectado
    base_prompt = SYSTEM_INSTRUCTIONS_QA_ES if detected_lang == "es" else SYSTEM_INSTRUCTIONS_QA_EN
    additional_context = ""
    
    if AnalysisType.RECIPE_SUGGESTION in state.detected_analysis_types:
        if detected_lang == "es":
            additional_context += (
                "\n\n[ÉNFASIS RECETAS] El usuario busca ideas de recetas. "
                "Proporciona de 3-5 opciones con nombres en negrita, descripción breve y tipo de aporte nutricional."
            )
        else:
            additional_context += (
                "\n\n[EMPHASIS RECIPES] The user is looking for recipe ideas. "
                "Provide 3-5 options with names in bold, brief description, and type of nutritional contribution."
            )
    
    if AnalysisType.PRODUCT_LABEL in state.detected_analysis_types:
        if detected_lang == "es":
            additional_context += (
                "\n\n[ÉNFASIS ETIQUETA] Estás analizando un etiqueta nutricional. "
                "Interpreta valores clave (kcal, azúcar, grasas, proteína, sodio) y da recomendaciones."
            )
        else:
            additional_context += (
                "\n\n[EMPHASIS LABEL] You are analyzing a nutritional label. "
                "Interpret key values (kcal, sugar, fats, protein, sodium) and provide recommendations."
            )
    
    if AnalysisType.MEAL_PLAN in state.detected_analysis_types:
        if detected_lang == "es":
            additional_context += (
                "\n\n[ÉNFASIS PLAN] El usuario solicita un plan de comidas o menú. "
                "Sé práctico y realista, considerando equilibrio nutricional."
            )
        else:
            additional_context += (
                "\n\n[EMPHASIS PLAN] The user is requesting a meal plan or menu. "
                "Be practical and realistic, considering nutritional balance."
            )
    
    state.system_prompt = base_prompt + additional_context
    state.add_log(
        "enrich_system_prompt",
        "success",
        f"Prompt enriquecido (idioma: {detected_lang}, análisis: {len(state.detected_analysis_types)})"
    )
    state.processing_time_ms += (time.time() - start_time) * 1000
    return state


def generate_answer(state: OrchestrationState) -> OrchestrationState:
    """
    Nodo 5: Genera respuesta usando Gemini con los archivos y prompt enriquecido
    """
    start_time = time.time()
    state.add_log("generate_answer", "iniciado")
    
    if not state.validation_passed:
        state.answer = "Error: Validación fallida. " + ", ".join(state.validation_errors)
        state.answer_markdown = state.answer
        state.add_log("generate_answer", "failed", "Skipped due to validation errors")
        return state
    
    try:
        # Construir mensaje con archivos
        if USING_NEW_SDK:
            parts = [state.system_prompt]
            
            # Agregar archivos (directo o referencia)
            for media_file in state.media_files:
                if media_file.is_uploaded:
                    # Referencia a archivo subido
                    parts.append(Part.from_uri(
                        uri=media_file.file_id,
                        mime_type=media_file.mime_type
                    ))
                else:
                    # Directo en bytes
                    parts.append(Part.from_bytes(
                        data=media_file.data,
                        mime_type=media_file.mime_type
                    ))
            
            parts.append(f"Pregunta del usuario: {state.question}")
            
            client = _get_gemini_client()
            response = client.models.generate_content(
                model=state.model_name,
                contents=parts,
                config={"temperature": state.temperature},
            )
            state.answer = getattr(response, "text", "") or ""
        
        else:
            # Fallback SDK viejo (solo bytes directo)
            model = google_genai.GenerativeModel(state.model_name)
            parts = [state.system_prompt]
            
            for media_file in state.media_files:
                parts.append(Part.from_bytes(
                    data=media_file.data,
                    mime_type=media_file.mime_type
                ))
            
            parts.append(f"Pregunta del usuario: {state.question}")
            response = model.generate_content(parts, generation_config={"temperature": state.temperature})
            state.answer = getattr(response, "text", "") or ""
        
        state.answer_markdown = _force_markdown(state.answer)
        state.add_log("generate_answer", "success", f"Respuesta generada ({len(state.answer)} caracteres)")
    
    except Exception as e:
        state.answer = f"Error al generar respuesta: {type(e).__name__}: {e}"
        state.answer_markdown = state.answer
        state.add_log("generate_answer", "error", str(e))
    
    state.processing_time_ms += (time.time() - start_time) * 1000
    return state


def cleanup_uploads(state: OrchestrationState) -> OrchestrationState:
    """
    Nodo 6: Limpia archivos subidos a Files API (opcional, para mantener cuenta limpia)
    """
    start_time = time.time()
    state.add_log("cleanup_uploads", "iniciado")
    
    if not state.uploaded_file_ids or not USING_NEW_SDK:
        state.add_log("cleanup_uploads", "skipped", "Sin archivos para limpiar")
        return state
    
    try:
        for file_id in state.uploaded_file_ids:
            try:
                client = _get_gemini_client()
                client.files.delete(file_id)
                state.add_log("cleanup_uploads", "success", f"Borrado: {file_id}")
            except:
                pass  # Silenciar errores de borrado
    except Exception as e:
        state.add_log("cleanup_uploads", "warning", f"Cleanup error: {str(e)}")
    
    state.processing_time_ms += (time.time() - start_time) * 1000
    return state


# ===========================
# FUNCIONES AUXILIARES
# ===========================

def _detect_language(text: str) -> str:
    """
    Detecta si el texto está en español o inglés.
    Retorna 'es' para español, 'en' para inglés.
    """
    if not text:
        return "es"  # Default a español
    
    spanish_keywords = {
        "el", "la", "de", "que", "es", "y", "en", "un", "una", "los", "las",
        "por", "con", "para", "a", "se", "del", "al", "lo", "como", "más",
        "cómo", "qué", "cuál", "cuáles", "dónde", "cuándo", "cuánto", "cuántos",
        "receta", "nutrición", "caloría", "proteína", "carbohidrato", "grasa",
        "comida", "plato", "dieta", "plan", "menú", "etiqueta", "hábito"
    }
    
    english_keywords = {
        "the", "a", "and", "is", "in", "of", "to", "for", "that", "it",
        "with", "on", "as", "at", "be", "or", "by", "from", "this", "an",
        "how", "what", "which", "where", "when", "why", "recipe", "nutrition",
        "calorie", "protein", "carbohydrate", "fat", "meal", "diet", "plan",
        "menu", "label", "habit"
    }
    
    text_lower = text.lower()
    words = set(text_lower.split())
    
    spanish_count = len(words & spanish_keywords)
    english_count = len(words & english_keywords)
    
    # Si hay una diferencia clara, usar el idioma detectado
    if spanish_count > english_count:
        return "es"
    elif english_count > spanish_count:
        return "en"
    
    # Default a español si no hay diferencia clara
    return "es"


def _force_markdown(text: str) -> str:
    """Limpia fences de código y evita respuestas en JSON puro"""
    import re
    if not text:
        return ""
    t = text.strip()
    t = re.sub(r"^```(?:\w+)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    if t.strip().startswith("{") or t.strip().startswith("["):
        return "- " + t.replace("\n", "\n- ")
    return t


# ===========================
# CONSTRUCCIÓN DEL GRAFO
# ===========================

def build_orchestration_graph() -> Any:
    """
    Construye el grafo LangGraph de orquestación multimodal
    """
    
    # Crear StateGraph
    workflow = StateGraph(OrchestrationState)
    
    # Agregar nodos
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("classify_media", classify_media)
    workflow.add_node("upload_large_files", upload_large_files)
    workflow.add_node("enrich_system_prompt", enrich_system_prompt)
    workflow.add_node("generate_answer", generate_answer)
    workflow.add_node("cleanup_uploads", cleanup_uploads)
    
    # Definir flujo
    workflow.set_entry_point("validate_input")
    workflow.add_edge("validate_input", "classify_media")
    workflow.add_edge("classify_media", "upload_large_files")
    workflow.add_edge("upload_large_files", "enrich_system_prompt")
    workflow.add_edge("enrich_system_prompt", "generate_answer")
    workflow.add_edge("generate_answer", "cleanup_uploads")
    workflow.add_edge("cleanup_uploads", END)
    
    # Compilar grafo
    graph = workflow.compile()
    return graph


# Instancia global
_orchestration_graph = None


def get_orchestration_graph() -> Any:
    """Obtiene la instancia compilada del grafo (singleton)"""
    global _orchestration_graph
    if _orchestration_graph is None:
        _orchestration_graph = build_orchestration_graph()
    return _orchestration_graph


def invoke_orchestration(
    question: str,
    media_files: List[MediaFile],
    use_files_api: bool = False,
) -> Tuple[str, Dict]:
    """
    Invoca el flujo de orquestación y retorna (respuesta, metadatos)
    """
    graph = get_orchestration_graph()
    
    initial_state = OrchestrationState(
        question=question,
        media_files=media_files,
        use_files_api=use_files_api,
    )
    
    result = graph.invoke(initial_state)
    
    # Convertir el resultado a OrchestrationState si es necesario
    if isinstance(result, dict):
        # Si es diccionario, reconstruir el estado
        final_state = OrchestrationState(**result)
    else:
        final_state = result
    
    return (
        final_state.answer_markdown,
        final_state.get_summary(),
    )
