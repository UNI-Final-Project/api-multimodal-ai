# 🍽️ Integración Frontend - NutriApp

Guía completa para integrar los endpoints del backend en tu aplicación frontend.

---

## 🔗 URLs Base

```javascript
const API_BASE_URL = "https://658096ec9c01.ngrok-free.app"; // Producción
// const API_BASE_URL = "http://localhost:8000"; // Desarrollo
```

---

## 📸 1. Analizar Imagen de Comida

### Endpoint
```
POST /analyze-meal
```

### Frontend Code
```javascript
async function analyzeMealImage(imageFile) {
  const formData = new FormData();
  formData.append("file", imageFile);
  
  try {
    const response = await fetch(`${API_BASE_URL}/analyze-meal`, {
      method: "POST",
      body: formData,
    });
    
    const data = await response.json();
    
    if (data.ok) {
      return {
        calories: data.nutrients.calories,
        protein_g: data.nutrients.protein_g,
        carbs_g: data.nutrients.carbs_g,
        fat_g: data.nutrients.fat_g,
        fiber_g: data.nutrients.fiber_g,
        sugar_g: data.nutrients.sugar_g,
        sodium_mg: data.nutrients.sodium_mg,
      };
    } else {
      console.error("Error:", data);
      return null;
    }
  } catch (error) {
    console.error("Error analizando comida:", error);
    return null;
  }
}

// Uso
const input = document.getElementById("imageInput");
input.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  const nutrients = await analyzeMealImage(file);
  console.log("Nutrientes:", nutrients);
  // Aquí guarda en Supabase
});
```

---

## 💾 2. Guardar en Supabase (Tu Código)

```javascript
// Ya lo tienes, solo asegúrate de usar los valores de analyzeMealImage
async function saveMealToSupabase(userId, nutrients) {
  const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  
  const { data, error } = await supabase
    .from('daily_nutrition')
    .insert({
      user_id: userId,
      date: today,
      calories: Math.round(nutrients.calories),
      protein: Math.round(nutrients.protein_g),
      carbs: Math.round(nutrients.carbs_g),
      fat: Math.round(nutrients.fat_g),
    });
  
  if (error) console.error("Error guardando:", error);
  return data;
}
```

---

## 👤 3. Obtener Perfil del Usuario

### Endpoint
```
GET /user/{user_id}/profile
```

### Frontend Code
```javascript
async function getUserProfile(userId) {
  try {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/profile`);
    const data = await response.json();
    
    if (data.ok) {
      const profile = data.profile;
      
      // Métricas
      const metrics = profile.metrics;
      console.log({
        name: "Usuario",
        weight: metrics.weight,
        height: metrics.height,
        calorie_goal: metrics.calorie_goal,
        protein_goal: metrics.protein_goal,
        carbs_goal: metrics.carbs_goal,
        fat_goal: metrics.fat_goal,
      });
      
      // Consumo de hoy
      const today = new Date().toISOString().split('T')[0];
      const todayNutrition = profile.daily_nutrition.find(
        d => d.date === today
      );
      
      return profile;
    }
  } catch (error) {
    console.error("Error obteniendo perfil:", error);
  }
}

