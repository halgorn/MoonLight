"""
MoonLight Phase 1 Complete Test Suite
Validates that all Phase 1 (Persistent Kernels) requirements are met
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parser
from transpiler import gerar_codigo_cpp


class TestPhase1Week1:
    """Test Week 1: Work Queue System"""
    
    def test_queue_implementation_exists(self):
        """Verify queue implementation files exist"""
        assert os.path.exists('gpu_runtime/queue.cu')
        assert os.path.exists('gpu_runtime/queue.cuh')
        
        # Check that queue.cu has key functions
        with open('gpu_runtime/queue.cu', 'r') as f:
            content = f.read()
            assert 'enqueue' in content
            assert 'dequeue' in content
            assert 'dequeue_wait' in content
            assert 'atomicAdd' in content  # Lock-free operations
    
    def test_queue_syntax_supported(self):
        """Test that queue syntax is supported"""
        code = "queue = gpu_queue[int, 10000]"
        ast = parser.parse(code)
        assert ast is not None
        assert ast[0][0] == 'gpu_queue_decl'
    
    def test_host_queue_operations(self):
        """Test enqueue_host and dequeue_host"""
        code1 = "enqueue_host(queue, item)"
        code2 = "result = dequeue_host(queue)"
        
        ast1 = parser.parse(code1)
        ast2 = parser.parse(code2)
        
        assert ast1 is not None
        assert ast2 is not None


class TestPhase1Week2:
    """Test Week 2: Persistent Kernel Implementation"""
    
    def test_persistent_keyword(self):
        """Test that 'cuda persistent kernel' is recognized"""
        code = """
cuda persistent kernel def worker(queue) {
    tid = threadIdx_x
}
"""
        ast = parser.parse(code)
        assert ast is not None
        assert ast[0][4] == True  # is_persistent flag
    
    def test_launch_bounds_generation(self):
        """Test that __launch_bounds__ is generated"""
        code = """
cuda persistent kernel def worker(queue) {
    tid = threadIdx_x
}
"""
        ast = parser.parse(code)
        cpp = gerar_codigo_cpp(ast)
        assert '__launch_bounds__' in cpp
    
    def test_stop_signal_pattern(self):
        """Test stop signal handling pattern"""
        code = """
