"""Decorator @jit para MoonLight
Compila funções usando LLVM JIT para performance máxima
"""

import time
import functools

try:
    from llvm_backend import LLVM_AVAILABLE, jit_compiler, llvm_codegen
except ImportError:
    LLVM_AVAILABLE = False
    jit_compiler = None
    llvm_codegen = None

# Cache de funções JIT
jit_cache = {}

# Estatísticas
jit_stats = {
    'compilations': 0,
    'cache_hits': 0,
    'total_time_saved': 0.0
}

def jit(func=None, *, optimize=True, cache=True):
    """
    Decorator @jit para compilação JIT de funções MoonLight
    
    Uso:
    @jit
    def fibonacci(n) {
        if (n <= 1) { return n }
        return fibonacci(n-1) + fibonacci(n-2)
    }
    
    @jit(optimize=False)
    def quick_func() {
        return 42
    }
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            func_name = f.__name__
            
            # Se JIT está desabilitado, executa normalmente
            if not LLVM_AVAILABLE:
                return f(*args, **kwargs)
            
            # Verificar cache
            if cache and func_name in jit_cache:
                jit_stats['cache_hits'] += 1
                # Executar versão compilada
                # Por ora, fallback para interpretado
                return f(*args, **kwargs)
            
            # Primeira execução: compilar
            start_compile = time.time()
            
            try:
                # Obter AST da função se disponível
                # Por enquanto, tentar compilar usando llvm_backend
                from llvm_backend import generate_llvm_for_ast, jit_compiler, LLVM_AVAILABLE
                
                if not LLVM_AVAILABLE or jit_compiler is None:
                    # Fallback para interpretador
                    return f(*args, **kwargs)
                
                # Tentar obter AST da função
                # Se a função foi decorada, pode ter AST armazenada
                func_ast = getattr(f, '_moonlight_ast', None)
                
                if func_ast is None:
                    # Não temos AST, usar interpretador
                    return f(*args, **kwargs)
                
                # Gerar LLVM IR
                llvm_ir = generate_llvm_for_ast(func_ast)
                
                if llvm_ir is None:
                    # Falha na geração de IR, usar interpretador
                    return f(*args, **kwargs)
                
                # Compilar função
                func_ptr = jit_compiler.compile_function(llvm_ir, func_name)
                
                if func_ptr is None:
                    # Falha na compilação, usar interpretador
                    return f(*args, **kwargs)
                
                jit_stats['compilations'] += 1
                
                # Adicionar ao cache
                if cache:
                    jit_cache[func_name] = {
                        'compiled': True,
                        'timestamp': start_compile,
                        'func_ptr': func_ptr,
                        'llvm_ir': llvm_ir
                    }
                
                compile_time = time.time() - start_compile
                
                # Executar função compilada
                result = jit_compiler.execute_jit(func_name, *args)
                
                if result is None:
                    # Execução JIT falhou, usar interpretador
                    return f(*args, **kwargs)
                
                return result
                
            except Exception as e:
                print(f"JIT compilation failed for {func_name}: {e}")
                print(f"Falling back to interpreter")
                return f(*args, **kwargs)
        
        # Marcar como função JIT
        wrapper._is_jit = True
        wrapper._jit_func = f
        
        return wrapper
    
    # Permitir uso com e sem parênteses
    if func is None:
        return decorator
    else:
        return decorator(func)

def numba_jit(*args, **kwargs):
    """Compatibilidade com sintaxe Numba"""
    return jit(*args, **kwargs)

def get_jit_stats():
    """Retorna estatísticas de JIT"""
    return jit_stats.copy()

def clear_jit_cache():
    """Limpa cache de funções JIT"""
    jit_cache.clear()
    jit_stats['cache_hits'] = 0
    jit_stats['compilations'] = 0

def print_jit_stats():
    """Imprime estatísticas de JIT"""
    print("=== JIT Statistics ===")
    print(f"Total compilations: {jit_stats['compilations']}")
    print(f"Cache hits: {jit_stats['cache_hits']}")
    if jit_stats['compilations'] > 0:
        hit_rate = (jit_stats['cache_hits'] / 
                   (jit_stats['cache_hits'] + jit_stats['compilations'])) * 100
        print(f"Cache hit rate: {hit_rate:.1f}%")
    print(f"Time saved (estimate): {jit_stats['total_time_saved']:.2f}s")

# Exemplo de uso
if __name__ == "__main__":
    print("=== Teste do decorator @jit ===\n")
    
    @jit
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    @jit(optimize=True)
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n-1)
    
    # Teste
    print("fibonacci(10) =", fibonacci(10))
    print("factorial(5) =", factorial(5))
    
    print("\n")
    print_jit_stats()
    
    if not LLVM_AVAILABLE:
        print("\nNota: LLVM não disponível, funções executadas no interpretador")
        print("Instale llvmlite para JIT real: pip install llvmlite")









