#!/usr/bin/env python3
"""
MoonLight vs Python Benchmark Suite
Compara performance de MoonLight (interpretado e compilado) com Python puro
"""

import time
import subprocess
import sys
import os
from pathlib import Path

class BenchmarkRunner:
    def __init__(self):
        self.results = []
        self.project_root = Path(__file__).parent.parent
        
    def run_python(self, script_path):
        """Executa script Python e mede tempo"""
        print(f"  Executando Python: {script_path.name}")
        start = time.perf_counter()
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )
            elapsed = time.perf_counter() - start
            
            if result.returncode != 0:
                print(f"    ❌ Erro: {result.stderr}")
                return None
            
            return elapsed
        except subprocess.TimeoutExpired:
            print(f"    ❌ Timeout (>5min)")
            return None
        except Exception as e:
            print(f"    ❌ Erro: {e}")
            return None
    
    def run_moonlight_interpreted(self, script_path):
        """Executa script MoonLight interpretado"""
        print(f"  Executando MoonLight (interpretado): {script_path.name}")
        start = time.perf_counter()
        try:
            result = subprocess.run(
                [sys.executable, str(self.project_root / "executor_main.py"), str(script_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            elapsed = time.perf_counter() - start
            
            if result.returncode != 0:
                print(f"    ❌ Erro: {result.stderr}")
                return None
            
            return elapsed
        except subprocess.TimeoutExpired:
            print(f"    ❌ Timeout (>5min)")
            return None
        except Exception as e:
            print(f"    ❌ Erro: {e}")
            return None
    
    def run_moonlight_compiled(self, script_path):
        """Compila e executa script MoonLight"""
        print(f"  Executando MoonLight (compilado): {script_path.name}")
        
        # Compilar
        exe_name = script_path.stem + "_compiled"
        if sys.platform == "win32":
            exe_name += ".exe"
        
        exe_path = self.project_root / "benchmarks" / exe_name
        
        print(f"    Compilando para {exe_name}...")
        compile_result = subprocess.run(
            [sys.executable, str(self.project_root / "moonc.py"), 
             str(script_path), "-o", str(exe_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if compile_result.returncode != 0:
            print(f"    ❌ Erro na compilação: {compile_result.stderr}")
            return None
        
        # Executar
        start = time.perf_counter()
        try:
            result = subprocess.run(
                [str(exe_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            elapsed = time.perf_counter() - start
            
            # Limpar executável
            if exe_path.exists():
                exe_path.unlink()
            
            if result.returncode != 0:
                print(f"    ❌ Erro na execução: {result.stderr}")
                return None
            
            return elapsed
        except subprocess.TimeoutExpired:
            print(f"    ❌ Timeout (>5min)")
            if exe_path.exists():
                exe_path.unlink()
            return None
        except Exception as e:
            print(f"    ❌ Erro: {e}")
            if exe_path.exists():
                exe_path.unlink()
            return None
    
    def run_benchmark(self, name, moonlight_script, python_script):
        """Executa um benchmark completo"""
        print(f"\n{'='*70}")
        print(f"Benchmark: {name}")
        print(f"{'='*70}")
        
        result = {
            'name': name,
            'python': None,
            'moonlight_interp': None,
            'moonlight_compiled': None
        }
        
        # Python
        result['python'] = self.run_python(python_script)
        
        # MoonLight Interpretado
        result['moonlight_interp'] = self.run_moonlight_interpreted(moonlight_script)
        
        # MoonLight Compilado (C++)
        result['moonlight_compiled'] = self.run_moonlight_compiled(moonlight_script)
        
        # Mostrar resultados
        print(f"\n  Resultados:")
        if result['python']:
            print(f"    Python:                 {result['python']:.4f}s")
        if result['moonlight_interp']:
            print(f"    MoonLight (interp):     {result['moonlight_interp']:.4f}s")
        if result['moonlight_compiled']:
            print(f"    MoonLight (compilado):  {result['moonlight_compiled']:.4f}s")
        
        # Calcular speedups
        if result['python'] and result['moonlight_compiled']:
            speedup = result['python'] / result['moonlight_compiled']
            print(f"\n  🚀 Speedup (compilado vs Python): {speedup:.2f}x")
            if speedup > 1:
                print(f"     MoonLight é {speedup:.2f}x MAIS RÁPIDO!")
            else:
                print(f"     Python é {1/speedup:.2f}x mais rápido")
        
        self.results.append(result)
        return result
    
    def print_summary(self):
        """Imprime resumo de todos os benchmarks"""
        print(f"\n\n{'='*70}")
        print("RESUMO GERAL DOS BENCHMARKS")
        print(f"{'='*70}\n")
        
        print(f"{'Benchmark':<30} {'Python':<12} {'Interp':<12} {'Compilado':<12} {'Speedup'}")
        print("-" * 85)
        
        for r in self.results:
            py = f"{r['python']:.3f}s" if r['python'] else "N/A"
            interp = f"{r['moonlight_interp']:.3f}s" if r['moonlight_interp'] else "N/A"
            comp = f"{r['moonlight_compiled']:.3f}s" if r['moonlight_compiled'] else "N/A"
            
            speedup = ""
            if r['python'] and r['moonlight_compiled']:
                sp = r['python'] / r['moonlight_compiled']
                speedup = f"{sp:.2f}x"
            
            print(f"{r['name']:<30} {py:<12} {interp:<12} {comp:<12} {speedup}")
        
        # Calcular speedup médio
        speedups = []
        for r in self.results:
            if r['python'] and r['moonlight_compiled']:
                speedups.append(r['python'] / r['moonlight_compiled'])
        
        if speedups:
            avg_speedup = sum(speedups) / len(speedups)
            print(f"\n🏆 Speedup médio (MoonLight compilado vs Python): {avg_speedup:.2f}x")
            
            if avg_speedup > 1:
                print(f"   MoonLight é em média {avg_speedup:.2f}x MAIS RÁPIDO que Python! 🚀")
            else:
                print(f"   Python é em média {1/avg_speedup:.2f}x mais rápido")

def main():
    print("="*70)
    print("MoonLight vs Python - Suite de Benchmarks")
    print("="*70)
    
    runner = BenchmarkRunner()
    benchmark_dir = Path(__file__).parent
    
    # Lista de benchmarks
    benchmarks = [
        ("Fibonacci (Recursão)", 
         benchmark_dir / "benchmark_fibonacci.gpu",
         benchmark_dir / "benchmark_fibonacci.py"),
        
        ("Loops Intensivos", 
         benchmark_dir / "benchmark_loops.gpu",
         benchmark_dir / "benchmark_loops.py"),
        
        ("Manipulação de Arrays", 
         benchmark_dir / "benchmark_arrays.gpu",
         benchmark_dir / "benchmark_arrays.py"),
    ]
    
    # Executar cada benchmark
    for name, moon_script, py_script in benchmarks:
        if moon_script.exists() and py_script.exists():
            runner.run_benchmark(name, moon_script, py_script)
        else:
            print(f"\n⚠️  Pulando {name}: arquivos não encontrados")
    
    # Mostrar resumo
    runner.print_summary()
    
    print(f"\n{'='*70}")
    print("Benchmarks concluídos!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()

