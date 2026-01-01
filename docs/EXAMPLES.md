# Quick Examples

Ejemplos rápidos de cómo usar cada endpoint.

## 1. Análisis de Imagen

### Usando curl
```bash
curl -X POST "http://localhost:8000/analyze-meal" \
  -F "file=@pizza.jpg"
```

### Respuesta
```json
{
  "ok": true,
  "nutrients": {
    "calories": 285,
    "protein_g": 12,
    "carbs_g": 36,
    "fat_g": 9,
    "fiber_g": 2,
    "sugar_g": 3,
    "sodium_mg": 500
  },
  "metadata": {
    "method": "direct_gemini_sdk",
    "model": "gemini-2.5-flash",
    "processing_time_ms": 2340
  }
}
```

### Usando Python
```python
import requests

with open('pizza.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/analyze-meal',
        files=files
    )
    print(response.json())
```

---

## 2. Obtener Perfil del Usuario

### Usando curl
```bash
curl "http://localhost:8000/user/user-123/profile"
```

### Respuesta
```json
{
  "ok": true,
  "profile": {
    "metrics": {
      "weight": 75.5,
      "height": 180,
      "calorie_goal": 2300,
      "protein_goal": 115,
      "carbs_goal": 260,
      "fat_goal": 77
    },
    "daily_nutrition": [
      {
        "date": "2026-01-01",
        "calories": 1850,
        "protein": 92,
        "carbs": 210,
        "fat": 60
      }
    ]
  },
  "metadata": {
    "timestamp": 1704139800.0,
    "user_id": "user-123"
  }
}
```

### Usando Python
```python
import requests

response = requests.get('http://localhost:8000/user/user-123/profile')
profile = response.json()
print(f"Weight: {profile['profile']['metrics']['weight']}kg")
```

---

## 3. Chat con el Chatbot

### Usando curl
```bash
curl -X POST "http://localhost:8000/chat/user-123" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Acabo de comer 400 calorías, ¿qué me recomiendas?",
    "user_name": "Juan"
  }'
```

### Respuesta
```json
{
  "ok": true,
  "response": "¡Hola Juan! Veo que has consumido 400 kcal hasta ahora, lo que te deja 1900 kcal para el resto del día.\n\nTe recomiendo:\n\n1. **Para el almuerzo:**\n   - 150g de pollo a la parrilla (250 kcal)\n   - 200g de arroz integral (250 kcal)\n   - Ensalada verde (50 kcal)\n\nEsto te daría 550 kcal más, dejándote con 1350 kcal para cena.\n\n¿Hay algo específico que tengas ganas de comer?",
  "metadata": {
    "timestamp": "2026-01-01T16:30:00.000Z",
    "user_name": "Juan",
    "model": "gemini-2.5-flash",
    "context_available": true,
    "memory_messages_count": 3
  }
}
```

### Usando Python
```python
import requests

response = requests.post(
    'http://localhost:8000/chat/user-123',
    json={
        'message': '¿Qué debo comer?',
        'user_name': 'Juan'
    }
)
print(response.json()['response'])
```

---

## 4. Ver Historial de Chat

### Usando curl
```bash
curl "http://localhost:8000/chat/user-123/history?limit=10"
```

### Respuesta
```json
{
  "ok": true,
  "history": [
    {
      "id": "msg-1",
      "user_id": "user-123",
      "message_type": "user",
      "content": "¿Qué debo comer?",
      "timestamp": "2026-01-01T16:30:00.000Z",
      "created_at": "2026-01-01T16:30:00.000Z"
    },
    {
      "id": "msg-2",
      "user_id": "user-123",
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

### Usando Python
```python
import requests

response = requests.get(
    'http://localhost:8000/chat/user-123/history',
    params={'limit': 10}
)
history = response.json()['history']
for msg in history:
    print(f"{msg['message_type']}: {msg['content'][:50]}...")
