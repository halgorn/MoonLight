"""
MoonLight Test Suite: CUDA Streams
Tests for multi-stream execution, async launches, and CUDA Graph API
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from parser import parser
from transpiler import gerar_codigo_cpp


class TestStreamCreation:
    """Test CUDA stream creation"""
    
    def test_cuda_stream_syntax(self):
        """Test that cuda_stream() parses correctly"""
        code = """
def test() {
    stream = cuda_stream()
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_multiple_streams(self):
        """Test creating multiple streams"""
        code = """
def test() {
    stream1 = cuda_stream()
    stream2 = cuda_stream()
    stream3 = cuda_stream()
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestStreamLaunches:
    """Test kernel launches with streams"""
    
    def test_stream_parameter_syntax(self):
        """Test stream= parameter in kernel launches"""
        code = """
cuda kernel def test_kernel(data, n) {
    tid = threadIdx_x
    if (tid < n) {
        data[tid] = tid
    }
}

def main() {
    stream = cuda_stream()
    d_data = device[1000]
    gpu[4, 256, stream=stream] test_kernel(d_data, 1000)
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_multiple_stream_launches(self):
        """Test multiple kernels on different streams"""
        code = """
def main() {
    stream1 = cuda_stream()
    stream2 = cuda_stream()
    
    d_data1 = device[1000]
    d_data2 = device[1000]
    
    gpu[4, 256, stream=stream1] kernel1(d_data1, 1000)
    gpu[4, 256, stream=stream2] kernel2(d_data2, 1000)
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestStreamSynchronization:
    """Test stream synchronization"""
    
    def test_sync_stream_syntax(self):
        """Test sync_stream() function"""
        code = """
def test() {
    stream = cuda_stream()
    sync_stream(stream)
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_multiple_stream_sync(self):
        """Test synchronizing multiple streams"""
        code = """
def test() {
    stream1 = cuda_stream()
    stream2 = cuda_stream()
    stream3 = cuda_stream()
    
    sync_stream(stream1)
    sync_stream(stream2)
    sync_stream(stream3)
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestCUDAGraph:
    """Test CUDA Graph API"""
    
    def test_graph_begin_syntax(self):
        """Test cuda_graph_begin() syntax"""
        code = """
def test() {
    graph = cuda_graph_begin()
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_graph_end_syntax(self):
        """Test cuda_graph_end() syntax"""
        code = """
def test() {
    graph = cuda_graph_begin()
    cuda_graph_end()
}
"""
        ast = parser.parse(code)
        assert ast is not None
    
    def test_graph_launch_syntax(self):
        """Test cuda_graph_launch() syntax"""
        code = """
def test() {
    graph = cuda_graph_begin()
    gpu[4, 256] kernel(data, n)
    cuda_graph_end()
    
    cuda_graph_launch(graph)
}
"""
        ast = parser.parse(code)
        assert ast is not None


class TestStreamExamples:
    """Test that stream examples exist and parse"""
    
    def test_multi_stream_example(self):
        """Verify multi_stream.gpu exists and parses"""
        example_path = 'examples/streams/multi_stream.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_async_pipeline_example(self):
        """Verify async_pipeline.gpu exists and parses"""
        example_path = 'examples/streams/async_pipeline.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None
    
    def test_graph_api_example(self):
        """Verify graph_api.gpu exists and parses"""
        example_path = 'examples/streams/graph_api.gpu'
        assert os.path.exists(example_path)
        
        with open(example_path, 'r') as f:
            code = f.read()
        
        ast = parser.parse(code)
        assert ast is not None


class TestStreamTranspilation:
    """Test transpilation of stream code"""
    
    def test_stream_code_generation(self):
        """Test that stream code generates correctly"""
        code = """
def test() {
    stream = cuda_stream()
    sync_stream(stream)
}
"""
        ast = parser.parse(code)
        cpp_code = gerar_codigo_cpp(ast)
        
        assert cpp_code is not None
        # Should contain stream-related code
        assert 'stream' in cpp_code.lower() or 'Stream' in cpp_code


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

