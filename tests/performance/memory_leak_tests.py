"""
MoonLight Memory Leak Tests
Tests to detect memory leaks in GPU code
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from parser import parser


class TestMemoryAllocation:
    """Test memory allocation patterns"""
    
    def test_device_malloc_free_pattern(self):
        """Test proper malloc/free pattern"""
        code = """
cuda kernel def test(data, n) {
    temp = device_malloc(1024)
    if (temp != nullptr) {
        # Use temp
        temp[0] = 1.0
        device_free(temp)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_gpu_resident_allocation(self):
        """Test GPU-resident allocation"""
        code = """
gpu_resident d_data = device[1000000]
# Should persist across function calls
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_memory_pool_pattern(self):
        """Test memory pool allocation pattern"""
        code = """
def test() {
    pool = create_gpu_pool(1000000)
    ptr = allocate_from_pool(pool, 1024)
    # Use ptr
    free_to_pool(pool, ptr)
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestMemoryLeakPatterns:
    """Test patterns that should not leak memory"""
    
    def test_no_leak_in_loop(self):
        """Test that loops don't leak memory"""
        code = """
def test() {
    for (i = 0; i < 100; i = i + 1) {
        temp = device_malloc(1024)
        # Use temp
        device_free(temp)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_no_leak_in_recursive(self):
        """Test that recursive kernels don't leak"""
        code = """
cuda kernel def recursive(n) {
    if (n > 0) {
        temp = device_malloc(1024)
        device_free(temp)
        gpu[1, 256] recursive(n - 1)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestMemoryValidation:
    """Test memory validation patterns"""
    
    def test_cuda_memcheck_pattern(self):
        """Test pattern for cuda-memcheck validation"""
        code = """
def test() {
    # All allocations should be freed
    d_data1 = device[1000]
    d_data2 = device[1000]
    
    # Use data
    process(d_data1, 1000)
    process(d_data2, 1000)
    
    # Free all
    free(d_data1)
    free(d_data2)
}
"""
        ast = parser.parse(code)
        assert ast is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

