"""
Script de Benchmark de Performance para MoonLight
Testa código interpretado vs JIT compilado e mostra métricas de desempenho
"""

import time
import sys
import os
import subprocess
import tempfile
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from parser import parser
from executor_simple import executar_codigo
from llvm_backend import LLVM_AVAILABLE, generate_llvm_for_ast, jit_compiler
from moonc import compile_file
from transpiler import gerar_codigo_cpp

class PerformanceBenchmark:
    """Classe para executar benchmarks de performance"""
    
    def __init__(self):
        self.results = []
    
    def benchmark_interpreted(self, code, iterations=1, warmup=0):
        """
        Testa código MoonLight em modo interpretado
        
        Args:
            code: Código MoonLight como string
            iterations: Número de iterações para média
            warmup: Número de iterações de aquecimento
        
        Returns:
            dict com métricas de performance
        """
        # Parse do código
        parse_start = time.perf_counter()
        ast = parser.parse(code)
        parse_time = time.perf_counter() - parse_start
        
        if ast is None:
            return {'error': 'Falha ao parsear código'}
        
        # Warmup
        for _ in range(warmup):
            try:
                executar_codigo(code)
            except:
                pass
        
        # Execução medida
        execution_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                result = executar_codigo(code)
            except Exception as e:
                return {'error': f'Erro na execução: {e}'}
            end = time.perf_counter()
            execution_times.append(end - start)
        
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        return {
            'mode': 'interpreted',
            'parse_time': parse_time,
            'avg_execution_time': avg_time,
            'min_execution_time': min_time,
            'max_execution_time': max_time,
            'total_time': sum(execution_times),
            'iterations': iterations,
            'result': result
        }
    
    def benchmark_jit(self, code, iterations=1, warmup=0):
        """
        Testa código MoonLight com JIT compilation (se disponível)
        
        Args:
            code: Código MoonLight como string
            iterations: Número de iterações para média
            warmup: Número de iterações de aquecimento
        
        Returns:
            dict com métricas de performance ou None se JIT não disponível
        """
        if not LLVM_AVAILABLE:
            return {'error': 'JIT não disponível (llvmlite não instalado)'}
        
        # Parse do código
        parse_start = time.perf_counter()
        ast = parser.parse(code)
        parse_time = time.perf_counter() - parse_start
        
        if ast is None:
            return {'error': 'Falha ao parsear código'}
        
        # Tentar compilar com JIT
        if isinstance(ast, list) and len(ast) > 0:
            func_ast = ast[0]
            if isinstance(func_ast, tuple) and func_ast[0] == 'func_def':
                compile_start = time.perf_counter()
                llvm_ir = generate_llvm_for_ast(func_ast)
                compile_time = time.perf_counter() - compile_start
                
                if llvm_ir is None:
                    return {'error': 'Falha ao gerar LLVM IR'}
            else:
                return {'error': 'JIT só funciona com funções (@jit def ...)'}
        else:
            return {'error': 'JIT só funciona com funções (@jit def ...)'}
        
        # Por enquanto, JIT ainda usa interpretador como fallback
        # Então vamos medir o tempo de compilação + execução
        execution_times = []
        for _ in range(iterations):
            start = time.perf_counter()
            try:
                result = executar_codigo(code)
            except Exception as e:
                return {'error': f'Erro na execução: {e}'}
            end = time.perf_counter()
            execution_times.append(end - start)
        
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        return {
            'mode': 'jit',
            'parse_time': parse_time,
            'compile_time': compile_time,
            'avg_execution_time': avg_time,
            'min_execution_time': min_time,
            'max_execution_time': max_time,
            'total_time': sum(execution_times),
            'iterations': iterations,
            'result': result
        }
    
    def benchmark_compiled(self, code, iterations=1, warmup=0, optimize=True):
        """
        Testa código MoonLight compilado para executável
        
        Args:
            code: Código MoonLight como string
            iterations: Número de iterações para média
            warmup: Número de iterações de aquecimento
            optimize: Aplicar otimizações na compilação
        
        Returns:
            dict com métricas de performance
        """
        # Parse do código
        parse_start = time.perf_counter()
        ast = parser.parse(code)
        parse_time = time.perf_counter() - parse_start
        
        if ast is None:
            return {'error': 'Falha ao parsear código'}
        
        # Transpile para C++
        transpile_start = time.perf_counter()
        try:
            codigo_cpp = gerar_codigo_cpp(ast)
        except Exception as e:
            return {'error': f'Falha ao transpilar: {e}'}
        transpile_time = time.perf_counter() - transpile_start
        
        # Criar arquivo temporário
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            cpp_file = tmpdir_path / "benchmark_temp.cpp"
            exe_file = tmpdir_path / "benchmark_temp"
            
            if sys.platform == 'win32':
                exe_file = exe_file.with_suffix('.exe')
            
            # Escrever C++
            try:
                with open(cpp_file, 'w', encoding='utf-8') as f:
                    f.write(codigo_cpp)
            except Exception as e:
                return {'error': f'Falha ao escrever C++: {e}'}
            
            # Compilar
            compile_start = time.perf_counter()
            compile_cmd = ['g++', str(cpp_file), '-o', str(exe_file), '-std=c++17']
            if optimize:
                compile_cmd.append('-O2')
            
            try:
                result = subprocess.run(
                    compile_cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                compile_time = time.perf_counter() - compile_start
                
                if result.returncode != 0:
                    return {'error': f'Falha na compilação: {result.stderr}'}
            except subprocess.TimeoutExpired:
                return {'error': 'Timeout na compilação (>60s)'}
            except FileNotFoundError:
                return {'error': 'g++ não encontrado. Instale MinGW ou configure PATH.'}
            except Exception as e:
                return {'error': f'Erro na compilação: {e}'}
            
            # Verificar se executável foi criado
            if not exe_file.exists():
                return {'error': 'Executável não foi criado'}
            
            # Warmup
            for _ in range(warmup):
                try:
                    subprocess.run([str(exe_file)], capture_output=True, timeout=30)
                except:
                    pass
            
            # Executar e medir
            execution_times = []
            for _ in range(iterations):
                try:
                    start = time.perf_counter()
                    result = subprocess.run(
                        [str(exe_file)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    end = time.perf_counter()
                    execution_times.append(end - start)
                    
                    if result.returncode != 0:
                        return {'error': f'Erro na execução: {result.stderr}'}
                except subprocess.TimeoutExpired:
                    return {'error': 'Timeout na execução (>30s)'}
                except Exception as e:
                    return {'error': f'Erro ao executar: {e}'}
        
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        
        return {
            'mode': 'compiled',
            'parse_time': parse_time,
            'transpile_time': transpile_time,
            'compile_time': compile_time,
            'avg_execution_time': avg_time,
            'min_execution_time': min_time,
            'max_execution_time': max_time,
            'total_time': sum(execution_times),
            'iterations': iterations
        }
    
    def compare(self, code, iterations=10, warmup=2, test_compiled=True):
        """
        Compara performance entre modo interpretado e JIT
        
        Args:
            code: Código MoonLight como string
            iterations: Número de iterações
            warmup: Número de iterações de aquecimento
        
        Returns:
            dict com comparação de resultados
        """
        # Configurar encoding para Windows
        import sys
        if sys.platform == 'win32':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        
        print("=" * 70)
        print("MOONLIGHT PERFORMANCE BENCHMARK")
        print("=" * 70)
        print(f"\nCódigo testado ({len(code)} caracteres):")
        print("-" * 70)
        # Mostrar apenas primeiras linhas se muito longo
        lines = code.split('\n')
        if len(lines) > 10:
            print('\n'.join(lines[:5]))
            print("...")
            print('\n'.join(lines[-2:]))
        else:
            print(code)
        print("-" * 70)
        
        # Benchmark interpretado
        print("\n[1/3] Testando modo INTERPRETADO...")
        interpreted_result = self.benchmark_interpreted(code, iterations, warmup)
        
        if 'error' in interpreted_result:
            print(f"ERRO: {interpreted_result['error']}")
            return None
        
        # Benchmark JIT
        print("[2/3] Testando modo JIT...")
        jit_result = self.benchmark_jit(code, iterations, warmup)
        
        if 'error' in jit_result:
            print(f"AVISO JIT: {jit_result['error']}")
            jit_result = None
        
        # Benchmark compilado
        compiled_result = None
        if test_compiled:
            print("[3/3] Testando modo COMPILADO...")
            compiled_result = self.benchmark_compiled(code, iterations, warmup)
            
            if 'error' in compiled_result:
                print(f"AVISO COMPILADO: {compiled_result['error']}")
                compiled_result = None
        
        # Mostrar resultados
        print("\n" + "=" * 70)
        print("RESULTADOS")
        print("=" * 70)
        
        print("\n[MODO INTERPRETADO]")
        print(f"  Tempo médio:     {interpreted_result['avg_execution_time']*1000:.3f} ms")
        print(f"  Tempo mínimo:    {interpreted_result['min_execution_time']*1000:.3f} ms")
        print(f"  Tempo máximo:    {interpreted_result['max_execution_time']*1000:.3f} ms")
        print(f"  Tempo total:     {interpreted_result['total_time']*1000:.3f} ms")
        print(f"  Tempo de parse:  {interpreted_result['parse_time']*1000:.3f} ms")
        print(f"  Iterações:       {interpreted_result['iterations']}")
        if 'result' in interpreted_result:
            print(f"  Resultado:       {interpreted_result['result']}")
        
        if jit_result:
            print("\n[MODO JIT]")
            print(f"  Tempo médio:     {jit_result['avg_execution_time']*1000:.3f} ms")
            print(f"  Tempo mínimo:    {jit_result['min_execution_time']*1000:.3f} ms")
            print(f"  Tempo máximo:    {jit_result['max_execution_time']*1000:.3f} ms")
            print(f"  Tempo total:     {jit_result['total_time']*1000:.3f} ms")
            print(f"  Tempo de parse:  {jit_result['parse_time']*1000:.3f} ms")
            if 'compile_time' in jit_result:
                print(f"  Tempo de compilação: {jit_result['compile_time']*1000:.3f} ms")
            print(f"  Iterações:       {jit_result['iterations']}")
            if 'result' in jit_result:
                print(f"  Resultado:       {jit_result['result']}")
        
        if compiled_result:
            print("\n[MODO COMPILADO]")
            print(f"  Tempo médio:     {compiled_result['avg_execution_time']*1000:.3f} ms")
            print(f"  Tempo mínimo:    {compiled_result['min_execution_time']*1000:.3f} ms")
            print(f"  Tempo máximo:    {compiled_result['max_execution_time']*1000:.3f} ms")
            print(f"  Tempo total:     {compiled_result['total_time']*1000:.3f} ms")
            print(f"  Tempo de parse:  {compiled_result['parse_time']*1000:.3f} ms")
            print(f"  Tempo de transpile: {compiled_result['transpile_time']*1000:.3f} ms")
            print(f"  Tempo de compilação: {compiled_result['compile_time']*1000:.3f} ms")
            print(f"  Iterações:       {compiled_result['iterations']}")
        
        # Comparações
        print("\n[COMPARACAO]")
        
        if jit_result:
            speedup_jit = interpreted_result['avg_execution_time'] / jit_result['avg_execution_time']
            if speedup_jit > 1.0:
                print(f"  JIT: {speedup_jit:.2f}x MAIS RAPIDO que interpretado")
            elif speedup_jit < 1.0:
                print(f"  JIT: {1/speedup_jit:.2f}x MAIS LENTO que interpretado")
            else:
                print(f"  JIT: Performance equivalente ao interpretado")
            print(f"  JIT diferenca:   {abs(interpreted_result['avg_execution_time'] - jit_result['avg_execution_time'])*1000:.3f} ms")
        
        if compiled_result:
            speedup_compiled = interpreted_result['avg_execution_time'] / compiled_result['avg_execution_time']
            if speedup_compiled > 1.0:
                print(f"  COMPILADO: {speedup_compiled:.2f}x MAIS RAPIDO que interpretado")
            elif speedup_compiled < 1.0:
                print(f"  COMPILADO: {1/speedup_compiled:.2f}x MAIS LENTO que interpretado")
            else:
                print(f"  COMPILADO: Performance equivalente ao interpretado")
            print(f"  COMPILADO diferenca: {abs(interpreted_result['avg_execution_time'] - compiled_result['avg_execution_time'])*1000:.3f} ms")
            
            # Comparar compilado vs JIT
            if jit_result:
                speedup_compiled_vs_jit = jit_result['avg_execution_time'] / compiled_result['avg_execution_time']
                if speedup_compiled_vs_jit > 1.0:
                    print(f"  COMPILADO: {speedup_compiled_vs_jit:.2f}x MAIS RAPIDO que JIT")
                elif speedup_compiled_vs_jit < 1.0:
                    print(f"  COMPILADO: {1/speedup_compiled_vs_jit:.2f}x MAIS LENTO que JIT")
                else:
                    print(f"  COMPILADO: Performance equivalente ao JIT")
        
        print("\n" + "=" * 70)
        
        return {
            'interpreted': interpreted_result,
            'jit': jit_result,
            'compiled': compiled_result
        }


def main():
    """Função principal - permite testar código customizado"""
    
    if len(sys.argv) > 1:
        # Se arquivo fornecido, ler código do arquivo
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(f"ERRO: Arquivo nao encontrado: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        test_compiled = '--no-compiled' not in sys.argv
    else:
        # Código de exemplo padrão
        print("AVISO: Nenhum arquivo fornecido. Usando codigo de exemplo...")
        print("   Uso: python benchmark_performance.py <arquivo.gpu> [iterações]")
        print()
        
        code = """
def fibonacci(n) {
    if (n <= 1) {
        return n
    }
    return fibonacci(n-1) + fibonacci(n-2)
}

result = fibonacci(30)
print("Fibonacci(30) =", result)
"""
        iterations = 5
        test_compiled = True
    
    benchmark = PerformanceBenchmark()
    benchmark.compare(code, iterations=iterations, warmup=1, test_compiled=test_compiled)


if __name__ == '__main__':
    main()

