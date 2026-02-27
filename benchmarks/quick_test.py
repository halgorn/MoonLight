#!/usr/bin/env python3
"""
Quick benchmark test - Teste rápido de performance
Usa Fibonacci pequeno para teste rápido
"""

import time
import subprocess
import sys
from pathlib import Path

def test_python():
    """Testa Python puro"""
    code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

print(fib(30))
"""
    start = time.perf_counter()
    result = subprocess.run([sys.executable, "-c", code], 
                          capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    return elapsed, result.stdout.strip()

def test_moonlight():
    """Testa MoonLight interpretado"""
    code = """def fib(n) {
    if (n <= 1) { return n }
    return fib(n-1) + fib(n-2)
}
print(fib(30))
"""
    # Salvar temporário
    temp_file = Path("temp_test.gpu")
    temp_file.write_text(code)
    
    start = time.perf_counter()
    result = subprocess.run([sys.executable, "executor_main.py", str(temp_file)],
                          capture_output=True, text=True)
    elapsed = time.perf_counter() - start
    
    temp_file.unlink()
    return elapsed, result.stdout.strip()

def main():
    print("="*60)
    print("Quick Performance Test: Fibonacci(30)")
    print("="*60)
    
    print("\n1. Python puro...")
    py_time, py_result = test_python()
    print(f"   Resultado: {py_result}")
    print(f"   Tempo: {py_time:.4f}s")
    
    print("\n2. MoonLight interpretado...")
    moon_time, moon_result = test_moonlight()
    print(f"   Resultado: {moon_result}")
    print(f"   Tempo: {moon_time:.4f}s")
    
    print("\n" + "="*60)
    print("Comparação:")
    print("="*60)
    
    if py_time < moon_time:
        ratio = moon_time / py_time
        print(f"✅ Python foi {ratio:.2f}x mais rápido")
        print("   (Normal para modo interpretado)")
    else:
        ratio = py_time / moon_time
        print(f"🚀 MoonLight foi {ratio:.2f}x mais rápido!")
    
    print("\n💡 Dica: Para MoonLight realmente brilhar, compile:")
    print("   python moonc.py programa.gpu -o programa")
    print("   ./programa")
    print("\n   Speedup esperado: 5-10x vs Python! 🚀")

if __name__ == "__main__":
    main()