// Uso
const userId = "afaa08a0-cff4-40eb-9686-c83ff3d256f8"; // De tu auth
const profile = await getUserProfile(userId);
```

### Mostrar en UI
```javascript
function displayUserProfile(profile, userName) {
  const metrics = profile.metrics;
  const today = new Date().toISOString().split('T')[0];
  const todayNutrition = profile.daily_nutrition.find(d => d.date === today);
  
  // Sección de bienvenida/edición (parte superior)
  document.querySelector("#welcome-name").textContent = userName;
  document.querySelector("#edit-profile-btn").onclick = () => editProfile(userName);
  
  // Tu Información Personal (sin nombre)
  document.querySelector("#weight").textContent = `${metrics.weight} kg`;
  document.querySelector("#height").textContent = `${metrics.height} cm`;
  document.querySelector("#imc").textContent = (
    metrics.weight / ((metrics.height / 100) ** 2)
  ).toFixed(1);
  
  // Objetivos Diarios
  document.querySelector("#calorie-goal").textContent = `${metrics.calorie_goal} kcal`;
  document.querySelector("#protein-goal").textContent = `${metrics.protein_goal}g`;
  document.querySelector("#carbs-goal").textContent = `${metrics.carbs_goal}g`;
  document.querySelector("#fat-goal").textContent = `${metrics.fat_goal}g`;
  
  // Today's Nutrition
  if (todayNutrition) {
    const caloriesRemaining = metrics.calorie_goal - todayNutrition.calories;
    const proteinRemaining = metrics.protein_goal - todayNutrition.protein;
    const carbsRemaining = metrics.carbs_goal - todayNutrition.carbs;
    const fatRemaining = metrics.fat_goal - todayNutrition.fat;
    
    document.querySelector("#calories-consumed").textContent = 
      `${todayNutrition.calories} kcal`;
    document.querySelector("#calories-remaining").textContent = 
      `Falta: ${caloriesRemaining} kcal`;
    
    document.querySelector("#protein-consumed").textContent = 
      `${todayNutrition.protein}g`;
    document.querySelector("#carbs-consumed").textContent = 
      `${todayNutrition.carbs}g`;
    document.querySelector("#fat-consumed").textContent = 
      `${todayNutrition.fat}g`;
    
    // Barras de progreso
    const caloriesProgress = (todayNutrition.calories / metrics.calorie_goal) * 100;
    const proteinProgress = (todayNutrition.protein / metrics.protein_goal) * 100;
    const carbsProgress = (todayNutrition.carbs / metrics.carbs_goal) * 100;
    const fatProgress = (todayNutrition.fat / metrics.fat_goal) * 100;
    
    document.querySelector("#progress-calories").style.width = `${caloriesProgress}%`;
    document.querySelector("#progress-protein").style.width = `${proteinProgress}%`;
    document.querySelector("#progress-carbs").style.width = `${carbsProgress}%`;
    document.querySelector("#progress-fat").style.width = `${fatProgress}%`;
  }
}

// Función para editar perfil
function editProfile(userName) {
  const newName = prompt("Nuevo nombre:", userName);
  if (newName) {
    // Guardar en localStorage o en tu sistema de auth
    localStorage.setItem("userName", newName);
    displayUserProfile(profile, newName);
  }
}
```

---

## 🤖 4. Chatbot de Recomendaciones

### Endpoint
```
POST /chat/{user_id}
```

### Frontend Code
```javascript
class NutritionChatbot {
  constructor(userId, userName = "Usuario") {
    this.userId = userId;
    this.userName = userName;
    this.messages = [];
  }
  
  async sendMessage(userMessage) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/${this.userId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          user_name: this.userName,
        }),
      });
      
      const data = await response.json();
      
      if (data.ok) {
        // Agregar a historial local
        this.messages.push({
          type: "user",
          content: userMessage,
          timestamp: new Date(),
        });
        
        this.messages.push({
          type: "assistant",
          content: data.response,
          timestamp: new Date(),
          metadata: data.metadata,
        });
        
        return data.response;
      } else {
        console.error("Error del chatbot:", data);
        return null;
      }
    } catch (error) {
      console.error("Error:", error);
      return null;
    }
  }
  
  async loadHistory() {
    try {
      const response = await fetch(
        `${API_BASE_URL}/chat/${this.userId}/history`
      );
      const data = await response.json();
      
      if (data.ok) {
        this.messages = data.history.map(msg => ({
          type: msg.message_type,
          content: msg.content,
          timestamp: msg.created_at,
        }));
        return this.messages;
      }
    } catch (error) {
      console.error("Error cargando historial:", error);
    }
  }
  
  async clearHistory() {
    try {
      const response = await fetch(
        `${API_BASE_URL}/chat/${this.userId}/history`,
        { method: "DELETE" }
      );
      const data = await response.json();
      
      if (data.ok) {
        this.messages = [];
        return true;
      }
    } catch (error) {
      console.error("Error limpiando historial:", error);
    }
  }
}

// Uso
const chatbot = new NutritionChatbot(userId, "Juan");

// Enviar mensaje
const response = await chatbot.sendMessage(
  "Acabo de comer 450 calorías. ¿Qué puedo comer ahora?"
);
console.log("Respuesta:", response);

// Cargar historial anterior
await chatbot.loadHistory();
console.log("Historial:", chatbot.messages);

// Limpiar historial
await chatbot.clearHistory();
```

---

## 🎨 UI Component Ejemplo (React)

```jsx
import { useState, useEffect } from "react";

