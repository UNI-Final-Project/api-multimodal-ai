# NutriApp QA Multimodal API v2.0

Orquestación de flujos multimodales con **LangGraph** + **FastAPI** + **Google Gemini**

## 📁 Estructura del Proyecto

```
Proyecto IA food/
│
├── 📂 src/                          Código fuente principal
│   ├── MultimediaLLM.py            FastAPI application
│   ├── __init__.py
│   └── 📂 orchestration/           Módulo de orquestación
│       ├── __init__.py
│       ├── state.py                Definiciones de estado
│       ├── graph.py                Grafo compilado (6 nodos)
│       └── config.py               Configuración centralizada
│
├── 📂 docs/                        Documentación
│   ├── BIENVENIDA.txt
│   ├── INICIO_RAPIDO.md
│   ├── README_LANGGRAPH.md
│   ├── ORCHESTRATION.md
│   ├── ESTRUCTURA.md
│   ├── INDICE.md
│   ├── RESUMEN_EJECUTIVO.txt
│   ├── IMPLEMENTACION_COMPLETA.txt
│   └── README_IMPLEMENTACION.txt
│
├── 📂 tests/                       Tests y ejemplos
│   └── examples_and_tests.py       6 tests unitarios + 4 ejemplos
│
├── 📂 scripts/                     Scripts de utilidad
│   └── verify_implementation.py    Verificación de setup
│
├── 📂 config/                      Configuración del proyecto
│   ├── .env                        Variables de entorno
│   └── requirements.txt            Dependencias Python
│
├── 📂 deployment/                  Archivos de deployment
│   ├── Dockerfile
│   └── gcp-ia-food-api.yaml
│
└── ⚙️ Archivos de raíz (LEGACY, mirar en carpetas respectivas)
    ├── .git/
    ├── .venv/
    ├── .gitignore
    └── .dockerignore
```

---

## 🚀 Inicio Rápido

### 1️⃣ Instalación (2 min)

```bash
# Instalar dependencias
pip install -r config/requirements.txt
```

### 2️⃣ Configuración (2 min)

```bash
# Editar config/.env
GOOGLE_API_KEY=sk-...
GEMINI_MODEL=gemini-2.5-flash
PORT=8080
```

### 3️⃣ Ejecutar (2 min)

```bash
# Ejecutar servidor
python src/MultimediaLLM.py
```

### 4️⃣ Probar (2 min)

```bash
# Acceder a API docs
http://localhost:8080/docs
```

---

## 📚 Documentación

| Documento | Tiempo | Propósito |
|-----------|--------|----------|
| `docs/BIENVENIDA.txt` | 2 min | Resumen visual |
| `docs/INICIO_RAPIDO.md` | 10 min | Primeros pasos |
| `docs/README_LANGGRAPH.md` | 5 min | Guía rápida |
| `docs/ORCHESTRATION.md` | 15 min | Documentación técnica |
| `docs/ESTRUCTURA.md` | 10 min | Diagramas y flujos |
| `docs/INDICE.md` | 5 min | Índice de navegación |

---

## 🎯 Estructura del Código

### `src/orchestration/`

```python
# state.py
- MediaType enum           Tipos de medios (IMAGE, PDF, AUDIO, etc)
- AnalysisType enum       Tipos de análisis (NUTRITIONAL, RECIPE, etc)
- MediaFile dataclass     Archivo multimedia
- OrchestrationState      Estado centralizado del flujo

# graph.py
- validate_input()        Nodo 1: Validación
- classify_media()        Nodo 2: Clasificación
- upload_large_files()    Nodo 3: Upload Files API
- enrich_system_prompt()  Nodo 4: Enriquecimiento
- generate_answer()       Nodo 5: Generación
- cleanup_uploads()       Nodo 6: Limpieza
- build_orchestration_graph()   Construcción del grafo
- invoke_orchestration()        Entry point

# config.py
- ValidationConfig        Límites de validación
- GenerationConfig        Parámetros de generación
- FilesAPIConfig          Configuración Files API
- OrchestrationConfig     Configuración global
```

### `src/MultimediaLLM.py`