```

---

## 5. Limpiar Historial de Chat

### Usando curl
```bash
curl -X DELETE "http://localhost:8000/chat/user-123/history"
```

### Respuesta
```json
{
  "ok": true,
  "message": "Historial de conversación eliminado",
  "metadata": {
    "timestamp": 1704139800.0,
    "user_id": "user-123"
  }
}
```

---

## 6. Obtener Solo Métricas

### Usando curl
```bash
curl "http://localhost:8000/user/user-123/metrics"
```

### Respuesta
```json
{
  "ok": true,
  "metrics": {
    "weight": 75.5,
    "height": 180,
    "calorie_goal": 2300,
    "protein_goal": 115,
    "carbs_goal": 260,
    "fat_goal": 77
  },
  "metadata": {
    "timestamp": 1704139800.0
  }
}
```

---

## 7. Obtener Historial de Nutrición

### Usando curl
```bash
curl "http://localhost:8000/user/user-123/nutrition/history?limit=7"
```

### Respuesta
```json
{
  "ok": true,
  "daily_nutrition": [
    {
      "date": "2026-01-01",
      "calories": 1850,
      "protein": 92,
      "carbs": 210,
      "fat": 60
    },
    {
      "date": "2025-12-31",
      "calories": 2100,
      "protein": 105,
      "carbs": 240,
      "fat": 70
    }
  ],
  "metadata": {
    "count": 2,
    "timestamp": 1704139800.0
  }
}
```

---

## 8. Obtener Nutrición de un Día

### Usando curl
```bash
curl "http://localhost:8000/user/user-123/nutrition/today?date=2026-01-01"
```

### Respuesta
```json
{
  "ok": true,
  "daily_nutrition": {
    "date": "2026-01-01",
    "calories": 1850,
    "protein": 92,
    "carbs": 210,
    "fat": 60
  },
  "metadata": {
    "timestamp": 1704139800.0
  }
}
```

---

## 9. QA Multimodal

### Usando curl
```bash
curl -X POST "http://localhost:8000/qa" \
  -F "question=¿Qué puedo hacer con esto?" \
  -F "files=@image.jpg" \
  -F "files=@document.pdf"
```

### Respuesta
```json
{
  "ok": true,
  "answer": "Basándome en los documentos y la imagen que compartiste:\n\n## Análisis de la imagen\nLa imagen muestra...",
  "metadata": {
    "model": "gemini-2.5-flash",
    "processing_time_ms": 3500,
    "language": "es"
  }
}
```

---

## 10. Health Check

### Usando curl
```bash
curl "http://localhost:8000/health"
```

### Respuesta
```json
{
  "status": "ok"
}
```

---

## Scripts de Ejemplo (Python)

### Setup inicial
```python
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "user-123"

def health_check():
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

def analyze_meal(image_path):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{BASE_URL}/analyze-meal",
            files=files
        )
    return response.json()

def get_profile(user_id):
    response = requests.get(f"{BASE_URL}/user/{user_id}/profile")
    return response.json()

def chat(user_id, message, user_name="User"):
    response = requests.post(
        f"{BASE_URL}/chat/{user_id}",
        json={"message": message, "user_name": user_name}
    )
    return response.json()

# Uso
if __name__ == "__main__":
    print("Health:", health_check())
    print("Profile:", get_profile(USER_ID))
    print("Chat:", chat(USER_ID, "¿Qué debo comer?", "Juan"))
```

---

## Usando Postman

### Importar colección

Puedes crear una colección en Postman con estos endpoints:

1. **POST** `{{BASE_URL}}/analyze-meal`
   - Tab: Body → form-data
   - Key: file (File)

2. **GET** `{{BASE_URL}}/user/{{USER_ID}}/profile`
   - Variables: BASE_URL, USER_ID

3. **POST** `{{BASE_URL}}/chat/{{USER_ID}}`
   - Body (JSON): `{"message": "...", "user_name": "..."}`

4. **GET** `{{BASE_URL}}/chat/{{USER_ID}}/history`
   - Params: limit

---

**Documentación actualizada:** 2026-01-01
