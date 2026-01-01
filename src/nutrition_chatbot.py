"""
Chatbot de recomendaciones nutricionales con memory
Usa LangChain para mantener contexto y hacer recomendaciones inteligentes
"""
import os
from datetime import datetime, date
from typing import List, Dict, Any, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate

from supabase_client import (
    get_user_metrics,
    get_daily_nutrition,
    get_conversation_history,
    save_conversation_message,
    UserMetrics,
    DailyNutrition,
)

# Config
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


class NutritionChatbot:
    """
    Chatbot especializado en recomendaciones nutricionales con memory
    """
    
    def __init__(self, user_id: str, user_name: str = "Usuario"):
        """
        Inicializa el chatbot para un usuario específico
        
        Args:
            user_id: UUID del usuario
            user_name: Nombre del usuario (para personalizacion)
        """
        self.user_id = user_id
        self.user_name = user_name
        self.llm = ChatGoogleGenerativeAI(
            model=DEFAULT_MODEL,
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY,
        )
    
    async def _build_context(self) -> Dict[str, Any]:
        """
        Construye el contexto del usuario (métricas, nutrición de hoy, historial)
        
        Returns:
            Dict con información del usuario
        """
        try:
            metrics = await get_user_metrics(self.user_id)
            today = date.today().isoformat()
            
            # Obtener nutrición de hoy
            daily_records = await get_daily_nutrition(self.user_id, limit=7)
            today_nutrition = next(
                (r for r in daily_records if r.date == today),
                None
            )
            
            context = {
                "user_name": self.user_name,
                "metrics": metrics,
                "today_nutrition": today_nutrition,
                "recent_nutrition": daily_records[:7],
            }
            
            return context
        
        except Exception as e:
            print(f"[ERROR] _build_context: {str(e)}")
            raise
    
    async def _get_conversation_memory(self, limit: int = 10) -> List[BaseMessage]:
        """
        Obtiene el historial de conversación formateado para LangChain
        
        Args:
            limit: Número de mensajes anteriores a recuperar
        
        Returns:
            Lista de mensajes (HumanMessage o SystemMessage)
        """
        try:
            history = await get_conversation_history(self.user_id, limit=limit)
            
            messages = []
            for msg in history:
                if msg.message_type == "user":
                    messages.append(HumanMessage(content=msg.content))
                else:
                    messages.append(SystemMessage(content=msg.content))
            
            return messages
        
        except Exception as e:
            print(f"[ERROR] _get_conversation_memory: {str(e)}")
            return []
    
    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """
        Formatea el contexto del usuario para incluir en el system prompt
        
        Args:
            context: Diccionario con información del usuario
        
        Returns:
            String formateado con contexto
        """
        metrics = context["metrics"]
        today_nutrition = context["today_nutrition"]
        
        context_str = f"""
=== CONTEXTO DEL USUARIO ===
Nombre: {context['user_name']}

MÉTRICAS PERSONALES:
- Peso: {metrics.weight} kg
- Altura: {metrics.height} cm
- IMC: {metrics.weight / ((metrics.height / 100) ** 2):.1f}

OBJETIVOS DIARIOS:
- Calorías: {metrics.calorie_goal} kcal
- Proteína: {metrics.protein_goal}g
- Carbohidratos: {metrics.carbs_goal}g
- Grasas: {metrics.fat_goal}g
"""
        
        if today_nutrition:
            remaining_calories = metrics.calorie_goal - today_nutrition.calories
            remaining_protein = metrics.protein_goal - today_nutrition.protein
            remaining_carbs = metrics.carbs_goal - today_nutrition.carbs
            remaining_fat = metrics.fat_goal - today_nutrition.fat
            
            context_str += f"""
CONSUMO DE HOY ({today_nutrition.date}):
- Calorías consumidas: {today_nutrition.calories} kcal (Falta: {remaining_calories:.0f} kcal)
- Proteína: {today_nutrition.protein}g (Falta: {remaining_protein:.0f}g)
- Carbohidratos: {today_nutrition.carbs}g (Falta: {remaining_carbs:.0f}g)
- Grasas: {today_nutrition.fat}g (Falta: {remaining_fat:.0f}g)
"""
        
        return context_str
    
    async def chat(self, user_message: str) -> Tuple[str, Dict[str, Any]]:
        """
        Procesa un mensaje del usuario y retorna la respuesta del chatbot
        
        Args:
            user_message: Mensaje del usuario
        
        Returns:
            Tupla (respuesta_texto, metadata)
        """
        try:
            # Construir contexto
            context = await self._build_context()
            context_str = self._format_context_for_prompt(context)
            
            # Obtener historial
            memory_messages = await self._get_conversation_memory(limit=5)
            
            # System prompt
            system_prompt = f"""Eres un experto nutricionista y asistente de salud personalizado.
Tu rol es:
1. Recomendar comidas y alimentos que ayuden a cumplir los objetivos de nutrición
2. Sugerir opciones de alimentos balanceados basado en lo que ya consumió hoy
3. Ser amable, motivador y proporcionar consejos prácticos
4. Considerar siempre los objetivos nutricionales del usuario
5. Sugerir alternativas saludables y deliciosas

{context_str}

Responde siempre en español de manera amigable y profesional.
Proporciona recomendaciones específicas basadas en los datos del usuario."""
            
            # Construir mensajes para LangChain
            messages = [
                SystemMessage(content=system_prompt),
                *memory_messages,
                HumanMessage(content=user_message),
            ]
            
            # Invocar LLM
            print(f"[DEBUG] Invocando chatbot para usuario {self.user_name}...")
            response = self.llm.invoke(messages)
            assistant_response = response.content
            
            # Guardar en historial
            await save_conversation_message(
                user_id=self.user_id,
                message_type="user",
                content=user_message,
            )
            await save_conversation_message(
                user_id=self.user_id,
                message_type="assistant",
                content=assistant_response,
            )
            
            metadata = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_name": self.user_name,
                "model": DEFAULT_MODEL,
                "context_available": True,
                "memory_messages_count": len(memory_messages),
            }
            
            return assistant_response, metadata
        
        except Exception as e:
            print(f"[ERROR] chat: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
