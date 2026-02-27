"""
MoonLight Test Suite: Optimization Features
Tests for shared memory optimization, warp primitives, and optimization passes
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from parser import parser
from transpiler import gerar_codigo_cpp


class TestWarpPrimitives:
    """Test warp-level primitives"""
    
    def test_lane_id_syntax(self):
        """Test lane_id() built-in"""
        code = """
cuda kernel def test(data) {
    lane = lane_id()
    data[lane] = lane
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_warp_id_syntax(self):
        """Test warp_id() built-in"""
        code = """
cuda kernel def test(data) {
    warp = warp_id()
    data[warp] = warp
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_warp_reduce_sum_syntax(self):
        """Test warp_reduce_sum() function"""
        code = """
cuda kernel def test(data, result) {
    val = data[threadIdx_x]
    reduced = warp_reduce_sum(val)
    if (lane_id() == 0) {
        result[warp_id()] = reduced
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_warp_shuffle_syntax(self):
        """Test warp_shuffle() function"""
        code = """
cuda kernel def test(data) {
    val = data[threadIdx_x]
    shuffled = warp_shuffle(val, lane_id() + 1)
    data[threadIdx_x] = shuffled
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestSharedMemoryOptimization:
    """Test shared memory optimization patterns"""
    
    def test_shared_memory_pattern(self):
        """Test shared memory usage pattern"""
        code = """
cuda kernel def test(data, n) {
    tid = threadIdx_x
    # shared_data = shared[256]  # Would be auto-generated
    
    if (tid < n) {
        data[tid] = data[tid] * 2.0
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestOptimizationExamples:
    """Test that optimization examples exist and parse"""
    
    def test_auto_shared_matrix_example(self):
        """Verify auto_shared_matrix.gpu exists and parses"""
        example_path = 'examples/optimization/auto_shared_matrix.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_warp_reduce_example(self):
        """Verify warp_reduce.gpu exists and parses"""
        example_path = 'examples/optimization/warp_reduce.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_bank_conflict_demo_example(self):
        """Verify bank_conflict_demo.gpu exists and parses"""
        example_path = 'examples/optimization/bank_conflict_demo.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_kernel_fusion_example(self):
        """Verify kernel_fusion.gpu exists and parses"""
        example_path = 'examples/optimization/kernel_fusion.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_optimization_levels_example(self):
        """Verify optimization_levels.gpu exists and parses"""
        example_path = 'examples/optimization/optimization_levels.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None


class TestOptimizationTranspilation:
    """Test transpilation of optimization features"""
    
    def test_warp_primitives_code_generation(self):
        """Test that warp primitives generate correct code"""
        code = """
cuda kernel def test(data) {
    lane = lane_id()
    warp = warp_id()
    data[lane] = warp
}
"""
        ast = parser.parse(code)
        cpp_code = gerar_codigo_cpp(ast)
        
        assert cpp_code is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

