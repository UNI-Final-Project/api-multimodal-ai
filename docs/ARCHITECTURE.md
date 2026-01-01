# Arquitectura Técnica

Descripción técnica de la solución NutriApp.

## 1. Stack Tecnológico

```
┌─────────────────────────────────────────────┐
│           Frontend (Next.js)                │
└──────────────────┬──────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────┐
│    FastAPI (Python)                         │
│  src/nutrition_api.py                       │
├─────────────────────────────────────────────┤
│  • POST /analyze-meal                       │
│  • POST /chat/{user_id}                     │
│  • GET /user/{user_id}/profile              │
│  • POST /qa                                 │
└──────┬──────────────────────────┬───────────┘
       │                          │
       │ Análisis de imagen       │ Conversaciones
       │                          │
┌──────▼──────────┐      ┌────────▼──────────┐
│ Gemini API      │      │  Supabase         │
│ (gemini-2.5-    │      │  • user_metrics   │
│  flash)         │      │  • daily_nutrition│
│                 │      │  • conversation_  │
│ LangChain       │      │    history        │
│ JsonOutputParser│      │                   │
└─────────────────┘      └───────────────────┘

LangGraph Orchestration (Graph + State)
- 6-node workflow para QA multimodal
- Language detection (ES/EN)
- Dual prompts en español/inglés
```

## 2. Flujo de Análisis de Imagen

```
REQUEST: POST /analyze-meal
    ↓
Read Image File
    ↓
Convert to Base64
    ↓
Send to Gemini API
    ├─ Model: gemini-2.5-flash
    ├─ Temperature: 0.0 (determinístico)
    └─ Prompt: JSON structure
    ↓
Parse JSON Response
    ├─ calories
    ├─ protein_g
    ├─ carbs_g
    ├─ fat_g
    ├─ fiber_g
    ├─ sugar_g
    └─ sodium_mg
    ↓
Return MealNutrients
    ↓
RESPONSE: {"ok": true, "nutrients": {...}}
```

## 3. Flujo del Chatbot

```
REQUEST: POST /chat/{user_id}
    ↓
Load User Context
    ├─ Get user_metrics from Supabase
    └─ Get today's daily_nutrition
    ↓
Retrieve Conversation Memory
    ├─ Get last N messages from conversation_history
    └─ Build context for prompt
    ↓
Build System Prompt
    ├─ Include user metrics
    ├─ Include daily nutrition progress
    ├─ Include goals
    └─ Include personality
    ↓
Call Gemini API
    ├─ Model: gemini-2.5-flash
    ├─ Temperature: 0.7 (natural responses)
    └─ Include conversation history
    ↓
Parse Response
    ↓
Save to conversation_history
    ├─ Save user message
    └─ Save assistant response
    ↓
RESPONSE: {"ok": true, "response": "..."}
```

## 4. Flujo QA Multimodal (LangGraph)

```
Graph Structure:
[Input] → [validate_input] → [detect_language]
                                   ↓
                    ┌──────────────┴──────────────┐
                    ↓ (ES)                (EN) ↓
              [process_es]              [process_en]
                    ↓                          ↓
              ┌─────────────────────────────────┘
              ↓
          [aggregate]
              ↓
          [Output]

Nodes:
1. validate_input: Verifica inputs
2. detect_language: Detecta idioma (ES/EN)
3. process_es: Procesa en español
4. process_en: Procesa en inglés
5. aggregate: Combina resultados
6. Output: Formatea respuesta
```

## 5. Modelos de Datos

### User Metrics
```
user_metrics {
  id: UUID
  user_id: TEXT (unique)
  weight: FLOAT (kg)
  height: FLOAT (cm)
  calorie_goal: FLOAT (kcal/día)
  protein_goal: FLOAT (g/día)
  carbs_goal: FLOAT (g/día)
  fat_goal: FLOAT (g/día)
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}
```

### Daily Nutrition
```
daily_nutrition {
  id: UUID
  user_id: TEXT
  date: DATE
  calories: FLOAT
  protein: FLOAT
  carbs: FLOAT
  fat: FLOAT
  created_at: TIMESTAMP
  updated_at: TIMESTAMP
}
```

### Conversation History
```
conversation_history {
  id: UUID
  user_id: TEXT
  message_type: TEXT (user|assistant)
  content: TEXT
  timestamp: TIMESTAMP
  created_at: TIMESTAMP
}
```

## 6. Pydantic Models (Python)

### MealNutrients
```python
class MealNutrients(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sugar_g: float
    sodium_mg: float
```

### ChatRequest
```python
class ChatRequest(BaseModel):
    message: str
    user_name: Optional[str] = None
```

### ChatResponse
```python
class ChatResponse(BaseModel):
    ok: bool
    response: str
    metadata: dict
```

### UserMetrics
```python
class UserMetrics(BaseModel):
    weight: float
    height: float
    calorie_goal: float
    protein_goal: float
    carbs_goal: float
    fat_goal: float
```

