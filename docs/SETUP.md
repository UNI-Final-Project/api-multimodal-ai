# Guía de Configuración

Pasos detallados para configurar el proyecto NutriApp.

## 1. Requisitos Previos

- Python 3.9+
- pip o conda
- Cuenta de Google Cloud (para Gemini API)
- Cuenta de Supabase

## 2. Instalación

### Paso 1: Clonar repositorio
```bash
cd d:\UNI\
git clone <repo>
cd "Proyecto IA food"
```

### Paso 2: Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

## 3. Configurar Variables de Ambiente

Crear archivo `config/.env`:

```env
# Google Gemini API
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Supabase
NEXT_PUBLIC_SUPABASE_NUTRITION_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_NUTRITION_ANON_KEY=your_anon_key_here

# Servidor
PORT=8000
```

### Obtener Credenciales

**Google Gemini API:**
1. Ir a [Google Cloud Console](https://console.cloud.google.com)
2. Crear proyecto
3. Habilitar API de Gemini
4. Crear clave API

**Supabase:**
1. Ir a [Supabase](https://supabase.com)
2. Crear proyecto
3. Copiar URL y clave anónima del settings

## 4. Configurar Supabase

### Crear Tablas

En la consola de Supabase, ejecutar estos SQL:

**Tabla: user_metrics**
```sql
CREATE TABLE user_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT UNIQUE NOT NULL,
  weight FLOAT,
  height FLOAT,
  calorie_goal FLOAT,
  protein_goal FLOAT,
  carbs_goal FLOAT,
  fat_goal FLOAT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Tabla: daily_nutrition**
```sql
CREATE TABLE daily_nutrition (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  date DATE NOT NULL,
  calories FLOAT DEFAULT 0,
  protein FLOAT DEFAULT 0,
  carbs FLOAT DEFAULT 0,
  fat FLOAT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, date)
);
```

**Tabla: conversation_history**
```sql
CREATE TABLE conversation_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  message_type TEXT NOT NULL,
  content TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 5. Ejecutar la Aplicación

```bash
python main.py
```

Acceder a:
- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`

## 6. Pruebas Rápidas

### Análisis de Imagen
```bash
curl -X POST "http://localhost:8000/analyze-meal" \
  -F "file=@test_image.jpg"
```

### Obtener Perfil
```bash
curl "http://localhost:8000/user/test-user-123/profile"
```

### Chat
```bash
curl -X POST "http://localhost:8000/chat/test-user-123" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué debo comer?",
    "user_name": "Juan"
  }'
```

## 7. Variables de Ambiente Detalladas

| Variable | Descripción | Ejemplo |
|----------|------------|---------|
| `GOOGLE_API_KEY` | Clave API de Google Gemini | `AIzaS...` |
| `GEMINI_MODEL` | Modelo a usar | `gemini-2.5-flash` |
| `NEXT_PUBLIC_SUPABASE_NUTRITION_URL` | URL del proyecto Supabase | `https://xxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_NUTRITION_ANON_KEY` | Clave pública de Supabase | `eyJhbG...` |
| `PORT` | Puerto del servidor | `8000` |

## 8. Troubleshooting

### "ModuleNotFoundError: No module named 'google'"
```bash
pip install google-generativeai
```

### "ModuleNotFoundError: No module named 'supabase'"
```bash
pip install "supabase>=2.0.0"
```

### "GOOGLE_API_KEY not loaded"
- Verificar que `config/.env` existe
- Verificar que la variable está correctamente escrita
- Reiniciar la aplicación

### "Failed to connect to Supabase"
- Verificar credenciales en `config/.env`
- Verificar que las tablas están creadas
- Verificar conexión a internet

## 9. Estructura del Proyecto

```
.
├── main.py                    # Punto de entrada
├── requirements.txt           # Dependencias
├── config/
│   └── .env                  # Variables de ambiente
├── src/
│   ├── nutrition_api.py      # API endpoints
│   ├── nutrition_chatbot.py  # Lógica del chatbot
│   ├── supabase_client.py    # Cliente de Supabase
│   └── orchestration/
│       ├── graph.py          # LangGraph workflow
│       └── state.py          # Estados del grafo
└── docs/
    ├── API_REFERENCE.md      # Referencia de API
    └── SETUP.md             # Este archivo
```

## 10. Ambiente de Desarrollo

### Instalar con dependencias de desarrollo
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8
```

### Formatear código
```bash
black src/ main.py
```

### Lint
```bash
flake8 src/ main.py --max-line-length=100
```

### Tests
```bash
pytest tests/
```

## 11. Deployment

### Docker
```bash
docker build -t nutriapp .
docker run -p 8000:8000 --env-file config/.env nutriapp
```

### Google Cloud Run
```bash
gcloud run deploy nutriapp \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY
```

## 12. Performance

- **Gemini análisis de imagen**: ~2-3 segundos
- **Respuesta del chatbot**: ~1-2 segundos (con contexto precargado)
- **Queries de Supabase**: ~100-300ms

## 13. Seguridad

- ✅ API keys en `config/.env` (nunca commitar)
- ✅ Supabase con Row Level Security (opcional, implementar en producción)
- ✅ CORS configurado en FastAPI
- ✅ Rate limiting (implementar en producción)
- ✅ HTTPS en producción (usar nginx/reverse proxy)

## 14. Monitoreo

Ver logs en tiempo real:
```bash
python main.py 2>&1 | tee logs.txt
```

Con Uvicorn verbose:
```bash
uvicorn src.nutrition_api:app --reload --log-level debug
```

---

**Documentación actualizada:** 2026-01-01
