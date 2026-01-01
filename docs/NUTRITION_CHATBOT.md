# 🤖 Nutrition Chatbot API

## Descripción
Un chatbot especializado en recomendaciones nutricionales que:
- ✅ Mantiene **historial** de todas las conversaciones
- ✅ Recuerda el **nombre del usuario**
- ✅ Conoce los **objetivos nutricionales** del usuario
- ✅ Recomienda **comidas personalizadas**
- ✅ Sugiere **alimentos específicos** para cumplir metas
- ✅ Proporciona **recomendaciones contextuales** basadas en lo consumido hoy

## Endpoints

### 1. Chatbot Principal

**POST** `/chat/{user_id}`

Envía un mensaje al chatbot y obtiene una respuesta personalizada con recomendaciones.

#### Parámetros

- `user_id` (path): UUID del usuario

#### Body (JSON)
```json
{
  "message": "¿Qué comida puedo hacer para llegar a los 2080 calorías?",
  "user_name": "Juan"
}
```

#### Respuesta (200 OK)
```json
{
  "ok": true,
  "response": "Hola Juan! Basándome en tu consumo de hoy (1080 kcal), te recomiendo:\n\n1. **Almuerzo/Cena:**\n   - 150g de pollo a la parrilla (200 kcal, 45g proteína)\n   - 200g de arroz blanco (260 kcal, 5g proteína)...",
  "metadata": {
    "timestamp": "2026-01-01T16:30:00.000Z",
    "user_name": "Juan",
    "model": "gemini-2.5-flash",
    "context_available": true,
    "memory_messages_count": 5
  }
}
```

#### Ejemplo con cURL
```bash
curl -X POST "http://localhost:8000/chat/afaa08a0-cff4-40eb-9686-c83ff3d256f8" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué snacks puedo comer que sean altos en proteína?",
    "user_name": "Juan"
  }'
```

---

### 2. Ver Historial de Conversación

**GET** `/chat/{user_id}/history?limit=50`

Obtiene el historial completo de conversaciones del usuario.

#### Parámetros

- `user_id` (path): UUID del usuario
- `limit` (query): Número máximo de mensajes (default: 50)

#### Respuesta (200 OK)
```json
{
  "ok": true,
  "history": [
    {
      "id": "msg-123",
      "user_id": "afaa08a0-cff4-40eb-9686-c83ff3d256f8",
      "message_type": "user",
      "content": "¿Qué comida puedo hacer para llegar a los 2080 calorías?",
      "timestamp": "2026-01-01T16:30:00.000Z",
      "created_at": "2026-01-01T16:30:00.000Z"
    },
    {
      "id": "msg-124",
      "user_id": "afaa08a0-cff4-40eb-9686-c83ff3d256f8",
      "message_type": "assistant",
      "content": "Hola! Basándome en tu consumo de hoy...",
      "timestamp": "2026-01-01T16:30:05.000Z",
      "created_at": "2026-01-01T16:30:05.000Z"
    }
  ],
  "metadata": {
    "timestamp": 1704139800.0,
    "user_id": "afaa08a0-cff4-40eb-9686-c83ff3d256f8",
    "message_count": 2
  }
}
```

#### Ejemplo con cURL
```bash
curl "http://localhost:8000/chat/afaa08a0-cff4-40eb-9686-c83ff3d256f8/history?limit=20"
```

---

### 3. Limpiar Historial

**DELETE** `/chat/{user_id}/history`

Elimina completamente el historial de conversación del usuario.

#### Respuesta (200 OK)
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

## Contexto Automático del Chatbot

El chatbot automáticamente:

1. **Obtiene métricas del usuario** (peso, altura, objetivos)
2. **Calcula lo que falta consumir hoy** basado en `daily_nutrition`
3. **Recupera últimos 5 mensajes** del historial para mantener contexto
4. **Personaliza recomendaciones** según objetivos y consumo actual

### Ejemplo de Contexto
```
=== CONTEXTO DEL USUARIO ===
Nombre: Juan

MÉTRICAS PERSONALES:
- Peso: 65 kg
- Altura: 170 cm
- IMC: 22.5

OBJETIVOS DIARIOS:
- Calorías: 2080 kcal
- Proteína: 104g
- Carbohidratos: 234g
- Grasas: 69g

CONSUMO DE HOY (2026-01-01):
- Calorías consumidas: 1080 kcal (Falta: 1000 kcal)
- Proteína: 83g (Falta: 21g)
- Carbohidratos: 80g (Falta: 154g)
- Grasas: 48g (Falta: 21g)
```

---

## Flujo Típico de Uso

### Cliente Frontend

```javascript
// 1. Enviar mensaje al chatbot
const response = await fetch('https://api.example.com/chat/user-uuid', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "¿Qué debería comer ahora?",
    user_name: "Juan"
  })
});

const data = await response.json();
console.log(data.response); // Respuesta personalizada

// 2. Ver historial de conversación
const historyResponse = await fetch('https://api.example.com/chat/user-uuid/history');
const history = await historyResponse.json();
console.log(history.history); // Array de mensajes

// 3. Limpiar historial (si es necesario)
await fetch('https://api.example.com/chat/user-uuid/history', {
  method: 'DELETE'
});
```

---

## Casos de Uso

### 1. Recomendación de Comida Basada en Calorías Faltantes
```
Usuario: "Me faltan 1000 calorías para hoy, ¿qué debo comer?"
Chatbot: Recommends specific meals that add up to ~1000 kcal
```

### 2. Alimentos Alto en Proteína
```
Usuario: "Necesito aumentar proteína, ¿qué puedo comer?"
Chatbot: Suggests high-protein foods that fit remaining macros
```

### 3. Alternativas Saludables
```
Usuario: "Me encanta el helado, ¿hay algo saludable?"
Chatbot: Recommends protein-packed alternatives with macro calculations
```

### 4. Snacks Rápidos
```
Usuario: "¿Qué snack puedo llevar al trabajo?"
Chatbot: Suggests portable, healthy options based on current needs
```

---

## Notas Técnicas

- **Memory**: Usa Supabase `conversation_history` table
- **Context**: Obtenido dinámicamente de `user_metrics` y `daily_nutrition`
- **LLM**: Google Gemini con temperature=0.7 para respuestas naturales pero consistentes
- **Language**: Respuestas siempre en español
- **Rate Limit**: No hay límite configurado (configurable según necesidad)

---

## Estructura de Base de Datos Requerida

Se requieren las siguientes tablas en Supabase:

```sql
-- Ya existentes
- user_metrics (id, user_id, weight, height, calorie_goal, protein_goal, carbs_goal, fat_goal, created_at, updated_at)
- daily_nutrition (id, user_id, date, calories, protein, carbs, fat, created_at, updated_at)

-- Nueva para el chatbot
- conversation_history (id, user_id, message_type, content, timestamp, created_at)
```

---

## Error Handling

### 422 - User Not Found
```json
{
  "ok": false,
  "response": "Error: User with id xxx not found"
}
```

### 400 - Empty Message
```json
{
  "ok": false,
  "response": "El mensaje no puede estar vacío"
}
```

### 500 - Server Error
```json
{
  "ok": false,
  "response": "Error en el chatbot: [error details]"
}
```