export function NutritionChatbot({ userId, userName }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState(null);
  
  // Cargar perfil al iniciar
  useEffect(() => {
    fetchUserProfile();
    loadChatHistory();
  }, [userId]);
  
  async function fetchUserProfile() {
    const response = await fetch(`${API_BASE_URL}/user/${userId}/profile`);
    const data = await response.json();
    if (data.ok) setProfile(data.profile);
  }
  
  async function loadChatHistory() {
    const response = await fetch(`${API_BASE_URL}/chat/${userId}/history`);
    const data = await response.json();
    if (data.ok) {
      setMessages(data.history.map(msg => ({
        type: msg.message_type,
        content: msg.content,
      })));
    }
  }
  
  async function handleSendMessage() {
    if (!inputValue.trim()) return;
    
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/chat/${userId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: inputValue,
          user_name: userName,
        }),
      });
      
      const data = await response.json();
      
      if (data.ok) {
        setMessages(prev => [
          ...prev,
          { type: "user", content: inputValue },
          { type: "assistant", content: data.response },
        ]);
        setInputValue("");
      }
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  }
  
  async function handleClearHistory() {
    await fetch(`${API_BASE_URL}/chat/${userId}/history`, {
      method: "DELETE",
    });
    setMessages([]);
  }
  
  if (!profile) return <div>Cargando...</div>;
  
  const metrics = profile.metrics;
  const today = new Date().toISOString().split('T')[0];
  const todayNutrition = profile.daily_nutrition.find(d => d.date === today);
  const imc = (metrics.weight / ((metrics.height / 100) ** 2)).toFixed(1);
  
  return (
    <div className="nutrition-app">
      {/* Sección Superior - Bienvenida y Edición */}
      <div className="header-section">
        <div className="welcome">
          <h1>¡Bienvenido!</h1>
          <p>Rastrea tu nutrición diaria y mantén tus objetivos de salud</p>
        </div>
        
        <div className="user-info-edit">
          <h3>{userName}</h3>
          <button className="btn-edit" onClick={() => handleEditProfile()}>
            ✏️ Editar
          </button>
        </div>
      </div>
      
      {/* Tu Información Personal */}
      <div className="personal-info">
        <h2>Tu Información Personal</h2>
        <div className="info-grid">
          <div className="info-card">
            <label>Peso</label>
            <span className="value">{metrics.weight} kg</span>
          </div>
          <div className="info-card">
            <label>Altura</label>
            <span className="value">{metrics.height} cm</span>
          </div>
          <div className="info-card">
            <label>IMC</label>
            <span className="value">{imc}</span>
          </div>
        </div>
      </div>
      
      {/* Objetivos Diarios */}
      <div className="daily-goals">
        <h2>Objetivos Diarios</h2>
        <div className="goals-grid">
          <div className="goal-card">
            <label>Calorías</label>
            <span className="value">{metrics.calorie_goal} kcal</span>
          </div>
          <div className="goal-card">
            <label>Proteína</label>
            <span className="value">{metrics.protein_goal}g</span>
          </div>
          <div className="goal-card">
            <label>Carbos</label>
            <span className="value">{metrics.carbs_goal}g</span>
          </div>
          <div className="goal-card">
            <label>Grasas</label>
            <span className="value">{metrics.fat_goal}g</span>
          </div>
        </div>
      </div>
      
      {/* Today's Nutrition (Inicia en 0) */}
      <div className="nutrition-chatbot">
        <h2>Today's Nutrition (Inicia en 0)</h2>
        <div className="stats">
          <div className="stat">
            <label>Calories</label>
            <span>{todayNutrition?.calories || 0} {todayNutrition ? `/ ${metrics.calorie_goal}` : ''} kcal</span>
            {todayNutrition && (
              <span className="remaining">Target: {metrics.calorie_goal} kcal</span>
            )}
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{
                  width: `${((todayNutrition?.calories || 0) / metrics.calorie_goal) * 100}%`
                }}
              />
            </div>
          </div>
          
          <div className="stat">
            <label>Protein</label>
            <span>{todayNutrition?.protein || 0}g</span>
            <span className="target">Target: {metrics.protein_goal}g</span>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{
                  width: `${((todayNutrition?.protein || 0) / metrics.protein_goal) * 100}%`
                }}
              />
            </div>
          </div>
          
          <div className="stat">
            <label>Carbs</label>
            <span>{todayNutrition?.carbs || 0}g</span>
            <span className="target">Target: {metrics.carbs_goal}g</span>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{
                  width: `${((todayNutrition?.carbs || 0) / metrics.carbs_goal) * 100}%`
                }}
              />
            </div>
          </div>
          
          <div className="stat">
            <label>Fat</label>
            <span>{todayNutrition?.fat || 0}g</span>
            <span className="target">Target: {metrics.fat_goal}g</span>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{
                  width: `${((todayNutrition?.fat || 0) / metrics.fat_goal) * 100}%`
                }}
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Chatbot Section */}
      <div className="chatbot-section">
        <h2>Asesor Nutricional 🤖</h2>
        <div className="chat-container">
          <div className="chat-history">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.type}`}>
                <p>{msg.content}</p>
              </div>
            ))}
          </div>
          
          <div className="chat-input">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="¿Qué puedo comer? ¿Tengo espacio para...?"
              disabled={loading}
            />
            <button 
              onClick={handleSendMessage}
              disabled={loading}
            >
              {loading ? "Enviando..." : "Enviar"}
            </button>
            <button 
              onClick={handleClearHistory}
              className="secondary"
            >
              Limpiar Historial
            </button>
          </div>
        </div>
      </div>
    </div>
  );
  
  async function handleEditProfile() {
    const newName = prompt("Nuevo nombre:", userName);
    if (newName) {
      // Actualizar en tu sistema (localStorage, auth, etc)
      localStorage.setItem("userName", newName);
      window.location.reload(); // O actualizar estado
    }
  }
}
```

