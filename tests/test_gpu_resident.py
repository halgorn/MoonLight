"""
MoonLight Test Suite: GPU-Resident Data
Tests for Phase 2 Week 5 - Permanent GPU Memory
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parser
from transpiler import gerar_codigo_cpp
from lexer import lexer


class TestGPUResidentSyntax:
    """Test GPU-resident syntax parsing"""
    
    def test_gpu_resident_declaration(self):
        """Test parsing of gpu_resident declaration"""
        code = """
gpu_resident d_array = device[1000]
"""
        ast = parser.parse(code)
        assert ast is not None
        assert len(ast) > 0
        assert ast[0][0] == 'gpu_resident_alloc'
        assert ast[0][1] == 'd_array'
        assert ast[0][2] is not None
    
    def test_gpu_resident_with_expression(self):
        """Test gpu_resident with expression size"""
        code = """
size = 1000
gpu_resident d_data = device[size * 2]
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_multiple_gpu_resident(self):
        """Test multiple gpu_resident declarations"""
        code = """
gpu_resident d_array1 = device[1000]
gpu_resident d_array2 = device[2000]
gpu_resident d_array3 = device[3000]
"""
        ast = parser.parse(code)
        assert ast is not None
        assert len(ast) == 3
        for stmt in ast:
            assert stmt[0] == 'gpu_resident_alloc'


class TestGPUResidentTranspilation:
    """Test transpilation of GPU-resident code"""
    
    def test_gpu_resident_code_generation(self):
        """Test that gpu_resident generates correct C++"""
        code = """
gpu_resident d_model = device[1000000]
"""
        ast = parser.parse(code)
        assert ast is not None
        
        cpp_code = gerar_codigo_cpp(ast)
        assert cpp_code is not None
        assert 'cudaMalloc' in cpp_code
        assert 'd_model' in cpp_code
        assert 'GPU-resident' in cpp_code or 'persists' in cpp_code.lower()
    
    def test_gpu_resident_persistence_comment(self):
        """Test that persistence comment is generated"""
        code = """
gpu_resident d_cache = device[5000]
"""
        ast = parser.parse(code)
        cpp_code = gerar_codigo_cpp(ast)
        
        # Should have comment about persistence
        assert 'persist' in cpp_code.lower() or 'resident' in cpp_code.lower()


class TestGPUResidentUseCases:
    """Test GPU-resident use case patterns"""
    
    def test_ml_model_pattern(self):
        """Test ML model cache pattern"""
        code = """
gpu_resident d_model_weights = device[50000000]
gpu_resident d_input_cache = device[1000000]
gpu_resident d_output_cache = device[100000]

def inference() {
    # Use GPU-resident data
    # No transfer needed!
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_persistent_state_pattern(self):
        """Test persistent state pattern"""
        code = """
gpu_resident d_state = device[1000000]
gpu_resident d_accumulator = device[1000]

def update_state() {
    # Update GPU-resident state
    # Persists across calls
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_multiple_functions_using_resident(self):
        """Test multiple functions using same GPU-resident data"""
        code = """
gpu_resident d_shared = device[10000]

def function1() {
    # Use d_shared
}

def function2() {
    # Use same d_shared
}

def function3() {
    # Use same d_shared
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestGPUResidentExamples:
    """Test that GPU-resident examples exist and parse"""
    
    def test_basic_resident_data_example(self):
        """Verify basic_resident_data.gpu exists and parses"""
        example_path = 'examples/gpu_resident/basic_resident_data.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_ml_model_cache_example(self):
        """Verify ml_model_cache.gpu exists and parses"""
        example_path = 'examples/gpu_resident/ml_model_cache.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_persistent_state_example(self):
        """Verify persistent_state.gpu exists and parses"""
        example_path = 'examples/gpu_resident/persistent_state.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None


class TestGPUResidentIntegration:
    """Integration tests for GPU-resident features"""
    
    def test_gpu_resident_with_kernels(self):
        """Test GPU-resident data used in kernels"""
        code = """
gpu_resident d_data = device[1000]

cuda kernel def process(data, n) {
    tid = threadIdx_x + blockIdx_x * blockDim_x
    if (tid < n) {
        data[tid] = data[tid] * 2
    }
}

def main() {
    gpu[4, 256] process(d_data, 1000)
}

main()
"""
        ast = parser.parse(code)
        assert ast is not None
        
        cpp_code = gerar_codigo_cpp(ast)
        assert cpp_code is not None
        assert 'd_data' in cpp_code
    
    def test_gpu_resident_with_persistent_kernels(self):
        """Test GPU-resident data with persistent kernels"""
        code = """
gpu_resident d_cache = device[10000]

cuda persistent kernel def worker(queue) {
    while (true) {
        task = dequeue_wait(queue)
        if (task == -1) break
        # Use d_cache (resident on GPU)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestGPUResidentPerformance:
    """Performance-related tests for GPU-resident"""
    
    def test_no_transfer_overhead(self):
        """Verify that GPU-resident eliminates transfers"""
        # This is a documentation test
        # GPU-resident data should not require transfers between calls
        
        code = """
gpu_resident d_model = device[1000000]

def train() {
    # Use d_model - no transfer!
}

def inference() {
    # Use same d_model - no transfer!
}
"""
        ast = parser.parse(code)
        assert ast is not None
        
        # In real implementation, would verify no cudaMemcpy calls
        # between function calls for GPU-resident variables


def run_tests():
    """Run all GPU-resident tests"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_tests()

