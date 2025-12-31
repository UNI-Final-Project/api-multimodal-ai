# 🧪 Guía de Testing API - Copiar y Pegar

## Prerequisitos

```bash
# Terminal 1: Inicia el servidor (mantén abierta)
python src/MultimediaLLM.py

# Espera hasta ver:
# INFO:     Uvicorn running on http://127.0.0.1:8080
```

---

## ✅ OPCIÓN 1: Interfaz Web Swagger (MÁS FÁCIL)

### Paso 1: Abre en navegador
```
http://localhost:8080/docs
```

### Paso 2: Busca "POST /qa"

### Paso 3: Click en "Try it out"

### Paso 4: Copia y pega estos valores

**En campo "question":**
```
¿Qué estoy comiendo? ¿Es saludable? Dame análisis nutricional.
```

**En campo "files":**
- Haz click en "Select file"
- Selecciona una **imagen JPG o PNG** de tu comida
- (Si no tienes, descarga una de Google Imágenes)

**En campo "use_files_api":**
```
false
```

### Paso 5: Click en "Execute"

### Resultado esperado:
```json
{
  "ok": true,
  "answer": "# Análisis Nutricional\n\n[Tu respuesta aquí]",
  "metadata": {
    "question": "¿Qué estoy comiendo?...",
    "media_count": 1,
    "analysis_types": ["nutritional"],
    ...
  }
}
```

---

## ✅ OPCIÓN 2: Con cURL en PowerShell

### Test 1: Imagen simple (Copiar y Pegar)

```powershell
# Reemplaza: "C:\ruta\a\tu\imagen.jpg" con tu archivo
$imagePath = "C:\ruta\a\tu\imagen.jpg"
$question = "¿Qué estoy comiendo? ¿Es saludable?"

curl -X POST "http://localhost:8080/qa" `
  -F "question=$question" `
  -F "files=@`"$imagePath`"" `
  -F "use_files_api=false"
```

### Test 2: Video MP4 (Copiar y Pegar)

```powershell
# Reemplaza: "C:\Videos\receta.mp4" con tu video
$videoPath = "C:\Videos\receta.mp4"
$question = "¿Qué receta estoy preparando? ¿Cómo es la técnica?"

curl -X POST "http://localhost:8080/qa" `
  -F "question=$question" `
  -F "files=@`"$videoPath`"" `
  -F "use_files_api=false"
```

### Test 3: Múltiples archivos (Copiar y Pegar)

```powershell
# Imagen + PDF
$imagePath = "C:\plato.jpg"
$pdfPath = "C:\receta.pdf"
$question = "Compara la imagen del plato con la receta en PDF. ¿Falta algo?"

curl -X POST "http://localhost:8080/qa" `
  -F "question=$question" `
  -F "files=@`"$imagePath`"" `
  -F "files=@`"$pdfPath`"" `
  -F "use_files_api=false"
```

### Test 4: Caso Receta Sugerencia (Copiar y Pegar)

```powershell
# Imagen de ingredientes
$imagePath = "C:\ingredientes.jpg"
$question = "¿Qué recetas puedo hacer con estos ingredientes? Dame 3 ideas saludables."

curl -X POST "http://localhost:8080/qa" `
  -F "question=$question" `
  -F "files=@`"$imagePath`"" `
  -F "use_files_api=false"
```

### Test 5: Etiqueta de Producto (Copiar y Pegar)

```powershell
# Foto de etiqueta nutricional
$imagePath = "C:\etiqueta.jpg"
$question = "Analiza esta etiqueta nutricional. ¿Es saludable este producto? ¿Cuáles son sus macro nutrientes?"

curl -X POST "http://localhost:8080/qa" `
  -F "question=$question" `
  -F "files=@`"$imagePath`"" `
  -F "use_files_api=false"
```

---

## ✅ OPCIÓN 3: Python Script (Copiar y Pegar)

### Crear archivo: `test_api.py` en raíz del proyecto

```python
#!/usr/bin/env python3
"""
Test API multimodal - Copiar y pegar casos de uso
"""

import requests
import json
from pathlib import Path

API_URL = "http://localhost:8080/qa"

