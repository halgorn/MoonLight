"""
MoonLight Integration Tests: Complete Pipeline
Tests complete end-to-end pipelines using all features
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from parser import parser
from transpiler import gerar_codigo_cpp


class TestCompletePipeline:
    """Test complete pipelines using multiple features"""
    
    def test_persistent_pipeline_with_streams(self):
        """Test persistent kernel with streams"""
        code = """
cuda persistent kernel def worker(queue) {
    stream = cuda_stream()
    
    while (True) {
        task = dequeue_wait(queue)
        if (task == -1) { break }
        
        gpu[4, 256, stream=stream] process_task(task)
        sync_stream(stream)
    }
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_multi_gpu_pipeline(self):
        """Test pipeline using multiple GPUs (host-side allocation and launches)"""
        code = """
def run_pipeline() {
    enable_p2p(0, 1)
    d_data0 = device[1000]
    d_data1 = device[1000]
    gpu[0][4, 256] process_stage1(d_data0, 1000)
    p2p_copy(d_data1, d_data0, 1000 * 4)
    gpu[1][4, 256] process_stage2(d_data1, 1000)
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_dynamic_parallelism_pipeline(self):
        """Test pipeline with dynamic parallelism"""
        code = """
cuda kernel def parent(data, n) {
    if (n > 100) {
        gpu[1, 256] child1(data, n / 2)
        gpu[1, 256] child2(data + n/2, n - n/2)
    } else {
        process(data, n)
    }
}

def run_pipeline() {
    d_data = device[10000]
    gpu[4, 256] parent(d_data, 10000)
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_gpu_resident_pipeline(self):
        """Test pipeline with GPU-resident data"""
        code = """
gpu_resident d_model = device[1000000]

cuda kernel def inference(input, output, n) {
    tid = threadIdx_x + blockIdx_x * blockDim_x
    if (tid < n) {
        output[tid] = process_with_model(input[tid], d_model)
    }
}

def run_pipeline() {
    d_input = device[1000]
    d_output = device[1000]
    gpu[4, 256] inference(d_input, d_output, 1000)
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestProductionExamples:
    """Test that production examples parse correctly"""
    
    def test_video_encoder_example(self):
        """Verify video encoder example parses"""
        example_path = 'examples/production/gpu_video_encoder.gpu'
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                code = f.read()
            ast = parser.parse(code)
            assert ast is not None
    
    def test_ml_server_example(self):
        """Verify ML server example parses"""
        example_path = 'examples/production/gpu_ml_server.gpu'
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                code = f.read()
            ast = parser.parse(code)
            assert ast is not None
    
    def test_physics_engine_example(self):
        """Verify physics engine example parses"""
        example_path = 'examples/production/gpu_physics_engine.gpu'
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                code = f.read()
            ast = parser.parse(code)
            assert ast is not None
    
    def test_database_example(self):
        """Verify database example parses"""
        example_path = 'examples/production/gpu_database.gpu'
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                code = f.read()
            ast = parser.parse(code)
            assert ast is not None
    
    def test_ray_tracer_example(self):
        """Verify ray tracer example parses"""
        example_path = 'examples/production/gpu_ray_tracer.gpu'
        if os.path.exists(example_path):
            with open(example_path, 'r') as f:
                code = f.read()
            ast = parser.parse(code)
            assert ast is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

