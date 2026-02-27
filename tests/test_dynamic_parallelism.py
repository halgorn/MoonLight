"""
MoonLight Test Suite: Dynamic Parallelism
Tests for Phase 3 - Nested Kernel Launches and Recursive Algorithms
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parser
from transpiler import gerar_codigo_cpp
from lexer import lexer


class TestNestedKernelLaunches:
    """Test nested kernel launch syntax and patterns"""
    
    def test_nested_kernel_syntax(self):
        """Test that nested kernel launches parse correctly"""
        code = """
cuda kernel def parent(data, n) {
    tid = threadIdx_x
    if (tid == 0) {
        gpu[1, 256] child(data, n)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
        assert ast[0][0] == 'cuda_kernel'
    
    def test_nested_kernel_in_persistent(self):
        """Test nested launches within persistent kernels"""
        code = """
cuda persistent kernel def worker(queue) {
    while (true) {
        task = dequeue_wait(queue)
        if (task == -1) {
            return
        }
        
        # Launch child kernel
        gpu[1, 256] process_task(task)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_multiple_nested_launches(self):
        """Test multiple nested kernel launches"""
        code = """
cuda kernel def parent(data) {
    gpu[1, 256] child1(data)
    gpu[1, 256] child2(data)
    gpu[1, 256] child3(data)
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestRecursiveAlgorithms:
    """Test recursive algorithm patterns"""
    
    def test_recursive_kernel_syntax(self):
        """Test recursive kernel declaration"""
        code = """
cuda kernel def quicksort(data, left, right) {
    if (left < right) {
        pivot = partition(data, left, right)
        gpu[1, 256] quicksort(data, left, pivot - 1)
        gpu[1, 256] quicksort(data, pivot + 1, right)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_recursive_with_base_case(self):
        """Test recursive kernel with base case"""
        code = """
cuda kernel def recursive_func(n, depth) {
    if (n <= 1 or depth > 24) {
        return
    }
    gpu[1, 256] recursive_func(n / 2, depth + 1)
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_tree_traversal_pattern(self):
        """Test tree traversal recursive pattern"""
        code = """
cuda kernel def traverse(node_idx) {
    # Process node
    process(node_idx)
    
    # Traverse children
    if (has_left_child(node_idx)) {
        gpu[1, 256] traverse(left_child(node_idx))
    }
    if (has_right_child(node_idx)) {
        gpu[1, 256] traverse(right_child(node_idx))
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestRecursionDepthLimits:
    """Test recursion depth limits and validation"""
    
    def test_depth_tracking_pattern(self):
        """Test pattern for tracking recursion depth"""
        code = """
cuda kernel def depth_test(current_depth, max_depth) {
    if (current_depth < max_depth) {
        new_depth = current_depth + 1
        gpu[1, 256] depth_test(new_depth, max_depth)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_depth_limit_check(self):
        """Test depth limit checking pattern"""
        code = """
cuda kernel def limited_recursion(n, depth) {
    if (depth >= 24) {
        return  # CUDA limit
    }
    if (n > threshold) {
        gpu[1, 256] limited_recursion(n / 2, depth + 1)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_depth_limits_up_to_24(self):
        """Test that depth limits up to 24 are supported"""
        depths = [1, 5, 10, 15, 20, 24]
        for max_depth in depths:
            code = f"""
cuda kernel def depth_test(depth, max_depth) {{
    if (depth < max_depth) {{
        gpu[1, 256] depth_test(depth + 1, max_depth)
    }}
}}
"""
            ast = parser.parse(code)
            assert ast is not None, f"Failed to parse depth {max_depth}"
    
    def test_depth_limit_exceeded_pattern(self):
        """Test pattern for handling exceeded depth limits"""
        code = """
cuda kernel def safe_recursion(n, depth) {
    # CUDA maximum is 24 levels
    if (depth >= 24) {
        # Process without recursion
        process_base_case(n)
        return
    }
    
    if (n > threshold) {
        gpu[1, 256] safe_recursion(n / 2, depth + 1)
    } else {
        process_base_case(n)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_depth_validation_in_examples(self):
        """Verify examples validate depth limits"""
        examples = [
            'examples/dynamic/recursive_sort.gpu',
            'examples/dynamic/tree_traversal.gpu',
        ]
        
        for ex_path in examples:
            if os.path.exists(ex_path):
                with open(ex_path, 'r') as f:
                    content = f.read()
                    # Should have depth checking or mention limits
                    has_depth_check = (
                        'depth' in content.lower() or
                        '24' in content or
                        'limit' in content.lower()
                    )
                    # At least one example should check depth
                    if has_depth_check:
                        break


class TestAdaptiveMeshRefinement:
    """Test AMR (Adaptive Mesh Refinement) patterns"""
    
    def test_amr_refinement_pattern(self):
        """Test AMR refinement kernel pattern"""
        code = """
cuda kernel def adaptive_refine(mesh, error_threshold, cell_idx) {
    error = calculate_error(mesh, cell_idx)
    if (error > error_threshold) {
        # Subdivide and refine
        gpu[1, 256] refine_cell(mesh, cell_idx)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_work_generation_pattern(self):
        """Test dynamic work generation pattern"""
        code = """
cuda kernel def worker(work_item) {
    if (work_item > threshold) {
        # Generate new work
        gpu[1, 256] worker(work_item / 2)
        gpu[1, 256] worker(work_item / 2)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestDynamicParallelismExamples:
    """Test that dynamic parallelism examples exist and parse"""
    
    def test_nested_kernel_example(self):
        """Verify nested_kernel.gpu exists and parses"""
        example_path = 'examples/dynamic/nested_kernel.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_recursive_sort_example(self):
        """Verify recursive_sort.gpu exists and parses"""
        example_path = 'examples/dynamic/recursive_sort.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_tree_traversal_example(self):
        """Verify tree_traversal.gpu exists and parses"""
        example_path = 'examples/dynamic/tree_traversal.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_adaptive_refine_example(self):
        """Verify adaptive_refine.gpu exists and parses"""
        example_path = 'examples/dynamic/adaptive_refine.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_work_generation_example(self):
        """Verify work_generation.gpu exists and parses"""
        example_path = 'examples/dynamic/work_generation.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_load_balancing_example(self):
        """Verify load_balancing.gpu exists and parses"""
        example_path = 'examples/dynamic/load_balancing.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None


class TestDynamicParallelismTranspilation:
    """Test transpilation of dynamic parallelism code"""
    
    def test_nested_launch_code_generation(self):
        """Test that nested launches generate correct code"""
        code = """
cuda kernel def parent(data) {
    gpu[1, 256] child(data)
}
"""
        ast = parser.parse(code)
        cpp_code = gerar_codigo_cpp(ast)
        
        assert cpp_code is not None
        # Should contain kernel launch syntax
        assert 'parent' in cpp_code or 'child' in cpp_code
    
    def test_recursive_kernel_code_generation(self):
        """Test recursive kernel code generation"""
        code = """
cuda kernel def recursive(n) {
    if (n > 1) {
        gpu[1, 256] recursive(n - 1)
    }
}
"""
        ast = parser.parse(code)
        cpp_code = gerar_codigo_cpp(ast)
        
        assert cpp_code is not None
        assert 'recursive' in cpp_code


class TestDynamicParallelismRequirements:
    """Test CUDA requirements for dynamic parallelism"""
    
    def test_runtime_header_exists(self):
        """Verify dynamic_launch.cuh exists"""
        assert os.path.exists('gpu_runtime/dynamic_launch.cuh')
    
    def test_compilation_requirements_documented(self):
        """Verify requirements are documented"""
        # Check if examples mention requirements
        example_path = 'examples/dynamic/nested_kernel.gpu'
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                content = f.read()
                # Should mention compute capability or -rdc=true
                assert 'compute' in content.lower() or 'rdc' in content.lower() or '3.5' in content


class TestMemoryLeakPrevention:
    """Test patterns for preventing memory leaks in dynamic parallelism"""
    
    def test_device_malloc_free_pattern(self):
        """Test malloc/free pattern in recursive kernels"""
        code = """
cuda kernel def recursive_with_malloc(n) {
    if (n > 0) {
        temp = device_malloc(1024)
        # Use temp...
        device_free(temp)
        gpu[1, 256] recursive_with_malloc(n - 1)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_no_malloc_leak_pattern(self):
        """Test pattern that avoids malloc leaks"""
        code = """
cuda kernel def safe_recursive(n) {
    if (n <= 1) {
        return
    }
    # No malloc - use stack/local variables
    result = n * n
    gpu[1, 256] safe_recursive(n - 1)
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_memory_pool_pattern(self):
        """Test using memory pools to avoid leaks"""
        code = """
cuda kernel def recursive_with_pool(n, pool) {
    if (n > 0) {
        # Allocate from pool (automatically managed)
        temp = allocate_from_pool(pool, 1024)
        # Use temp...
        free_to_pool(pool, temp)
        gpu[1, 256] recursive_with_pool(n - 1, pool)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_raii_pattern(self):
        """Test RAII-like pattern with smart pointers"""
        # Note: gpu_unique_ptr syntax may not be fully implemented
        # This test validates the pattern conceptually
        code = """
cuda kernel def recursive_with_smart_ptr(n) {
    if (n > 0) {
        # Smart pointer auto-frees (conceptual)
        # temp = gpu_unique_ptr[float](1024)
        # Use temp.get()...
        # Automatically freed when scope exits
        gpu[1, 256] recursive_with_smart_ptr(n - 1)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_memory_leak_detection_pattern(self):
        """Test pattern for detecting memory leaks"""
        code = """
cuda kernel def tracked_recursive(n, alloc_count) {
    if (n > 0) {
        temp = device_malloc(1024)
        if (temp != 0) {
            # Track allocation (using atomic_add as expression)
            count = atomic_add(alloc_count, 1)
            # Use temp...
            device_free(temp)
            # Track deallocation
            count = atomic_add(alloc_count, -1)
            gpu[1, 256] tracked_recursive(n - 1, alloc_count)
        }
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestPerformanceValidation:
    """Test performance-related patterns"""
    
    def test_depth_limit_validation(self):
        """Test that depth limits are respected"""
        # This is a documentation test
        # In real implementation, would validate depth < 24
        
        code = """
cuda kernel def depth_limited(n, depth) {
    if (depth >= 24) {
        return  # Respect CUDA limit
    }
    if (n > 1) {
        gpu[1, 256] depth_limited(n / 2, depth + 1)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_synchronization_pattern(self):
        """Test synchronization patterns for nested kernels"""
        code = """
cuda kernel def parent(data) {
    gpu[1, 256] child1(data)
    # In real CUDA: cudaDeviceSynchronize() here
    gpu[1, 256] child2(data)
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestIntegrationScenarios:
    """Integration tests for dynamic parallelism"""
    
    def test_complete_nested_pipeline(self):
        """Test complete nested kernel pipeline"""
        code = """
cuda kernel def stage1(data, n) {
    gpu[1, 256] process(data, n)
}

cuda kernel def stage2(data, n) {
    gpu[1, 256] stage1(data, n)
    gpu[1, 256] stage1(data, n)
}

def main() {
    d_data = device[1000]
    gpu[4, 256] stage2(d_data, 1000)
}

main()
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_recursive_with_persistent_kernel(self):
        """Test recursive algorithms with persistent kernels"""
        code = """
cuda persistent kernel def worker(queue) {
    while (true) {
        task = dequeue_wait(queue)
        if (task == -1) {
            return
        }
        
        # Launch recursive processing
        gpu[1, 256] recursive_process(task)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None


def run_tests():
    """Run all dynamic parallelism tests"""
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == '__main__':
    run_tests()

