# 📊 Script de Validación: /analyze-meal

## Descripción

Script Python para probar y validar el endpoint `/analyze-meal` de la API NutriApp.

## Requisitos

```bash
pip install requests
```

## Uso

### Opción 1: Prueba automática (busca imagen en directorios estándar)

```bash
python test_analyze_meal_api.py
```

Busca automáticamente en:
- `tests/sample_meal.jpg`
- `test_image.jpg`
- `sample_meal.jpg`

### Opción 2: Proporcionar imagen específica

```bash
python test_analyze_meal_api.py ruta/a/tu/imagen.jpg
```

Ejemplo:
```bash
python test_analyze_meal_api.py C:\Users\Usuario\Pictures\comida.jpg
```

## Qué valida el script

✅ **Servidor**: Verifica que la API esté corriendo
✅ **Estructura de respuesta**: Comprueba que tenga los campos requeridos
✅ **Tipos de datos**: Valida que los nutrientes sean números
✅ **Campos requeridos**: 
  - `calories`
  - `protein_g`
  - `carbs_g`
  - `fat_g`

✅ **Campos opcionales**:
  - `fiber_g`
  - `sugar_g`
  - `sodium_mg`

✅ **Metadata**: Verifica tiempo de procesamiento

## Ejemplo de salida exitosa

```
============================================================
PRUEBA DE API: /analyze-meal
============================================================
✓ Servidor está activo

============================================================
TEST: /analyze-meal
============================================================
Imagen: tests/sample_meal.jpg
Enviando petición...
Status Code: 200

------------------------------------------------------------
RESPUESTA:
------------------------------------------------------------
{
  "ok": true,
  "nutrients": {
    "calories": 450,
    "protein_g": 35,
    "carbs_g": 55,
    "fat_g": 18,
    "fiber_g": 5,
    "sugar_g": 2,
    "sodium_mg": 600
  },
  "metadata": {
    "method": "direct_gemini_sdk",
    "model": "gemini-2.5-flash",
    "processing_time_ms": 6234.5
  }
}

------------------------------------------------------------
VALIDACIÓN:
------------------------------------------------------------
✓ ok = true

Campos requeridos:
  ✓ calories: 450
  ✓ protein_g: 35
  ✓ carbs_g: 55
  ✓ fat_g: 18

Campos opcionales:
  ✓ fiber_g: 5
  ✓ sugar_g: 2
  ✓ sodium_mg: 600

Metadata:
  - Tiempo procesamiento: 6234.5 ms

============================================================
✓ VALIDACIÓN EXITOSA
============================================================
```

## Pasos para probar

1. **Asegúrate que el servidor está corriendo:**
   ```bash
   python src/MultimediaLLM.py
   ```

2. **En otra terminal, ejecuta el test:**
   ```bash
   python test_analyze_meal_api.py
   ```

3. **O con una imagen específica:**
   ```bash
   python test_analyze_meal_api.py tu_imagen.jpg
   ```

## Solución de problemas

### "No se puede conectar al servidor"
- Verifica que `python src/MultimediaLLM.py` esté ejecutándose
- Comprueba que está en `http://localhost:8000`

### "Archivo no encontrado"
- Proporciona la ruta completa: `python test_analyze_meal_api.py C:\ruta\imagen.jpg`

### "Error en la respuesta"
- Revisa los logs de la API en el servidor
- Verifica que la imagen sea válida (JPG, PNG, etc.)

## Endpoints disponibles

- `GET /health` - Health check
- `POST /analyze-meal` - Analiza una imagen de comida
- `POST /qa` - QA multimodal con pregunta + archivos
- `GET /env-check` - Verifica configuración de variables