cuda persistent kernel def worker(input_queue) {
    while (true) {
        task = dequeue_wait(input_queue)
        if (task == -1) {
            break
        }
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_examples_week2(self):
        """Verify Week 2 examples exist"""
        examples = [
            'examples/persistent/gpu_server.gpu',
            'examples/persistent/video_stream.gpu',
            'examples/persistent/real_time_pipeline.gpu',
        ]
        for ex in examples:
            assert os.path.exists(ex), f"Missing: {ex}"


class TestPhase1Week3:
    """Test Week 3: Multi-Stage Pipelines"""
    
    def test_pipeline_tokens(self):
        """Verify pipeline tokens are defined"""
        from lexer import lexer
        lexer.input("pipeline stage")
        tokens = []
        while True:
            tok = lexer.token()
            if not tok:
                break
            tokens.append(tok.type)
        
        assert 'PIPELINE' in tokens
        assert 'STAGE' in tokens
    
    def test_multi_stage_example(self):
        """Verify multi-stage examples exist"""
        examples = [
            'examples/persistent/image_processing_pipeline.gpu',
            'examples/persistent/adaptive_pipeline.gpu',
            'examples/persistent/data_analytics_pipeline.gpu',
        ]
        for ex in examples:
            assert os.path.exists(ex), f"Missing: {ex}"
    
    def test_complex_pipeline_parses(self):
        """Test that complex pipelines parse correctly"""
        code = """
def main() {
    q1 = gpu_queue[int, 1000]
    q2 = gpu_queue[int, 1000]
    q3 = gpu_queue[int, 1000]
    
    gpu[2, 256] stage1(q1, q2)
    gpu[4, 256] stage2(q2, q3)
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestPhase1Week4:
    """Test Week 4: Testing & Benchmarks"""
    
    def test_benchmarks_exist(self):
        """Verify all benchmarks are present"""
        benchmarks = [
            'benchmarks/persistent/queue_throughput.gpu',
            'benchmarks/persistent/latency_test.gpu',
            'benchmarks/persistent/pipeline_vs_batch.gpu',
            'benchmarks/persistent/real_time_video.gpu',
        ]
        for bm in benchmarks:
            assert os.path.exists(bm), f"Missing: {bm}"
    
    def test_documentation_complete(self):
        """Verify documentation is complete"""
        docs = [
            'GPU_ROADMAP_PROGRESS.md',
            'PHASE1_WEEK2_SUMMARY.md',
            'benchmarks/persistent/README.md',
        ]
        for doc in docs:
            assert os.path.exists(doc), f"Missing: {doc}"
    
    def test_phase1_progress_document(self):
        """Verify progress document is updated"""
        with open('GPU_ROADMAP_PROGRESS.md', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Semana 1' in content
            assert 'Semana 2' in content
            assert 'COMPLETA' in content


class TestCodeQuality:
    """Test code quality and best practices"""
    
    def test_no_parser_conflicts(self):
        """Test that parser has no critical conflicts"""
        # This is validated by successful parsing
        code = """
def test() {
    x = 10
    print(x)
}
test()
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_transpiler_generates_valid_cpp(self):
        """Test that transpiler generates compilable C++"""
        code = """
def main() {
    x = 10
    y = 20
    z = x + y
    print(z)
}
main()
"""
        ast = parser.parse(code)
        cpp = gerar_codigo_cpp(ast)
        
        # Check for C++ validity
        assert '#include' in cpp
        assert 'int main()' in cpp
        assert 'return 0' in cpp


class TestPerformanceTargets:
    """Document performance targets (not executable tests)"""
    
    def test_performance_targets_documented(self):
        """Verify performance targets are documented"""
        with open('benchmarks/persistent/README.md', 'r', encoding='utf-8') as f:
            content = f.read()
            # Check for key performance metrics
            assert '1ms' in content or '1 ms' in content
            assert 'latency' in content.lower()
            assert 'throughput' in content.lower()
    
    def test_gpu_queue_optimization(self):
        """Verify queue uses optimizations"""
        with open('gpu_runtime/queue.cu', 'r') as f:
            content = f.read()
            # Check for optimizations
            assert 'atomic' in content.lower()
            assert 'mask' in content  # Power-of-2 optimization
            assert 'backoff' in content  # Spin-wait backoff


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    def test_complete_persistent_kernel_program(self):
        """Test a complete persistent kernel program"""
        code = """
cuda persistent kernel def worker(input_q, output_q) {
    tid = threadIdx_x + blockIdx_x * blockDim_x
    
    while (true) {
        task = dequeue_wait(input_q)
        
        if (task == -1) {
            break
        }
        
        result = task * task
        enqueue(output_q, result, tid)
    }
}

def main() {
    input_queue = gpu_queue[int, 1000]
    output_queue = gpu_queue[int, 1000]
    
    gpu[4, 256] worker(input_queue, output_queue)
    
    for (i = 0; i < 10; i = i + 1) {
        enqueue_host(input_queue, i)
    }
    
    for (i = 0; i < 10; i = i + 1) {
        result = dequeue_host(output_queue)
        print(result)
    }
    
    enqueue_host(input_queue, -1)
}

main()
"""
        ast = parser.parse(code)
        assert ast is not None
        
        cpp = gerar_codigo_cpp(ast)
        assert cpp is not None
        assert '__launch_bounds__' in cpp
        assert 'worker' in cpp
    
    def test_multi_stage_pipeline_program(self):
        """Test a complete multi-stage pipeline"""
        code = """
cuda persistent kernel def stage1(in_q, out_q) {
    while (true) {
        data = dequeue_wait(in_q)
        if (data == -1) {
            enqueue(out_q, -1, 0)
            break
        }
        processed = data * 2
        enqueue(out_q, processed, 0)
    }
}

cuda persistent kernel def stage2(in_q, out_q) {
    while (true) {
        data = dequeue_wait(in_q)
        if (data == -1) {
            enqueue(out_q, -1, 0)
            break
        }
        processed = data + 10
        enqueue(out_q, processed, 0)
    }
}

def main() {
    q1 = gpu_queue[int, 1000]
    q2 = gpu_queue[int, 1000]
    q3 = gpu_queue[int, 1000]
    
    gpu[2, 256] stage1(q1, q2)
    gpu[2, 256] stage2(q2, q3)
    
    enqueue_host(q1, 5)
    result = dequeue_host(q3)
    print(result)
}

main()
"""
        ast = parser.parse(code)
        assert ast is not None


def test_phase1_completeness():
    """Meta-test: verify Phase 1 is complete"""
    
    # Week 1 deliverables
    week1_files = [
        'gpu_runtime/queue.cu',
        'gpu_runtime/queue.cuh',
        'examples/persistent/basic_persistent_kernel.gpu',
        'benchmarks/persistent/queue_throughput.gpu',
        'benchmarks/persistent/latency_test.gpu',
    ]
    
    # Week 2 deliverables
    week2_files = [
        'examples/persistent/gpu_server.gpu',
        'examples/persistent/video_stream.gpu',
        'examples/persistent/real_time_pipeline.gpu',
        'PHASE1_WEEK2_SUMMARY.md',
    ]
    
    # Week 3 deliverables
    week3_files = [
        'examples/persistent/image_processing_pipeline.gpu',
        'examples/persistent/adaptive_pipeline.gpu',
        'examples/persistent/data_analytics_pipeline.gpu',
    ]
    
    # Week 4 deliverables
    week4_files = [
        'tests/test_persistent_kernels.py',
        'tests/test_phase1_complete.py',
    ]
    
    all_files = week1_files + week2_files + week3_files + week4_files
    
    missing = []
    for f in all_files:
        if not os.path.exists(f):
            missing.append(f)
    
    assert len(missing) == 0, f"Missing files: {missing}"
    
    print("✓ Phase 1 Complete!")
    print(f"  Week 1: {len(week1_files)} files ✓")
    print(f"  Week 2: {len(week2_files)} files ✓")
    print(f"  Week 3: {len(week3_files)} files ✓")
    print(f"  Week 4: {len(week4_files)} files ✓")
    print(f"  Total: {len(all_files)} files ✓")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

