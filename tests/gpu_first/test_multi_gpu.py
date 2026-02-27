"""
MoonLight Test Suite: Multi-GPU
Tests for P2P transfers, load balancing, and multi-GPU operations
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from parser import parser
from transpiler import gerar_codigo_cpp


class TestP2POperations:
    """Test P2P (Peer-to-Peer) operations"""
    
    def test_enable_p2p_syntax(self):
        """Test enable_p2p() syntax"""
        code = """
def test() {
    result = enable_p2p(0, 1)
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_p2p_copy_syntax(self):
        """Test p2p_copy() syntax"""
        code = """
def test() {
    d_data1 = device[1000]
    d_data2 = device[1000]
    p2p_copy(d_data2, d_data1, 1000 * sizeof(float))
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestMultiGPUSyntax:
    """Test multi-GPU syntax"""
    
    def test_gpu_selection_syntax(self):
        """Test GPU selection in kernel launches"""
        code = """
cuda kernel def test_kernel(data, n) {
    tid = threadIdx_x
    if (tid < n) {
        data[tid] = tid
    }
}

def main() {
    d_data0 = device[1000]
    d_data1 = device[1000]
    
    gpu[0][4, 256] test_kernel(d_data0, 1000)
    gpu[1][4, 256] test_kernel(d_data1, 1000)
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_multi_gpu_allocation(self):
        """Test device allocation on specific GPU"""
        code = """
def test() {
    gpu[0] d_data0 = device[1000]
    gpu[1] d_data1 = device[1000]
    gpu[2] d_data2 = device[1000]
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestLoadBalancing:
    """Test load balancing patterns"""
    
    def test_auto_partitioning_pattern(self):
        """Test automatic data partitioning pattern"""
        code = """
def partition_data(total_size, num_gpus) {
    chunk_size = total_size / num_gpus
    chunks = []
    
    for (i = 0; i < num_gpus; i = i + 1) {
        size = chunk_size
        if (i < total_size % num_gpus) {
            size = size + 1
        }
        chunks.append(size)
    }
    
    return chunks
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestMultiGPUExamples:
    """Test that multi-GPU examples exist and parse"""
    
    def test_p2p_transfer_example(self):
        """Verify p2p_transfer.gpu exists and parses"""
        example_path = 'examples/multi_gpu/p2p_transfer.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_auto_balance_example(self):
        """Verify auto_balance.gpu exists and parses"""
        example_path = 'examples/multi_gpu/auto_balance.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_distributed_pipeline_example(self):
        """Verify distributed_pipeline.gpu exists and parses"""
        example_path = 'examples/multi_gpu/distributed_pipeline.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None


class TestMultiGPURuntime:
    """Test multi-GPU runtime support"""
    
    def test_runtime_exists(self):
        """Verify multi_gpu.cu exists"""
        assert os.path.exists('gpu_runtime/multi_gpu.cu')
    
    def test_runtime_functions(self):
        """Verify runtime has key functions"""
        if os.path.exists('gpu_runtime/multi_gpu.cu'):
            with open('gpu_runtime/multi_gpu.cu', 'r') as f:
                content = f.read()
                assert 'enable_p2p' in content.lower() or 'P2P' in content
                assert 'p2p_memcpy' in content.lower() or 'memcpy' in content.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

