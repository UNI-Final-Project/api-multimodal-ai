#!/usr/bin/env python3
"""
verify_implementation.py - Script para verificar la implementación de LangGraph
Ejecutar: python verify_implementation.py
"""

import sys
from pathlib import Path

def check_file_exists(path, description):
    """Verifica si un archivo existe"""
    p = Path(path)
    exists = p.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_imports():
    """Verifica que los módulos se puedan importar"""
    print("\n📦 Verificando importaciones...")
    
    modules = [
        ("orchestration_state", "Estado y tipos"),
        ("orchestration_graph", "Grafo compilado"),
        ("orchestration_config", "Configuración"),
    ]
    
    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"✅ {description}: import {module_name} OK")
        except ImportError as e:
            print(f"❌ {description}: import {module_name} FAILED - {e}")
            all_ok = False
    
    return all_ok

def check_dependencies():
    """Verifica las dependencias instaladas"""
    print("\n📚 Verificando dependencias...")
    
    required = [
        "langgraph",
        "langchain",
        "langchain_core",
        "langchain_google_genai",
        "fastapi",
        "google",
    ]
    
    all_ok = True
    for package in required:
        try:
            __import__(package.replace("_", "-"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NO INSTALADO")
            all_ok = False
    
    return all_ok

def check_env_vars():
    """Verifica variables de entorno"""
    print("\n🔑 Verificando variables de entorno...")
    
    import os
    
    required = {
        "GOOGLE_API_KEY": "API Key de Google",
    }
    
    optional = {
        "GEMINI_MODEL": "Modelo Gemini a usar",
        "PORT": "Puerto del servidor",
    }
    
    # Requeridas
    all_ok = True
    for var, desc in required.items():
        value = os.environ.get(var)
        if value:
            masked = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: NO DEFINIDA")
            all_ok = False
    
    # Opcionales
    for var, desc in optional.items():
        value = os.environ.get(var)
        if value:
            print(f"ℹ️  {var}: {value}")
        else:
            print(f"ℹ️  {var}: (no configurada, usa default)")
    
    return all_ok

def check_code_structure():
    """Verifica la estructura del código"""
    print("\n📂 Verificando estructura de código...")
    
    files = {
        "MultimediaLLM.py": "FastAPI principal",
        "orchestration_state.py": "Dataclasses y tipos",
        "orchestration_graph.py": "Compilación LangGraph",
        "orchestration_config.py": "Configuración centralizada",
        "requirements.txt": "Dependencias",
    }
    
    all_ok = True
    for filename, description in files.items():
        if not check_file_exists(filename, description):
            all_ok = False
    
    return all_ok

def check_documentation():
    """Verifica la documentación"""
    print("\n📖 Verificando documentación...")
    
    docs = {
        "README_LANGGRAPH.md": "Guía rápida",
        "ORCHESTRATION.md": "Documentación técnica",
        "ESTRUCTURA.md": "Arquitectura y flujos",
        "IMPLEMENTACION_COMPLETA.txt": "Resumen de implementación",
    }
    
    all_ok = True
    for filename, description in docs.items():
        if not check_file_exists(filename, description):
            all_ok = False
    
    return all_ok

def check_graph_compilation():
    """Verifica que el grafo se compila correctamente"""
    print("\n🔧 Verificando compilación del grafo...")
    
    try:
        from orchestration_graph import get_orchestration_graph
        graph = get_orchestration_graph()
        print(f"✅ Grafo compilado exitosamente")
        print(f"   Nodos: {len(graph.nodes) if hasattr(graph, 'nodes') else 'N/A'}")
        return True
    except Exception as e:
        print(f"❌ Error compilando grafo: {e}")
        return False

def run_simple_test():
    """Ejecuta un test simple"""
    print("\n🧪 Ejecutando test simple...")
    
    try:
        from orchestration_state import OrchestrationState, MediaFile
        
        # Crear estado
        state = OrchestrationState(
            question="Test pregunta",
            media_files=[
                MediaFile(
                    filename="test.jpg",
                    mime_type="image/jpeg",
                    data=b"fake_data",
                    size_bytes=9,
                )
            ]
        )
        
        print(f"✅ Estado creado: {state.question}")
        print(f"   Media files: {len(state.media_files)}")
        print(f"   Validation passed: {state.validation_passed}")
        return True
    
    except Exception as e:
        print(f"❌ Error en test: {e}")
        return False

def main():
    """Ejecuta todas las verificaciones"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE IMPLEMENTACIÓN LANGGRAPH")
    print("=" * 60)
    
    results = {
        "Estructura de código": check_code_structure(),
        "Documentación": check_documentation(),
        "Dependencias": check_dependencies(),
        "Variables de entorno": check_env_vars(),
        "Compilación del grafo": check_graph_compilation(),
        "Test simple": run_simple_test(),
    }
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    for check_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ¡TODO ESTÁ LISTO!")
        print("\nPróximos pasos:")
        print("  1. python MultimediaLLM.py  # Ejecutar servidor")
        print("  2. open http://localhost:8080/docs  # Ver API docs")
        print("  3. Ver README_LANGGRAPH.md para más información")
        return 0
    else:
        print("❌ HAY PROBLEMAS QUE RESOLVER")
        print("\nVerifica:")
        print("  - requirements.txt instalado: pip install -r requirements.txt")
        print("  - .env configurado: GOOGLE_API_KEY=...")
        print("  - Archivos de código presentes en directorio")
        return 1

if __name__ == "__main__":
    sys.exit(main())
