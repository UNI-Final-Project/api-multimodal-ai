# NutriApp - API de Análisis Nutricional Inteligente

Asistente nutricional impulsado por IA que analiza imágenes de comida, proporciona recomendaciones personalizadas y mantiene un historial de conversación con memoria contextual.

**Stack:** FastAPI • Google Gemini 2.5 Flash • LangChain • LangGraph • Supabase

---

## 📋 Tabla de Contenidos

- [Quick Start](#-quick-start)
- [Endpoints](#-endpoints)
- [Características](#-características)
- [Documentación](#-documentación)
- [Arquitectura](#-arquitectura)
- [Configuración](#-configuración)
- [Seguridad](#-seguridad)

---

## 🚀 Quick Start

### 1. Instalación
```bash
git clone <repo>
cd "Proyecto IA food"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar Variables de Ambiente
Crear archivo `config/.env`:
```env
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
NEXT_PUBLIC_SUPABASE_NUTRITION_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_NUTRITION_ANON_KEY=your_anon_key_here
PORT=8000
```

### 3. Configurar Supabase
Ejecutar estos SQL en la consola de Supabase:
```sql
-- user_metrics
CREATE TABLE user_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT UNIQUE NOT NULL,
  weight FLOAT, height FLOAT,
  calorie_goal FLOAT, protein_goal FLOAT,
  carbs_goal FLOAT, fat_goal FLOAT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- daily_nutrition
CREATE TABLE daily_nutrition (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL, date DATE NOT NULL,
  calories FLOAT DEFAULT 0, protein FLOAT DEFAULT 0,
  carbs FLOAT DEFAULT 0, fat FLOAT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, date)
);

-- conversation_history
CREATE TABLE conversation_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  message_type TEXT NOT NULL, content TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 4. Ejecutar
```bash
python main.py
```
Acceder a `http://localhost:8000/docs` para Swagger UI

---

## 📡 Endpoints

### 🖼️ Análisis de Imagen
**POST** `/analyze-meal`
- Analiza imagen de comida → JSON con nutrientes
- **Request:** `multipart/form-data` con imagen
- **Response:** `{ok, nutrients, metadata}`

```bash
curl -X POST "http://localhost:8000/analyze-meal" \
  -F "file=@meal.jpg"
```

### 👤 Usuario
| Endpoint | Método | Descripción |
|----------|--------|------------|
| `/user/{user_id}/profile` | GET | Perfil + métricas + nutrición |
| `/user/{user_id}/metrics` | GET | Solo métricas personales |
| `/user/{user_id}/nutrition/history` | GET | Historial de nutrición |
| `/user/{user_id}/nutrition/today` | GET | Nutrición de un día |

### 🤖 Chatbot
| Endpoint | Método | Descripción |
|----------|--------|------------|
| `/chat/{user_id}` | POST | Enviar mensaje al chatbot |
| `/chat/{user_id}/history` | GET | Ver historial de conversación |
| `/chat/{user_id}/history` | DELETE | Limpiar historial |

**Ejemplo POST /chat:**
```bash
curl -X POST "http://localhost:8000/chat/user-123" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Acabo de comer 450 calorías",
    "user_name": "Juan"
  }'
```

### 📊 QA Multimodal
**POST** `/qa`
- Analiza múltiples archivos (PDF, imágenes, audio)
- **Request:** `multipart/form-data` con pregunta y archivos

---

## ✨ Características

✅ **Análisis Inteligente de Imágenes**
- Extracción automática de nutrientes usando Gemini 2.5 Flash
- Soporte para JPEG, PNG, GIF, WebP
- JSON estructurado con calorías, macronutrientes, fibra, sodio

✅ **Chatbot Personalizado**
- Recomendaciones basadas en metas y consumo actual
- Memoria de conversación persistente en Supabase
- Contexto: peso, altura, metas, consumo del día

✅ **Bilingüe** 
- Detección automática: Español/Inglés
- Respuestas en idioma del usuario
- Dual system prompts para cada idioma

✅ **Integración Supabase**
- Persistencia de métricas personales
- Historial de nutrición diaria
- Memoria de conversaciones

✅ **LangGraph Orchestration**
- Workflows automáticos para QA
- Procesamiento paralelo de idiomas
- Validación de inputs

---

## 📚 Documentación

Documentación detallada disponible en `docs/`:

| Documento | Contenido |
|-----------|----------|
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Referencia completa de endpoints con ejemplos |
| [SETUP.md](docs/SETUP.md) | Guía paso a paso: instalación, configuración, troubleshooting |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Diagramas, flujos, modelos de datos, componentes |

---

## 🏗️ Arquitectura

```
Frontend (Next.js)
    ↓ HTTP/REST
┌─────────────────────┐
│  FastAPI           │
│  ├─ Endpoints      │
│  └─ Router         │
├─────────────────────┤
│  Lógica de Negocio  │
│  ├─ NutritionChatbot│
│  ├─ LangChain       │
│  └─ LangGraph       │
├─────────────────────┤
│  Integraciones      │
│  ├─ Gemini API      │
│  └─ Supabase        │
└─────────────────────┘
```

**Componentes Clave:**
- `main.py` - Punto de entrada (uvicorn server)
- `src/nutrition_api.py` - Endpoints FastAPI
- `src/nutrition_chatbot.py` - Lógica de chatbot con LangChain
- `src/supabase_client.py` - Cliente de Supabase + modelos
- `src/orchestration/` - LangGraph para QA multimodal

**Stack Técnico:**
```
Python 3.9+ • FastAPI • Uvicorn
Google Generative AI (Gemini 2.5 Flash)
LangChain • LangGraph
Supabase (PostgreSQL)
Pydantic • python-dotenv • httpx
```

---

## 🔧 Configuración

### Variables de Ambiente Requeridas
| Variable | Tipo | Descripción | Ejemplo |
|----------|------|------------|---------|
| `GOOGLE_API_KEY` | string | Clave API de Google | `AIzaSy...` |
| `GEMINI_MODEL` | string | Modelo Gemini | `gemini-2.5-flash` |
| `NEXT_PUBLIC_SUPABASE_NUTRITION_URL` | URL | URL del proyecto | `https://xxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_NUTRITION_ANON_KEY` | string | Clave pública | `eyJhbG...` |
| `PORT` | number | Puerto del servidor | `8000` |

Ver [SETUP.md](docs/SETUP.md) para instrucciones detalladas.

---

## 🔐 Seguridad

- ✅ **Secretos en Ambiente**: API keys y credenciales en `config/.env` (nunca en git)
- ✅ **CORS Configurado**: FastAPI CORS middleware
- ✅ **Supabase RLS**: Row-Level Security (opcional, recomendado para producción)
- ✅ **HTTPS**: Usar reverse proxy (nginx) en producción
- ✅ **Rate Limiting**: Implementar en producción
- ✅ **JWT Tokens**: Estructura lista para implementación

---

## 📦 Dependencias

```
fastapi>=0.104.1          # Web framework
uvicorn>=0.24.0           # ASGI server
google-generativeai>=0.5.0 # Gemini API
langchain>=0.1.0          # LLM orchestration
langgraph>=0.0.20         # Graph workflows
supabase>=2.0.0           # Database client
python-dotenv>=1.0.0      # Env variables
httpx>=0.28.1,<0.29       # HTTP client
pydantic>=2.0.0           # Data validation
```

---

## 💻 Desarrollo

```bash
# Formatear código
black src/ main.py

# Lint
flake8 src/ main.py --max-line-length=100

# Tests
pytest tests/ -v

# Debug mode
uvicorn src.nutrition_api:app --reload --log-level debug
```

---

## 🚢 Deployment

### Docker
```bash
docker build -t nutriapp .
docker run -p 8000:8000 --env-file config/.env nutriapp
```

### Google Cloud Run
```bash
gcloud run deploy nutriapp --source . \
  --platform managed --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY
```

---

## 📊 Performance

| Operación | Tiempo Típico |
|-----------|---------------|
| Análisis de imagen | 2-3 segundos |
| Respuesta del chatbot | 1-2 segundos |
| Query Supabase | 100-300ms |

---

## 📝 Licencia

Privado - Proyecto IA Food 2026

---

**Última actualización:** 2026-01-01 | **Estado:** ✅ Production Ready
