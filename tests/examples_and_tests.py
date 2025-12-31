"""
examples_and_tests.py - Ejemplos de uso y tests del flujo de orquestación
"""

import sys
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestration_graph import invoke_orchestration, get_orchestration_graph
from orchestration_state import OrchestrationState, MediaFile, AnalysisType
from orchestration_config import get_config


# ============================================================
# EJEMPLOS DE USO
# ============================================================

def example_1_simple_question_with_image():
    """
    Ejemplo 1: Pregunta simple con una imagen
    """
    print("\n" + "=" * 60)
    print("EJEMPLO 1: Análisis de plato en imagen")
    print("=" * 60)
    
    # Simular carga de imagen
    with open("test_image.jpg", "rb") as f:
        image_data = f.read()
    
    media = MediaFile(
        filename="plato.jpg",
        mime_type="image/jpeg",
        data=image_data,
        size_bytes=len(image_data),
    )
    
    question = "¿Es este plato equilibrado? ¿Qué le falta?"
    
    answer, metadata = invoke_orchestration(
        question=question,
        media_files=[media],
        use_files_api=False,
    )
    
    print(f"\n📝 Pregunta: {question}")
    print(f"\n💬 Respuesta:\n{answer}")
    print(f"\n📊 Metadatos:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")


def example_2_recipe_suggestion():
    """
    Ejemplo 2: Sugerencia de recetas basada en ingredientes visibles
    """
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Sugerencia de recetas")
    print("=" * 60)
    
    with open("ingredients.jpg", "rb") as f:
        image_data = f.read()
    
    media = MediaFile(
        filename="ingredientes.jpg",
        mime_type="image/jpeg",
        data=image_data,
        size_bytes=len(image_data),
    )
    
    question = "¿Qué recetas puedo hacer con estos ingredientes? Dame ideas creativas pero saludables."
    
    answer, metadata = invoke_orchestration(
        question=question,
        media_files=[media],
        use_files_api=False,
    )
    
    print(f"\n📝 Pregunta: {question}")
    print(f"\n💬 Respuesta:\n{answer}")
    print(f"\n🔍 Análisis detectados: {metadata['analysis_types']}")


def example_3_multiple_files():
    """
    Ejemplo 3: Múltiples archivos (desayuno, almuerzo, cena)
    """
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Análisis de diario de comidas (3 fotos)")
    print("=" * 60)
    
    media_files = []
    for filename in ["breakfast.jpg", "lunch.jpg", "dinner.jpg"]:
        try:
            with open(filename, "rb") as f:
                data = f.read()
                media_files.append(MediaFile(
                    filename=filename,
                    mime_type="image/jpeg",
                    data=data,
                    size_bytes=len(data),
                ))
        except FileNotFoundError:
            print(f"  ⚠️  Archivo {filename} no encontrado")
    
    question = "Analiza mi diario de comidas de hoy. ¿Estoy comiendo balanceado? ¿Qué puedo mejorar?"
    
    if media_files:
        answer, metadata = invoke_orchestration(
            question=question,
            media_files=media_files,
            use_files_api=False,
        )
        
        print(f"\n📝 Pregunta: {question}")
        print(f"\n📊 Archivos procesados: {metadata['media_count']}")
        print(f"\n💬 Respuesta:\n{answer}")
    else:
        print("  No se encontraron archivos para este ejemplo")


def example_4_product_label_analysis():
    """
    Ejemplo 4: Análisis de etiqueta nutricional (PDF o foto)
    """
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Análisis de etiqueta nutricional")
    print("=" * 60)
    
    try:
        with open("nutrition_label.pdf", "rb") as f:
            label_data = f.read()
        
        media = MediaFile(
            filename="etiqueta.pdf",
            mime_type="application/pdf",
            data=label_data,
            size_bytes=len(label_data),
        )
        
        question = "¿Es este producto saludable? ¿Cuáles son sus principales componentes?"
        
        answer, metadata = invoke_orchestration(
            question=question,
            media_files=[media],
            use_files_api=False,  # O True si el PDF es >20MB
        )
        
        print(f"\n📝 Pregunta: {question}")
        print(f"\n💬 Respuesta:\n{answer}")
        print(f"\n🔍 Análisis detectados: {metadata['analysis_types']}")
    
    except FileNotFoundError:
        print("  ⚠️  Archivo nutrition_label.pdf no encontrado")


# ============================================================
# TESTS UNITARIOS
# ============================================================

def test_validation_missing_question():
    """Test: Validación falla si falta pregunta"""
    print("\n" + "=" * 60)
    print("TEST: Validación de pregunta vacía")
    print("=" * 60)
    
    media = MediaFile(
        filename="test.jpg",
        mime_type="image/jpeg",
        data=b"fake_image_data",
        size_bytes=15,
    )
    
    answer, metadata = invoke_orchestration(
        question="",  # Vacía
        media_files=[media],
        use_files_api=False,
    )
    
    print(f"\n✅ PASS" if "vacía" in answer.lower() else f"\n❌ FAIL")
    print(f"   Respuesta: {answer[:100]}...")