---

## 🎯 Flujo Completo Integrado

```javascript
async function completeNutritionFlow(userId, userName, imageFile) {
  // 1. Analizar imagen
  console.log("📸 Analizando imagen...");
  const nutrients = await analyzeMealImage(imageFile);
  
  if (!nutrients) {
    console.error("No se pudo analizar la imagen");
    return;
  }
  
  // 2. Guardar en Supabase
  console.log("💾 Guardando en Supabase...");
  await saveMealToSupabase(userId, nutrients);
  
  // 3. Obtener perfil actualizado
  console.log("👤 Cargando perfil...");
  const profile = await getUserProfile(userId);
  
  // 4. Obtener recomendación del chatbot
  console.log("🤖 Consultando chatbot...");
  const chatbot = new NutritionChatbot(userId, userName);
  
  const message = `
    Acabo de comer algo con:
    - ${Math.round(nutrients.calories)} calorías
    - ${Math.round(nutrients.protein_g)}g de proteína
    - ${Math.round(nutrients.carbs_g)}g de carbos
    - ${Math.round(nutrients.fat_g)}g de grasas
    
    ¿Qué me recomiendas que coma ahora?
  `;
  
  const recommendation = await chatbot.sendMessage(message);
  
  // 5. Mostrar resultado
  console.log("✅ Análisis completo");
  return {
    nutrients,
    profile,
    recommendation,
  };
}

// Uso
const result = await completeNutritionFlow(
  "afaa08a0-cff4-40eb-9686-c83ff3d256f8",
  "Juan",
  imageFile
);
```

---

## 📝 Checklist de Implementación

- [ ] Configurar `API_BASE_URL` según ambiente (dev/prod)
- [ ] Crear función `analyzeMealImage()`
- [ ] Crear clase `NutritionChatbot`
- [ ] Crear componente UI del chatbot
- [ ] Integrar con tu sistema de autenticación (userId)
- [ ] Integrar con Supabase para guardar nutrición
- [ ] Probar flujo completo en dev
- [ ] Desplegar en producción

---

## 🔐 Variables de Ambiente (Frontend)

```env
REACT_APP_API_BASE_URL=https://658096ec9c01.ngrok-free.app
REACT_APP_SUPABASE_URL=https://wlhawsxqhhlnwsuyymqm.supabase.co
REACT_APP_SUPABASE_ANON_KEY=sb_publishable_NiS3Oj_0qlxLBHQseT4PUw_d_OeXHd6
```

---

## 🚀 Próximos Pasos

1. Copia este código a tu proyecto
2. Ajusta rutas y estilos según tu diseño
3. Prueba en Swagger: `http://localhost:8000/docs`
4. Integra en tu componente de nutrición

¿Necesitas ayuda con alguna parte específica?
