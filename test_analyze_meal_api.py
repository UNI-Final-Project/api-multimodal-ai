#!/usr/bin/env python3
"""
Script de prueba para validar el endpoint /analyze-meal
Envía una imagen y valida que retorne los valores nutricionales correctos
"""

import requests
import json
import sys
from pathlib import Path

# Configuración
API_URL = "http://localhost:8000"
ANALYZE_MEAL_ENDPOINT = f"{API_URL}/analyze-meal"

def test_health():
    """Verifica que el servidor esté activo"""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✓ Servidor está activo")
            return True
        else:
            print("✗ Servidor no respondió correctamente")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ No se puede conectar al servidor. ¿Está corriendo en http://localhost:8000?")
        return False

def test_analyze_meal(image_path: str):
    """
    Prueba el endpoint /analyze-meal con una imagen
    
    Args:
        image_path: Ruta a la imagen para analizar
    """
    print("\n" + "="*60)
    print("TEST: /analyze-meal")
    print("="*60)
    
    # Validar que el archivo existe
    if not Path(image_path).exists():
        print(f"✗ Archivo no encontrado: {image_path}")
        return False
    
    print(f"Imagen: {image_path}")
    
    try:
        # Preparar archivo
        with open(image_path, 'rb') as f:
            files = {'file': f}
            
            print("Enviando petición...")
            response = requests.post(ANALYZE_MEAL_ENDPOINT, files=files)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"✗ Error: {response.text}")
            return False
        
        # Parsear respuesta
        data = response.json()
        
        print("\n" + "-"*60)
        print("RESPUESTA:")
        print("-"*60)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Validar estructura
        print("\n" + "-"*60)
        print("VALIDACIÓN:")
        print("-"*60)
        
        # Verificar campos principales
        if not isinstance(data, dict):
            print("✗ La respuesta no es un diccionario")
            return False
        
        if 'ok' not in data:
            print("✗ Falta el campo 'ok'")
            return False
        
        if not data['ok']:
            print("✗ ok = false")
            print(f"  Error: {data.get('detail', 'Desconocido')}")
            return False
        
        print("✓ ok = true")
        
        # Validar nutrientes
        if 'nutrients' not in data:
            print("✗ Falta el campo 'nutrients'")
            return False
        
        nutrients = data['nutrients']
        required_fields = ['calories', 'protein_g', 'carbs_g', 'fat_g']
        optional_fields = ['fiber_g', 'sugar_g', 'sodium_mg']
        
        print("\nCampos requeridos:")
        for field in required_fields:
            if field not in nutrients:
                print(f"  ✗ {field}: FALTA")
                return False
            value = nutrients[field]
            if not isinstance(value, (int, float)):
                print(f"  ✗ {field}: No es número (tipo: {type(value).__name__})")
                return False
            print(f"  ✓ {field}: {value}")
        
        print("\nCampos opcionales:")
        for field in optional_fields:
            if field in nutrients:
                value = nutrients[field]
                if isinstance(value, (int, float)):
                    print(f"  ✓ {field}: {value}")
                else:
                    print(f"  ! {field}: No es número (tipo: {type(value).__name__})")
            else:
                print(f"  - {field}: No presente")
        
        # Validar metadata
        if 'metadata' not in data:
            print("\n✗ Falta el campo 'metadata'")
            return False
        
        metadata = data['metadata']
        print(f"\nMetadata:")
        print(f"  - Tiempo procesamiento: {metadata.get('processing_time_ms', 'N/A')} ms")
        
        print("\n" + "="*60)
        print("✓ VALIDACIÓN EXITOSA")
        print("="*60)
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error en la petición: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Error al parsear JSON: {e}")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("PRUEBA DE API: /analyze-meal")
    print("="*60)
    
    # Prueba de salud
    if not test_health():
        print("\n✗ El servidor no está disponible")
        sys.exit(1)
    
    # Buscar una imagen de prueba
    test_image = None
    possible_paths = [
        "tests/sample_meal.jpg",
        "test_image.jpg",
        "sample_meal.jpg",
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            test_image = path
            break
    
    if not test_image:
        print("\n⚠ No se encontró imagen de prueba.")
        print("  Rutas buscadas:")
        for path in possible_paths:
            print(f"    - {path}")
        print("\n  Por favor, proporciona una imagen para probar:")
        print("  python test_analyze_meal_api.py <ruta_imagen>")
        return
    
    # Prueba con imagen
    if test_analyze_meal(test_image):
        print("\n✓ API funcionando correctamente")
    else:
        print("\n✗ API tiene problemas")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Usar imagen proporcionada como argumento
        test_health()
        test_analyze_meal(sys.argv[1])
    else:
        main()
