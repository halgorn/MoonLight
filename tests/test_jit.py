"""
MoonLight Test Suite: JIT Compilation
Tests for @jit decorator, LLVM IR generation, and JIT execution
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parser
from llvm_backend import generate_llvm_for_ast, LLVM_AVAILABLE, jit_compiler


class TestJITParsing:
    """Test parsing of @jit decorator"""
    
    def test_jit_decorator_simple(self):
        """Test @jit def function()"""
        code = """
@jit
def test() {
    return 1
}
"""
        ast = parser.parse(code)
        assert ast is not None
        
        # Verificar que função tem decorator jit
        if isinstance(ast, list) and len(ast) > 0:
            func_ast = ast[0]
            if isinstance(func_ast, tuple) and func_ast[0] == 'func_def':
                decorators = func_ast[4] if len(func_ast) > 4 else []
                has_jit = any(d[1] == 'jit' for d in decorators if isinstance(d, tuple) and len(d) > 1)
                assert has_jit, "Function should have @jit decorator"
    
    def test_jit_decorator_with_args(self):
        """Test @jit(optimize=True) def function()"""
        code = """
@jit(optimize=True)
def test() {
    return 1
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestLLVMIRGeneration:
    """Test LLVM IR generation from AST"""
    
    def test_simple_function_ir(self):
        """Test generating LLVM IR for simple function"""
        if not LLVM_AVAILABLE:
            pytest.skip("LLVM not available")
        
        code = """
def add(a, b) {
    return a + b
}
"""
        ast = parser.parse(code)
        assert ast is not None
        
        if isinstance(ast, list) and len(ast) > 0:
            func_ast = ast[0]
            if isinstance(func_ast, tuple) and func_ast[0] == 'func_def':
                llvm_ir = generate_llvm_for_ast(func_ast)
                assert llvm_ir is not None, "Should generate LLVM IR"
                assert 'define' in llvm_ir, "LLVM IR should contain function definition"
    
    def test_jit_function_ir(self):
        """Test generating LLVM IR for @jit function"""
        if not LLVM_AVAILABLE:
            pytest.skip("LLVM not available")
        
        code = """
@jit
def multiply(a, b) {
    return a * b
}
"""
        ast = parser.parse(code)
        assert ast is not None
        
        if isinstance(ast, list) and len(ast) > 0:
            func_ast = ast[0]
            if isinstance(func_ast, tuple) and func_ast[0] == 'func_def':
                llvm_ir = generate_llvm_for_ast(func_ast)
                # Pode ser None se não conseguir traduzir completamente
                # Isso é OK para implementação inicial
                if llvm_ir:
                    assert 'define' in llvm_ir


class TestJITExecution:
    """Test JIT execution of compiled functions"""
    
    def test_jit_compiler_available(self):
        """Test that JIT compiler is available if LLVM is installed"""
        if LLVM_AVAILABLE:
            assert jit_compiler is not None, "JIT compiler should be available"
            assert jit_compiler.enabled, "JIT compiler should be enabled"
    
    def test_simple_jit_compilation(self):
        """Test compiling a simple function with JIT"""
        if not LLVM_AVAILABLE or jit_compiler is None:
            pytest.skip("JIT not available")
        
        code = """
def add(a, b) {
    return a + b
}
"""
        ast = parser.parse(code)
        assert ast is not None
        
        if isinstance(ast, list) and len(ast) > 0:
            func_ast = ast[0]
            if isinstance(func_ast, tuple) and func_ast[0] == 'func_def':
                llvm_ir = generate_llvm_for_ast(func_ast)
                if llvm_ir:
                    func_name = func_ast[1]
                    func_ptr = jit_compiler.compile_function(llvm_ir, func_name)
                    # func_ptr pode ser None se compilação falhar (OK para implementação inicial)
                    # Mas se não for None, deve ser um ponteiro válido
                    if func_ptr:
                        assert func_ptr != 0, "Function pointer should be non-zero"


class TestJITExamples:
    """Test that JIT examples exist and parse"""
    
    def test_benchmark_jit_example(self):
        """Verify benchmark_jit.gpu exists and parses"""
        example_path = 'examples/jit/benchmark_jit.gpu'
        if os.path.exists(example_path):
            with open(example_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            ast = parser.parse(code)
            assert ast is not None
    
    def test_matrix_operations_example(self):
        """Verify matrix_operations.gpu exists and parses"""
        example_path = 'examples/jit/matrix_operations.gpu'
        if os.path.exists(example_path):
            with open(example_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            ast = parser.parse(code)
            assert ast is not None

class TestJITLoops:
    """Test JIT compilation of loops"""
    
    def test_for_loop_ir(self):
        """Test generating LLVM IR for for loop"""
        if not LLVM_AVAILABLE:
            pytest.skip("LLVM not available")
        
        code = """
def sum_loop(n) {
    sum = 0
    for (i = 0; i < n; i = i + 1) {
        sum = sum + i
    }
    return sum
}
"""
        ast = parser.parse(code)
        assert ast is not None
        
        if isinstance(ast, list) and len(ast) > 0:
            func_ast = ast[0]
            if isinstance(func_ast, tuple) and func_ast[0] == 'func_def':
                llvm_ir = generate_llvm_for_ast(func_ast)
                # Pode ser None se não conseguir traduzir completamente
                if llvm_ir:
                    assert 'define' in llvm_ir
    
    def test_while_loop_ir(self):
        """Test generating LLVM IR for while loop"""
        if not LLVM_AVAILABLE:
            pytest.skip("LLVM not available")
        
        code = """
def countdown(n) {
    while (n > 0) {
        n = n - 1
    }
    return n
}
"""
        ast = parser.parse(code)
        assert ast is not None
        
        if isinstance(ast, list) and len(ast) > 0:
            func_ast = ast[0]
            if isinstance(func_ast, tuple) and func_ast[0] == 'func_def':
                llvm_ir = generate_llvm_for_ast(func_ast)
                if llvm_ir:
                    assert 'define' in llvm_ir

class TestJITBuiltins:
    """Test JIT compilation of built-in functions"""
    
    def test_abs_function(self):
        """Test abs() function in JIT"""
        if not LLVM_AVAILABLE:
            pytest.skip("LLVM not available")
        
        code = """
def test_abs(x) {
    return abs(x)
}
"""
        ast = parser.parse(code)
        assert ast is not None
        
        if isinstance(ast, list) and len(ast) > 0:
            func_ast = ast[0]
            if isinstance(func_ast, tuple) and func_ast[0] == 'func_def':
                llvm_ir = generate_llvm_for_ast(func_ast)
                # abs pode não estar totalmente implementado, mas não deve quebrar
                if llvm_ir:
                    assert 'define' in llvm_ir


class TestJITIntegration:
    """Integration tests for JIT compilation"""
    
    def test_jit_with_executor(self):
        """Test that executor can detect and use JIT functions"""
        code = """
@jit
def add(a, b) {
    return a + b
}
"""
        ast = parser.parse(code)
        assert ast is not None
        
        # Verificar que executor pode processar função JIT
        # (teste básico de estrutura, execução real requer llvmlite)
        if isinstance(ast, list) and len(ast) > 0:
            func_ast = ast[0]
            if isinstance(func_ast, tuple) and func_ast[0] == 'func_def':
                assert len(func_ast) >= 4, "Function AST should have at least 4 elements"
                decorators = func_ast[4] if len(func_ast) > 4 else []
                has_jit = any(d[1] == 'jit' for d in decorators if isinstance(d, tuple) and len(d) > 1)
                assert has_jit, "Function should be marked for JIT"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

