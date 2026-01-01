"""
Cliente de Supabase para manejar datos de nutrición del usuario
"""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from pydantic import BaseModel

# Cargar variables de ambiente
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_NUTRITION_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_NUTRITION_ANON_KEY")

# Crear cliente de Supabase
supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Obtiene o crea el cliente de Supabase
    """
    global supabase_client
    if supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "Missing Supabase credentials. Check NEXT_PUBLIC_SUPABASE_NUTRITION_URL "
                "and NEXT_PUBLIC_SUPABASE_NUTRITION_ANON_KEY in .env"
            )
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase_client


# ===== Modelos Pydantic para las respuestas =====

class UserMetrics(BaseModel):
    """Datos de métricas del usuario"""
    id: str
    user_id: str
    weight: float
    height: float
    calorie_goal: float
    protein_goal: float
    carbs_goal: float
    fat_goal: float
    created_at: str
    updated_at: str


class DailyNutrition(BaseModel):
    """Datos de nutrición diaria del usuario"""
    id: str
    user_id: str
    date: str
    calories: float
    protein: float
    carbs: float
    fat: float
    created_at: str
    updated_at: str


class ConversationMessage(BaseModel):
    """Mensaje en el historial de conversación"""
    id: str
    user_id: str
    message_type: str  # "user" o "assistant"
    content: str
    timestamp: str
    created_at: str


class UserNutritionProfile(BaseModel):
    """Perfil completo de nutrición del usuario"""
    metrics: UserMetrics
    daily_nutrition: List[DailyNutrition]


# ===== Funciones para interactuar con Supabase =====

async def get_user_metrics(user_id: str) -> Optional[UserMetrics]:
    """
    Obtiene las métricas del usuario desde la tabla user_metrics
    
    Args:
        user_id: UUID del usuario
    
    Returns:
        UserMetrics o None si no existe
    """
    try:
        client = get_supabase_client()
        response = client.table("user_metrics").select("*").eq("user_id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            return UserMetrics(**response.data[0])
        return None
    except Exception as e:
        print(f"[ERROR] get_user_metrics: {str(e)}")
        raise Exception(f"Error fetching user metrics: {str(e)}")


async def get_daily_nutrition(user_id: str, limit: int = 30) -> List[DailyNutrition]:
    """
    Obtiene el historial de nutrición diaria del usuario
    
    Args:
        user_id: UUID del usuario
        limit: Número máximo de registros (últimos N días)
    
    Returns:
        Lista de DailyNutrition
    """
    try:
        client = get_supabase_client()
        response = (
            client.table("daily_nutrition")
            .select("*")
            .eq("user_id", user_id)
            .order("date", desc=True)
            .limit(limit)
            .execute()
        )
        
        return [DailyNutrition(**record) for record in response.data]
    except Exception as e:
        print(f"[ERROR] get_daily_nutrition: {str(e)}")
        raise Exception(f"Error fetching daily nutrition: {str(e)}")


async def get_today_nutrition(user_id: str, date: str) -> Optional[DailyNutrition]:
    """
    Obtiene el registro de nutrición de un día específico
    
    Args:
        user_id: UUID del usuario
        date: Fecha en formato YYYY-MM-DD
    
    Returns:
        DailyNutrition o None si no existe
    """
    try:
        client = get_supabase_client()
        response = (
            client.table("daily_nutrition")
            .select("*")
            .eq("user_id", user_id)
            .eq("date", date)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            return DailyNutrition(**response.data[0])
        return None
    except Exception as e:
        print(f"[ERROR] get_today_nutrition: {str(e)}")
        raise Exception(f"Error fetching today nutrition: {str(e)}")


async def create_or_update_daily_nutrition(
    user_id: str,
    date: str,
    calories: float,
    protein: float,
    carbs: float,
    fat: float,
) -> DailyNutrition:
    """
    Crea o actualiza el registro de nutrición diaria
    
    Args:
        user_id: UUID del usuario
        date: Fecha en formato YYYY-MM-DD
        calories: Calorías consumidas
        protein: Proteína en gramos
        carbs: Carbohidratos en gramos
        fat: Grasas en gramos
    
    Returns:
        DailyNutrition actualizado/creado
    """
    try:
        client = get_supabase_client()
        
        # Verificar si existe el registro
        existing = (
            client.table("daily_nutrition")
            .select("*")
            .eq("user_id", user_id)
            .eq("date", date)
            .execute()
        )
        
        if existing.data and len(existing.data) > 0:
            # Actualizar
            response = (
                client.table("daily_nutrition")
                .update({
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat,
                })
                .eq("id", existing.data[0]["id"])
                .execute()
            )
        else:
            # Crear
            response = (
                client.table("daily_nutrition")
                .insert({
                    "user_id": user_id,
                    "date": date,
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fat": fat,
                })
                .execute()
            )
        
        if response.data and len(response.data) > 0:
            return DailyNutrition(**response.data[0])
        else:
            raise Exception("Error creating/updating daily nutrition record")
    
    except Exception as e:
        print(f"[ERROR] create_or_update_daily_nutrition: {str(e)}")
        raise Exception(f"Error saving daily nutrition: {str(e)}")


async def get_user_profile(user_id: str) -> UserNutritionProfile:
    """
    Obtiene el perfil completo del usuario (métricas + últimos registros de nutrición)
    
    Args:
        user_id: UUID del usuario
    
    Returns:
        UserNutritionProfile con métricas y nutrición diaria
    """
    metrics = await get_user_metrics(user_id)
    if not metrics:
        raise Exception(f"User with id {user_id} not found")
    
    daily_nutrition = await get_daily_nutrition(user_id, limit=30)
    
    return UserNutritionProfile(
        metrics=metrics,
        daily_nutrition=daily_nutrition,
    )


# ===== Funciones para Historial de Conversaciones =====

async def save_conversation_message(
    user_id: str,
    message_type: str,
    content: str,
) -> ConversationMessage:
    """
    Guarda un mensaje en el historial de conversación
    
    Args:
        user_id: UUID del usuario
        message_type: 'user' o 'assistant'
        content: Contenido del mensaje
    
    Returns:
        ConversationMessage guardado
    """
    try:
        client = get_supabase_client()
        timestamp = datetime.utcnow().isoformat()
        
        response = (
            client.table("conversation_history")
            .insert({
                "user_id": user_id,
                "message_type": message_type,
                "content": content,
                "timestamp": timestamp,
            })
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            return ConversationMessage(**response.data[0])
        else:
            raise Exception("Error saving conversation message")
    
    except Exception as e:
        print(f"[ERROR] save_conversation_message: {str(e)}")
        raise Exception(f"Error saving message: {str(e)}")


async def get_conversation_history(
    user_id: str,
    limit: int = 50,
) -> List[ConversationMessage]:
    """
    Obtiene el historial de conversación del usuario
    
    Args:
        user_id: UUID del usuario
        limit: Número máximo de mensajes a retornar
    
    Returns:
        Lista de ConversationMessage ordenados por timestamp
    """
    try:
        client = get_supabase_client()
        response = (
            client.table("conversation_history")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        
        return [ConversationMessage(**record) for record in response.data]
    
    except Exception as e:
        print(f"[ERROR] get_conversation_history: {str(e)}")
        raise Exception(f"Error fetching conversation history: {str(e)}")


async def clear_conversation_history(user_id: str) -> bool:
    """
    Limpia el historial de conversación de un usuario
    
    Args:
        user_id: UUID del usuario
    
    Returns:
        True si se limpió correctamente
    """
    try:
        client = get_supabase_client()
        client.table("conversation_history").delete().eq("user_id", user_id).execute()
        return True
    except Exception as e:
        print(f"[ERROR] clear_conversation_history: {str(e)}")
        raise Exception(f"Error clearing conversation history: {str(e)}")