## 7. Flujo de Autenticación (Futuro)

```
Frontend
    ↓ POST /auth/login
API
    ├─ Validar credenciales
    ├─ Generar JWT token
    └─ Guardar sesión en Supabase
    ↓
Return {token, user_id}
    ↓
Subsequent Requests
    ├─ Include Authorization: Bearer {token}
    ├─ Verify JWT
    └─ Proceed con user context
```

## 8. Componentes del Módulo Chatbot

### NutritionChatbot Class
```
NutritionChatbot
├── __init__(user_id, user_name)
├── _build_context()          # Obtiene datos del usuario
├── _get_conversation_memory()# Carga historial
├── _format_context_for_prompt() # Construye prompt
├── chat(message)             # Procesa mensaje
└── Memory:
    ├─ User metrics
    ├─ Today's nutrition
    └─ Conversation history
```

## 9. Componentes del Módulo API

### nutrition_api.py
```
FastAPI App
├── Endpoints:
│   ├── GET /health
│   ├── GET /env-check
│   ├── POST /analyze-meal
│   ├── GET /user/{user_id}/profile
│   ├── GET /user/{user_id}/metrics
│   ├── GET /user/{user_id}/nutrition/history
│   ├── GET /user/{user_id}/nutrition/today
│   ├── POST /chat/{user_id}
│   ├── GET /chat/{user_id}/history
│   ├── DELETE /chat/{user_id}/history
│   └── POST /qa
├── Middleware:
│   └── CORS configuration
└── Global variables:
    └── app, supabase_client, chatbot_instances
```

## 10. Flujo de Carga de Imágenes

```
Frontend uploads image
    ↓
multipart/form-data
    ↓
Parse en FastAPI
    ↓
Read bytes
    ↓
Convert to Base64
    ↓
Create Content Part for Gemini
    ├─ Type: image/jpeg | image/png | etc.
    └─ Data: base64 encoded
    ↓
Send to Gemini API
    ↓
Receive JSON response
    ↓
Parse and validate
    ↓
Return MealNutrients
```

## 11. Performance & Escalabilidad

### Optimizaciones Actuales
- Temperature=0.0 para consistency en meal analysis
- Temperature=0.7 para naturalidad en chatbot
- Caching de user_metrics en memoria (opcional)
- Async operations para Supabase queries

### Mejoras Futuras
- Redis cache para conversation history
- Database indexing on (user_id, date)
- Load balancing con multiple workers
- Streaming responses para respuestas largas
- Rate limiting por usuario

## 12. Manejo de Errores

```
Try-Catch Pattern:
    ↓
Check: file exists?
    ├─ NO → Return 400 "No image provided"
    ↓
Check: valid image format?
    ├─ NO → Return 400 "Invalid image format"
    ↓
Check: user exists in Supabase?
    ├─ NO → Return 422 "User not found"
    ↓
Check: Gemini API response ok?
    ├─ NO → Return 500 "Gemini API error"
    ↓
Success → Return 200 with data
```

## 13. Prompts del Sistema

### Prompt para Meal Analysis
```
Analiza la imagen de comida.
Retorna SOLO JSON con estructura:
{
  "calories": float,
  "protein_g": float,
  "carbs_g": float,
  "fat_g": float,
  "fiber_g": float,
  "sugar_g": float,
  "sodium_mg": float
}

Sé preciso. Retorna SOLO JSON válido.
```

### Prompt para Chatbot (Base)
```
Eres un asesor nutricional personalizado.
Nombre del usuario: {user_name}

📊 Métricas del usuario:
- Peso: {weight}kg
- Altura: {height}cm
- Meta calórica: {calorie_goal} kcal
- Meta proteína: {protein_goal}g
- Meta carbohidratos: {carbs_goal}g
- Meta grasas: {fat_goal}g

📈 Consumo de hoy:
- Calorías: {today_calories}/{calorie_goal}
- Proteína: {today_protein}/{protein_goal}g
- Carbohidratos: {today_carbs}/{carbs_goal}g
- Grasas: {today_fat}/{fat_goal}g

Responde siempre en español o inglés según el usuario.
Sé empático, motivador, y específico.
```

## 14. Integración con LangChain

```
LangChain Components:
├── ChatGoogleGenerativeAI
│   └── Model: gemini-2.5-flash
├── JsonOutputParser
│   └── Para meal analysis
├── Prompts
│   ├── System prompts (ES/EN)
│   └── Dynamic user context
└── Memory Management
    ├─ Supabase-backed history
    └─ Conversation context
```

## 15. Diagrama de Bases de Datos

```
Supabase Project
├── user_metrics table
│   ├─ Indexed: user_id
│   └─ Stores: personal and nutritional goals
├── daily_nutrition table
│   ├─ Indexed: (user_id, date)
│   └─ Stores: daily nutrient consumption
└── conversation_history table
    ├─ Indexed: user_id
    └─ Stores: chat messages and responses
```

---

**Última actualización:** 2026-01-01
