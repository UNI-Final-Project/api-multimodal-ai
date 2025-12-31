"""
orchestration_config.py - Configuración centralizada para LangGraph Orchestration
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class EnvironmentMode(Enum):
    """Modo de ejecución"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ValidationConfig:
    """Configuración de validación de entrada"""
    
    # Límites de tamaño
    MAX_TOTAL_FILE_SIZE: int = 500 * 1024 * 1024  # 500 MB
    MAX_SINGLE_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    MAX_FILES_COUNT: int = 10
    
    # Límites de pregunta
    MIN_QUESTION_LENGTH: int = 3
    MAX_QUESTION_LENGTH: int = 5000
    
    # Mimetypes permitidos
    ALLOWED_MIMETYPES: List[str] = None
    
    def __post_init__(self):
        if self.ALLOWED_MIMETYPES is None:
            self.ALLOWED_MIMETYPES = [
                "image/jpeg", "image/png", "image/webp", "image/gif",
                "application/pdf",
                "audio/mpeg", "audio/wav", "audio/ogg",
                "video/mp4", "video/webm",
                "text/plain", "text/csv",
            ]


@dataclass
class FilesAPIConfig:
    """Configuración de Gemini Files API"""
    
    # Threshold para usar Files API
    SIZE_THRESHOLD: int = 20 * 1024 * 1024  # >20 MB
    
    # Timeout de upload
    UPLOAD_TIMEOUT_SECONDS: int = 120
    
    # Reintentos
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 2
    
    # Limpieza
    AUTO_CLEANUP: bool = True  # Borrar archivos después de usar


@dataclass
class GenerationConfig:
    """Configuración de generación de respuestas"""
    
    # Modelo
    DEFAULT_MODEL: str = "gemini-2.5-flash"
    FALLBACK_MODEL: str = "gemini-2.5-pro"
    
    # Temperatura (0.0 = determinista, 1.0 = creativo)
    DEFAULT_TEMPERATURE: float = 0.2  # Conservador para nutrición
    
    # Parámetros de generación
    MAX_OUTPUT_TOKENS: int = 2048
    TOP_P: float = 0.95
    TOP_K: int = 40
    
    # Timeouts
    GENERATION_TIMEOUT_SECONDS: int = 60
    
    # Reintentos automáticos
    MAX_GENERATION_RETRIES: int = 2
    RETRY_DELAY_SECONDS: int = 1


@dataclass
class ClassificationConfig:
    """Configuración de clasificación de análisis"""
    
    # Keywords para detección de tipos de análisis
    ANALYSIS_KEYWORDS: Dict[str, List[str]] = None
    
    # Confidence thresholds (0.0 - 1.0)
    MIN_CONFIDENCE: float = 0.3
    
    def __post_init__(self):
        if self.ANALYSIS_KEYWORDS is None:
            self.ANALYSIS_KEYWORDS = {
                "nutritional": [
                    "nutrición", "caloría", "grasa", "proteína", "carbohidrato",
                    "macronutriente", "vitamina", "mineral", "fibra", "sodio",
                    "azúcar", "equilibrado", "saludable", "energía",
                ],
                "recipe_suggestion": [
                    "receta", "idea", "cómo hacer", "preparar", "ingrediente",
                    "cocina", "cocinar", "hacer", "sugerencia", "propuesta",
                    "alternativa", "cambio", "modificación",
                ],
                "product_label": [
                    "etiqueta", "producto", "envasado", "composición",
                    "ingredientes", "alérgeno", "información nutricional",
                    "marca", "porción",
                ],
                "meal_plan": [
                    "plan", "menú", "semana", "diario", "programación",
                    "desayuno", "almuerzo", "cena", "snack", "horario",
                    "distribución",
                ],
                "habit_analysis": [
                    "hábito", "costumbre", "frecuencia", "rutina",
                    "diario", "regularidad", "patrón", "comportamiento",
                ],
            }