```python
# FastAPI application
@app.get("/health")      Health check
@app.get("/env-check")   Verificar variables
@app.post("/qa")         Endpoint principal (integración con orchestration)

# Helper functions
uploadfile_to_media_file()    Conversión de archivos
```

---

## 🧪 Testing

```bash
# Tests unitarios
python tests/examples_and_tests.py --tests

# Ejemplos completos
python tests/examples_and_tests.py --examples

# Verificar setup
python scripts/verify_implementation.py
```

---

## 📦 Dependencias

```
langgraph==0.2.52              Compilación de grafos
langchain==0.3.0               Framework LLM
langchain-google-genai==1.0.7  Google Gemini
fastapi==0.121.2               Web framework
google-genai==1.50.1           Gemini SDK nuevo
google-generativeai==0.8.5     Gemini SDK viejo (fallback)
```

Ver `config/requirements.txt` para lista completa.

---

## 🎯 Flujo de Orquestación

```
POST /qa (question + files)
    ↓
[validate_input] Validar entrada
    ↓
[classify_media] Clasificar tipos de análisis
    ↓
[upload_large_files] Subir archivos >20MB a Files API
    ↓
[enrich_system_prompt] Enriquecer prompt según análisis
    ↓
[generate_answer] Generar respuesta con Gemini
    ↓
[cleanup_uploads] Limpiar archivos subidos
    ↓
{ok, answer, metadata}
```

---

## ⚙️ Configuración

### Variables de Entorno (`config/.env`)

```env
# Obligatorio
GOOGLE_API_KEY=sk-...

# Opcional
GEMINI_MODEL=gemini-2.5-flash
PORT=8080
ENVIRONMENT=development  # development, staging, production
```

### Parámetros (`src/orchestration/config.py`)

```python
# Validación
MAX_TOTAL_FILE_SIZE = 500MB
MAX_SINGLE_FILE_SIZE = 50MB
MAX_FILES_COUNT = 10

# Generación
DEFAULT_TEMPERATURE = 0.2
GENERATION_TIMEOUT_SECONDS = 60

# Files API
SIZE_THRESHOLD = 20MB
AUTO_CLEANUP = True
```

---

## 🚢 Deployment

```bash
# Docker
docker build -t nutriapp deployment/
docker run -e GOOGLE_API_KEY=sk-... nutriapp

# GCP (Cloud Run)
cat deployment/gcp-ia-food-api.yaml
```

---

## 📊 Respuesta Típica

```json
{
  "ok": true,
  "answer": "# Análisis del plato\n\nSí, es equilibrado...",
  "metadata": {
    "analysis_types": ["nutritional"],
    "processing_time_ms": 2345.67,
    "execution_logs": [
      {"step": "validate_input", "status": "success"},
      {"step": "classify_media", "status": "success"},
      {"step": "generate_answer", "status": "success"}
    ]
  }
}
```

---

## ✅ Checklist Inicial

- [ ] `pip install -r config/requirements.txt`
- [ ] Configurar `config/.env` con GOOGLE_API_KEY
- [ ] `python src/MultimediaLLM.py`
- [ ] Acceder a `http://localhost:8080/docs`
- [ ] Leer `docs/INICIO_RAPIDO.md`

---

## 🔗 Recursos

| Recurso | Ubicación |
|---------|-----------|
| API Documentation | `http://localhost:8080/docs` |
| Guía Rápida | `docs/INICIO_RAPIDO.md` |
| Arquitectura | `docs/ORCHESTRATION.md` |
| Código | `src/orchestration/` |
| Tests | `tests/examples_and_tests.py` |
| Config | `config/` |

---

## 📞 Soporte

1. Lee `docs/INICIO_RAPIDO.md` para primeros pasos
2. Consulta `docs/INDICE.md` para navegar documentación
3. Ejecuta `python scripts/verify_implementation.py` para diagnóstico
4. Revisa `execution_logs` en respuestas JSON para debugging

---

**Versión:** 2.0.0  
**Estado:** ✅ Listo para Producción  
**Última actualización:** Diciembre 2025