def test_validation_missing_files():
    """Test: Validación falla si faltan archivos"""
    print("\n" + "=" * 60)
    print("TEST: Validación de archivos faltantes")
    print("=" * 60)
    
    answer, metadata = invoke_orchestration(
        question="¿Qué ves?",
        media_files=[],  # Sin archivos
        use_files_api=False,
    )
    
    print(f"\n✅ PASS" if "archivo" in answer.lower() else f"\n❌ FAIL")
    print(f"   Respuesta: {answer[:100]}...")


def test_classification_nutritional():
    """Test: Clasificación detecta análisis NUTRITIONAL"""
    print("\n" + "=" * 60)
    print("TEST: Clasificación - Análisis nutricional")
    print("=" * 60)
    
    media = MediaFile(
        filename="test.jpg",
        mime_type="image/jpeg",
        data=b"fake_image_data",
        size_bytes=15,
    )
    
    question = "¿Cuáles son las calorías y proteína en este plato?"
    
    answer, metadata = invoke_orchestration(
        question=question,
        media_files=[media],
        use_files_api=False,
    )
    
    has_nutritional = "nutritional" in metadata.get('analysis_types', [])
    print(f"\n✅ PASS" if has_nutritional else f"\n❌ FAIL")
    print(f"   Tipos detectados: {metadata['analysis_types']}")


def test_classification_recipe():
    """Test: Clasificación detecta análisis RECIPE_SUGGESTION"""
    print("\n" + "=" * 60)
    print("TEST: Clasificación - Sugerencia de recetas")
    print("=" * 60)
    
    media = MediaFile(
        filename="test.jpg",
        mime_type="image/jpeg",
        data=b"fake_image_data",
        size_bytes=15,
    )
    
    question = "¿Qué recetas puedo hacer con estos ingredientes?"
    
    answer, metadata = invoke_orchestration(
        question=question,
        media_files=[media],
        use_files_api=False,
    )
    
    has_recipe = "recipe_suggestion" in metadata.get('analysis_types', [])
    print(f"\n✅ PASS" if has_recipe else f"\n❌ FAIL")
    print(f"   Tipos detectados: {metadata['analysis_types']}")


def test_execution_logs():
    """Test: Logs de ejecución se generan correctamente"""
    print("\n" + "=" * 60)
    print("TEST: Ejecución y logging")
    print("=" * 60)
    
    media = MediaFile(
        filename="test.jpg",
        mime_type="image/jpeg",
        data=b"fake_image_data",
        size_bytes=15,
    )
    
    answer, metadata = invoke_orchestration(
        question="Test pregunta",
        media_files=[media],
        use_files_api=False,
    )
    
    has_logs = 'execution_logs' in metadata
    logs_count = len(metadata.get('execution_logs', []))
    
    print(f"\n✅ PASS" if has_logs and logs_count > 0 else f"\n❌ FAIL")
    print(f"   Logs generados: {logs_count}")
    print(f"   Pasos ejecutados: {[log.get('step') for log in metadata.get('execution_logs', [])]}")


def test_performance_timing():
    """Test: Timing de ejecución se registra"""
    print("\n" + "=" * 60)
    print("TEST: Timing de procesamiento")
    print("=" * 60)
    
    media = MediaFile(
        filename="test.jpg",
        mime_type="image/jpeg",
        data=b"fake_image_data",
        size_bytes=15,
    )
    
    answer, metadata = invoke_orchestration(
        question="Test timing",
        media_files=[media],
        use_files_api=False,
    )
    
    processing_time = metadata.get('processing_time_ms', 0)
    has_timing = processing_time > 0
    
    print(f"\n✅ PASS" if has_timing else f"\n❌ FAIL")
    print(f"   Tiempo de procesamiento: {processing_time:.2f}ms")


# ============================================================
# RUNNER
# ============================================================

def run_all_examples():
    """Ejecuta todos los ejemplos"""
    print("\n" + "=" * 60)
    print("🚀 EJECUTANDO EJEMPLOS DE USO")
    print("=" * 60)
    
    examples = [
        # example_1_simple_question_with_image,  # Requiere test_image.jpg
        # example_2_recipe_suggestion,           # Requiere ingredients.jpg
        # example_3_multiple_files,              # Requiere breakfast/lunch/dinner.jpg
        # example_4_product_label_analysis,      # Requiere nutrition_label.pdf
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\n❌ Error en {example.__name__}: {e}")


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 60)
    print("🧪 EJECUTANDO TESTS")
    print("=" * 60)
    
    tests = [
        test_validation_missing_question,
        test_validation_missing_files,
        test_classification_nutritional,
        test_classification_recipe,
        test_execution_logs,
        test_performance_timing,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            # Contar si pasó o falló basado en output
        except Exception as e:
            print(f"\n❌ Error en {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"✅ Tests completados")
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ejemplos y tests de orquestación")
    parser.add_argument("--examples", action="store_true", help="Ejecutar ejemplos")
    parser.add_argument("--tests", action="store_true", help="Ejecutar tests")
    parser.add_argument("--all", action="store_true", help="Ejecutar todo")
    
    args = parser.parse_args()
    
    if args.all:
        run_all_examples()
        run_all_tests()
    elif args.examples:
        run_all_examples()
    elif args.tests:
        run_all_tests()
    else:
        print("Uso: python examples_and_tests.py [--examples] [--tests] [--all]")
        
        # Por defecto, ejecutar tests
        print("\n(Ejecutando tests por defecto...)")
        run_all_tests()
