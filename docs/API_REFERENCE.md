# API Reference

Documentación detallada de todos los endpoints.

## 🖼️ Análisis de Imagen

### POST /analyze-meal

Analiza una imagen de comida y extrae información nutricional.

**Request:**
```
POST /analyze-meal
Content-Type: multipart/form-data

Body:
  file: <image.jpg>
```

**Response (200):**
```json
{
  "ok": true,
  "nutrients": {
    "calories": 450.0,
    "protein_g": 25.0,
    "carbs_g": 60.0,
    "fat_g": 15.0,
    "fiber_g": 5.0,
    "sugar_g": 10.0,
    "sodium_mg": 800.0
  },
  "metadata": {
    "method": "direct_gemini_sdk",
    "model": "gemini-2.5-flash",
    "processing_time_ms": 2500
  }
}
```

**Error (400):**
```json
{
  "ok": false,
  "nutrients": null,
  "metadata": {"error": "No image provided"}
}
```

---

## 👤 Perfil del Usuario

### GET /user/{user_id}/profile

Obtiene el perfil completo del usuario.

**Request:**
```
GET /user/afaa08a0-cff4-40eb-9686-c83ff3d256f8/profile
```

**Response (200):**
```json
{
  "ok": true,
  "profile": {
    "metrics": {
      "id": "a396be77-229f-4bf4-872a-05e20336b545",
      "user_id": "afaa08a0-cff4-40eb-9686-c83ff3d256f8",
      "weight": 65.0,
      "height": 170.0,
      "calorie_goal": 2080.0,
      "protein_goal": 104.0,
      "carbs_goal": 234.0,
      "fat_goal": 69.0,
      "created_at": "2026-01-01 00:12:29.777159+00",
      "updated_at": "2026-01-01 16:16:00.837+00"
    },
    "daily_nutrition": [
      {
        "id": "19d5aec2-aa82-4a4b-8ef0-2267b70e2f64",
        "user_id": "afaa08a0-cff4-40eb-9686-c83ff3d256f8",
        "date": "2026-01-01",
        "calories": 1080.0,
        "protein": 83.0,
        "carbs": 80.0,
        "fat": 48.0,
        "created_at": "2026-01-01 00:15:23.164957+00",
        "updated_at": "2026-01-01 16:16:47.226+00"
      }
    ]
  },
  "metadata": {
    "timestamp": 1704139800.0,
    "user_id": "afaa08a0-cff4-40eb-9686-c83ff3d256f8"
  }
}
```

### GET /user/{user_id}/metrics

Solo obtiene las métricas personales.

**Request:**
```
GET /user/{user_id}/metrics
```

**Response (200):**
```json
{
  "ok": true,
  "metrics": {
    "weight": 65.0,
    "height": 170.0,
    "calorie_goal": 2080.0,
    "protein_goal": 104.0,
    "carbs_goal": 234.0,
    "fat_goal": 69.0
  },
  "metadata": {"timestamp": 1704139800.0}
}
```

### GET /user/{user_id}/nutrition/history

Obtiene historial de nutrición.

**Request:**
```
GET /user/{user_id}/nutrition/history?limit=30
```

**Response (200):**
```json
{
  "ok": true,
  "daily_nutrition": [
    {
      "date": "2026-01-01",
      "calories": 1080.0,
      "protein": 83.0,
      "carbs": 80.0,
      "fat": 48.0
    }
  ],
  "metadata": {
    "count": 1,
    "timestamp": 1704139800.0
  }
}
```

### GET /user/{user_id}/nutrition/today

Obtiene nutrición de un día específico.

**Request:**
```
GET /user/{user_id}/nutrition/today?date=2026-01-01
```

**Response (200):**
```json
{
  "ok": true,
  "daily_nutrition": {
    "date": "2026-01-01",
    "calories": 1080.0,
    "protein": 83.0,
    "carbs": 80.0,
    "fat": 48.0
  },
  "metadata": {"timestamp": 1704139800.0}
}
```

---

## 🤖 Chatbot

### POST /chat/{user_id}

Envía un mensaje al chatbot y obtiene recomendaciones personalizadas.

**Request:**
```
POST /chat/afaa08a0-cff4-40eb-9686-c83ff3d256f8
Content-Type: application/json

{
  "message": "Acabo de comer 450 calorías, ¿qué me recomiendas?",
  "user_name": "Juan"
}
```

**Response (200):**
```json
{
  "ok": true,
  "response": "Hola Juan! Basándome en tu consumo de hoy (1080 kcal), te recomiendo:\n\n1. Almuerzo/Cena:\n   - 150g de pollo a la parrilla (250 kcal)...",
  "metadata": {
    "timestamp": "2026-01-01T16:30:00.000Z",
    "user_name": "Juan",
    "model": "gemini-2.5-flash",
    "context_available": true,
    "memory_messages_count": 5
  }
}
```

### GET /chat/{user_id}/history

Obtiene el historial de conversación.

**Request:**
```
GET /chat/{user_id}/history?limit=50
```

**Response (200):**
```json
{
  "ok": true,
  "history": [
    {
      "id": "msg-123",
      "user_id": "afaa08a0-cff4-40eb-9686-c83ff3d256f8",
      "message_type": "user",
      "content": "¿Qué puedo comer?",
      "timestamp": "2026-01-01T16:30:00.000Z",
      "created_at": "2026-01-01T16:30:00.000Z"
    },
    {
      "id": "msg-124",
      "user_id": "afaa08a0-cff4-40eb-9686-c83ff3d256f8",
      "message_type": "assistant",
      "content": "Te recomiendo...",
      "timestamp": "2026-01-01T16:30:05.000Z",
      "created_at": "2026-01-01T16:30:05.000Z"
    }
  ],
  "metadata": {
    "timestamp": 1704139800.0,
    "message_count": 2
  }
}
```

### DELETE /chat/{user_id}/history

Limpia el historial de conversación.

**Request:**
```
DELETE /chat/{user_id}/history
```

**Response (200):**
```json
{
  "ok": true,
  "message": "Historial de conversación eliminado",
  "metadata": {
    "timestamp": 1704139800.0,
    "user_id": "afaa08a0-cff4-40eb-9686-c83ff3d256f8"
  }
}
```

---

## 📊 QA Multimodal (Legacy)

### POST /qa

Responde preguntas sobre archivos multimedia (imagen, PDF, audio, etc.).

**Request:**
```
POST /qa
Content-Type: multipart/form-data

question: "¿Qué contiene esta imagen?"
files: [document.pdf, image.jpg]
use_files_api: false
```

**Response (200):**
```json
{
  "ok": true,
  "answer": "Markdown respuesta aquí...",
  "metadata": {
    "model": "gemini-2.5-flash",
    "processing_time_ms": 3500,
    "language": "es"
  }
}
```

---

## 🏥 Health Check

### GET /health

Verifica que la API esté disponible.

**Response (200):**
```json
{
  "status": "ok"
}
```

### GET /env-check

Verifica que las variables de ambiente estén configuradas.

**Response (200):**
```json
{
  "google_api_key_loaded": true,
  "model": "gemini-2.5-flash"
}
```

---

## ⚠️ Error Codes

| Code | Descripción |
|------|------------|
| 200 | Éxito |
| 400 | Parámetros inválidos |
| 422 | Usuario no encontrado |
| 500 | Error del servidor |

---

## 📝 Headers Recomendados

```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token> (si se implementa)
```
