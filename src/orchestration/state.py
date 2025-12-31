"""
Definición de estados y tipos para LangGraph Orchestration
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class MediaType(Enum):
    """Tipos de medios soportados"""
    IMAGE = "image"
    PDF = "pdf"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class AnalysisType(Enum):
    """Tipos de análisis posibles"""
    NUTRITIONAL = "nutritional"
    RECIPE_SUGGESTION = "recipe_suggestion"
    MEAL_PLAN = "meal_plan"
    PRODUCT_LABEL = "product_label"
    HABIT_ANALYSIS = "habit_analysis"
    GENERAL_NUTRITION = "general_nutrition"


@dataclass
class MediaFile:
    """Estructura para archivos multimedia"""
    filename: str
    mime_type: str
    data: bytes
    media_type: MediaType = MediaType.UNKNOWN
    size_bytes: int = 0
    is_uploaded: bool = False
    file_id: Optional[str] = None  # Para archivos subidos a API de Gemini


@dataclass
class OrchestrationState:
    """
    Estado global para el flujo de orquestación LangGraph.
    Mantiene toda la información necesaria durante el procesamiento.
    """
    
    # Input del usuario
    question: str
    media_files: List[MediaFile] = field(default_factory=list)
    use_files_api: bool = False
    
    # Análisis y clasificación
    detected_analysis_types: List[AnalysisType] = field(default_factory=list)
    file_classifications: Dict[str, AnalysisType] = field(default_factory=dict)
    
    # Processing intermediate
    uploaded_file_ids: List[str] = field(default_factory=list)
    validation_passed: bool = True
    validation_errors: List[str] = field(default_factory=list)
    
    # Configuración de generación
    temperature: float = 0.2
    model_name: str = "gemini-2.5-flash"
    system_prompt: str = ""
    
    # Salida final
    answer: str = ""
    answer_markdown: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Auditoría y debugging
    execution_logs: List[Dict[str, Any]] = field(default_factory=list)
    processing_time_ms: float = 0.0
    
    def add_log(self, step: str, status: str, details: str = ""):
        """Registra un evento en el log de ejecución"""
        self.execution_logs.append({
            "step": step,
            "status": status,
            "details": details,
        })
    
    def add_validation_error(self, error: str):
        """Agrega un error de validación"""
        self.validation_errors.append(error)
        self.validation_passed = False
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna un resumen del estado para debugging"""
        return {
            "question": self.question[:100] + "..." if len(self.question) > 100 else self.question,
            "media_count": len(self.media_files),
            "analysis_types": [at.value for at in self.detected_analysis_types],
            "validation_passed": self.validation_passed,
            "answer_length": len(self.answer),
            "execution_logs": len(self.execution_logs),
            "processing_time_ms": self.processing_time_ms,
        }