@dataclass
class PromptEnrichmentConfig:
    """Configuración de enriquecimiento de prompts"""
    
    # Sufijos de prompt para cada tipo de análisis
    ANALYSIS_SUFFIXES: Dict[str, str] = None
    
    def __post_init__(self):
        if self.ANALYSIS_SUFFIXES is None:
            self.ANALYSIS_SUFFIXES = {
                "recipe_suggestion": (
                    "\n\n[ÉNFASIS RECETAS] El usuario busca ideas de recetas. "
                    "Proporciona de 3-5 opciones con nombres en negrita, descripción breve y tipo de aporte nutricional."
                ),
                "product_label": (
                    "\n\n[ÉNFASIS ETIQUETA] Estás analizando una etiqueta nutricional. "
                    "Interpreta valores clave (kcal, azúcar, grasas, proteína, sodio) y da recomendaciones."
                ),
                "meal_plan": (
                    "\n\n[ÉNFASIS PLAN] El usuario solicita un plan de comidas o menú. "
                    "Sé práctico y realista, considerando equilibrio nutricional."
                ),
                "habit_analysis": (
                    "\n\n[ÉNFASIS HÁBITOS] Analiza patrones de consumo y hábitos alimenticios. "
                    "Sugiere cambios gradualmente realizables."
                ),
            }


@dataclass
class LoggingConfig:
    """Configuración de logging y auditoría"""
    
    # Nivel de logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Qué registrar
    LOG_VALIDATIONS: bool = True
    LOG_CLASSIFICATIONS: bool = True
    LOG_API_CALLS: bool = True
    LOG_EXECUTION_TIME: bool = True
    
    # Guardar logs en archivo
    SAVE_LOGS_TO_FILE: bool = False
    LOG_FILE_PATH: str = "logs/orchestration.log"
    
    # Nivel de detalle en respuestas
    INCLUDE_EXECUTION_LOGS_IN_RESPONSE: bool = True
    INCLUDE_METADATA_IN_RESPONSE: bool = True


@dataclass
class CacheConfig:
    """Configuración de caching (futuro)"""
    
    ENABLED: bool = False
    BACKEND: str = "memory"  # memory, redis
    TTL_SECONDS: int = 3600  # 1 hora
    MAX_ENTRIES: int = 1000


@dataclass
class OrchestrationConfig:
    """Configuración global de orquestación"""
    
    mode: EnvironmentMode = EnvironmentMode.DEVELOPMENT
    
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    files_api: FilesAPIConfig = field(default_factory=FilesAPIConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    classification: ClassificationConfig = field(default_factory=ClassificationConfig)
    prompt_enrichment: PromptEnrichmentConfig = field(default_factory=PromptEnrichmentConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    # Settings globales
    ENABLE_PARALLEL_PROCESSING: bool = False  # LangGraph feature
    STREAM_RESPONSES: bool = False
    
    @staticmethod
    def for_environment(env: str) -> "OrchestrationConfig":
        """Factory method para crear configuración por ambiente"""
        config = OrchestrationConfig()
        
        if env == "production":
            config.mode = EnvironmentMode.PRODUCTION
            config.generation.MAX_GENERATION_RETRIES = 3
            config.logging.LOG_LEVEL = "WARNING"
            config.files_api.AUTO_CLEANUP = True
            config.cache.ENABLED = True
            config.cache.BACKEND = "redis"
            
        elif env == "staging":
            config.mode = EnvironmentMode.STAGING
            config.logging.LOG_LEVEL = "INFO"
            
        return config


# Instancia global (singleton)
_global_config: OrchestrationConfig = None


def get_config() -> OrchestrationConfig:
    """Obtiene configuración global"""
    global _global_config
    if _global_config is None:
        import os
        env = os.environ.get("ENVIRONMENT", "development")
        _global_config = OrchestrationConfig.for_environment(env)
    return _global_config


def set_config(config: OrchestrationConfig):
    """Establece configuración global"""
    global _global_config
    _global_config = config


# Ejemplo de uso:
if __name__ == "__main__":
    config = get_config()
    print(f"Modo: {config.mode.value}")
    print(f"Temperatura generación: {config.generation.DEFAULT_TEMPERATURE}")
    print(f"Max archivos: {config.validation.MAX_FILES_COUNT}")
    print(f"Files API threshold: {config.files_api.SIZE_THRESHOLD / 1024 / 1024:.0f}MB")