def test_image_analysis():
    """Test 1: Análisis de imagen"""
    print("\n" + "="*60)
    print("TEST 1: Análisis de Imagen")
    print("="*60)
    
    image_path = input("📸 Ruta de imagen (ej: C:\\plato.jpg): ").strip('"')
    question = "¿Qué estoy comiendo? ¿Es saludable? Dame análisis nutricional."
    
    if not Path(image_path).exists():
        print(f"❌ Archivo no encontrado: {image_path}")
        return
    
    with open(image_path, 'rb') as f:
        files = {'files': (Path(image_path).name, f, 'image/jpeg')}
        data = {'question': question, 'use_files_api': 'false'}
        
        print(f"📤 Enviando: {Path(image_path).name}")
        response = requests.post(API_URL, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ RESPUESTA:\n{result['answer']}")
            print(f"\n📊 Tiempo: {result['metadata'].get('processing_time_ms', 0):.0f}ms")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

def test_video_analysis():
    """Test 2: Análisis de video"""
    print("\n" + "="*60)
    print("TEST 2: Análisis de Video")
    print("="*60)
    
    video_path = input("🎬 Ruta de video (ej: C:\\receta.mp4): ").strip('"')
    question = "¿Qué receta estoy preparando? ¿Cómo es la técnica?"
    
    if not Path(video_path).exists():
        print(f"❌ Archivo no encontrado: {video_path}")
        return
    
    with open(video_path, 'rb') as f:
        files = {'files': (Path(video_path).name, f, 'video/mp4')}
        data = {'question': question, 'use_files_api': 'false'}
        
        print(f"📤 Enviando: {Path(video_path).name}")
        response = requests.post(API_URL, files=files, data=data, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ RESPUESTA:\n{result['answer']}")
            print(f"\n📊 Tiempo: {result['metadata'].get('processing_time_ms', 0):.0f}ms")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

def test_recipe_suggestion():
    """Test 3: Sugerencia de recetas"""
    print("\n" + "="*60)
    print("TEST 3: Sugerencia de Recetas")
    print("="*60)
    
    image_path = input("🥗 Ruta de imagen ingredientes (ej: C:\\ingredientes.jpg): ").strip('"')
    question = "¿Qué recetas puedo hacer con estos ingredientes? Dame 3 ideas saludables y prácticas."
    
    if not Path(image_path).exists():
        print(f"❌ Archivo no encontrado: {image_path}")
        return
    
    with open(image_path, 'rb') as f:
        files = {'files': (Path(image_path).name, f, 'image/jpeg')}
        data = {'question': question, 'use_files_api': 'false'}
        
        print(f"📤 Enviando: {Path(image_path).name}")
        response = requests.post(API_URL, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ RESPUESTA:\n{result['answer']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

def test_product_label():
    """Test 4: Análisis de etiqueta"""
    print("\n" + "="*60)
    print("TEST 4: Análisis de Etiqueta Nutricional")
    print("="*60)
    
    image_path = input("🏷️  Ruta de foto etiqueta (ej: C:\\etiqueta.jpg): ").strip('"')
    question = "Analiza esta etiqueta nutricional. ¿Es saludable? ¿Cuáles son sus macronutrientes principales?"
    
    if not Path(image_path).exists():
        print(f"❌ Archivo no encontrado: {image_path}")
        return
    
    with open(image_path, 'rb') as f:
        files = {'files': (Path(image_path).name, f, 'image/jpeg')}
        data = {'question': question, 'use_files_api': 'false'}
        
        print(f"📤 Enviando: {Path(image_path).name}")
        response = requests.post(API_URL, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ RESPUESTA:\n{result['answer']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

def test_multiple_files():
    """Test 5: Múltiples archivos"""
    print("\n" + "="*60)
    print("TEST 5: Múltiples Archivos (Imagen + PDF)")
    print("="*60)
    
    image_path = input("📸 Ruta de imagen (ej: C:\\plato.jpg): ").strip('"')
    pdf_path = input("📄 Ruta de PDF (ej: C:\\receta.pdf): ").strip('"')
    question = "Compara la imagen del plato con la receta en PDF. ¿El plato se ve como la receta? ¿Falta algo?"
    
    if not Path(image_path).exists() or not Path(pdf_path).exists():
        print(f"❌ Uno o ambos archivos no encontrados")
        return
    
    files = {}
    with open(image_path, 'rb') as f1, open(pdf_path, 'rb') as f2:
        files = [
            ('files', (Path(image_path).name, f1, 'image/jpeg')),
            ('files', (Path(pdf_path).name, f2, 'application/pdf'))
        ]
        data = {'question': question, 'use_files_api': 'false'}
        
        print(f"📤 Enviando: {Path(image_path).name} + {Path(pdf_path).name}")
        response = requests.post(API_URL, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ RESPUESTA:\n{result['answer']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

def health_check():
    """Verificar que el servidor está activo"""
    print("\n" + "="*60)
    print("VERIFICANDO SERVIDOR")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL.replace('/qa', '')}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor activo")
            return True
        else:
            print("❌ Servidor no responde correctamente")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Asegúrate de que FastAPI está corriendo:")
        print(f"   python src/MultimediaLLM.py")
        return False

def main():
    """Menú principal"""
    print("\n" + "="*60)
    print("🧪 TEST API - NutriApp Multimodal")
    print("="*60)
    
    # Verificar servidor
    if not health_check():
        return
    
    while True:
        print("\n" + "="*60)
        print("MENÚ DE TESTS")
        print("="*60)
        print("1. Análisis de Imagen")
        print("2. Análisis de Video")
        print("3. Sugerencia de Recetas")
        print("4. Análisis de Etiqueta Nutricional")
        print("5. Múltiples Archivos (Imagen + PDF)")
        print("6. Salir")
        
        choice = input("\n🔢 Elige opción (1-6): ").strip()
        
        if choice == '1':
            test_image_analysis()
        elif choice == '2':
            test_video_analysis()
        elif choice == '3':
            test_recipe_suggestion()
        elif choice == '4':
            test_product_label()
        elif choice == '5':
            test_multiple_files()
        elif choice == '6':
            print("\n✅ ¡Gracias por usar NutriApp!")
            break
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()
```

### Ejecutar:

```bash
# Terminal 2 (mientras el servidor corre en Terminal 1)
python test_api.py

# Sigue los prompts e ingresa rutas de archivos
```

---

## 📋 CASOS DE PRUEBA LISTOS

### Caso 1: Análisis Simple
**Pregunta:**
```
¿Qué estoy comiendo? ¿Es saludable? Dame análisis nutricional detallado.
```
**Archivo:** Cualquier foto de comida (JPG/PNG)

---

### Caso 2: Sugerencia de Recetas
**Pregunta:**
```
¿Qué recetas puedo hacer con estos ingredientes? Dame 3 opciones saludables.
```
**Archivo:** Foto de ingredientes en una mesa

---

### Caso 3: Etiqueta Nutricional
**Pregunta:**
```
Analiza esta etiqueta nutricional. ¿Es saludable? ¿Qué macronutrientes destacan?
```
**Archivo:** Foto de etiqueta de producto (cereal, yogurt, etc.)

---

### Caso 4: Evaluación de Plato
**Pregunta:**
```
Evalúa este plato:
1. ¿Qué ingredientes ves?
2. ¿Es equilibrado?
3. ¿Tamaño de porción aproximado?
4. ¿Sugerencias de mejora?
```
**Archivo:** Foto de plato terminado

---

### Caso 5: Técnica de Video
**Pregunta:**
```
¿Qué estoy cocinando? Evalúa mi técnica. ¿Qué hago bien? ¿Qué puedo mejorar?
```
**Archivo:** Video MP4 (30 seg - 5 min)

---

## 🚀 Resumen Rápido

### Opción más fácil: **Swagger Web**
1. `http://localhost:8080/docs`
2. Click "POST /qa" → "Try it out"
3. Copia pregunta, sube imagen
4. Execute

### Opción programática: **Python Script**
1. `python test_api.py`
2. Elige test del menú
3. Ingresa ruta del archivo
4. Ver respuesta en Markdown

---

¡Listo para testear! 🎉
