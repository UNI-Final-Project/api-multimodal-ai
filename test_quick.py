#!/usr/bin/env python3
"""
Test rápido de la orquestación sin FastAPI
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestration.state import OrchestrationState, MediaFile, MediaType
from orchestration.graph import invoke_orchestration

# Test 1: Sin archivos (debe fallar validación)
print("=" * 60)
print("TEST 1: Sin archivos")
print("=" * 60)

try:
    answer, metadata = invoke_orchestration(
        question="¿Esto es saludable?",
        media_files=[],
        use_files_api=False
    )
    print(f"✅ Respuesta recibida")
    print(f"📝 Respuesta (primeros 200 chars): {answer[:200]}")
    print(f"📊 Metadata: {metadata}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("TEST 2: Con imagen simulada")
print("=" * 60)

# Crear imagen dummy de 1x1 píxel JPEG
jpeg_dummy = bytes.fromhex(
    "ffd8ffe000104a46494600010100000100010000"
    "ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c285037"
    "3d78edc019090909090c0b0c0c01110a0b10110101111111111111111111111111111111111111111111111111111111111111111111"
    "1111111111111111111111111111111111111111ffc0001108000100010111110111ffc4001f00000105010101010101010100000000"
    "0000000102030405060708090a0bffc400b5100002010303020403050504040000017d0102030004110512213106072322328108144"
    "291a1082342b1c11552d1f024262728292a3435363738393a434445464748494a535455565758595a636465666768696a7374757677"
    "78797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7"
    "d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffd9"
)

media_file = MediaFile(
    filename="test.jpg",
    mime_type="image/jpeg",
    data=jpeg_dummy,
    media_type=MediaType.IMAGE,
    size_bytes=len(jpeg_dummy),
)

try:
    answer, metadata = invoke_orchestration(
        question="¿Qué hay en esta imagen?",
        media_files=[media_file],
        use_files_api=False
    )
    print(f"✅ Respuesta recibida")
    print(f"📝 Respuesta (primeros 300 chars): {answer[:300]}")
    print(f"📊 Metadata: {metadata}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Tests completados")
