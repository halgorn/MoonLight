# Troubleshooting Guide

## Common Issues

### Kernel Launch Fails

**Problem**: Kernel doesn't launch or crashes

**Solutions**:
- Check grid/block dimensions
- Verify memory allocation succeeded
- Check for out-of-bounds access
- Validate input parameters

```moonlight
# Verify allocation
d_data = device[1000]
if (d_data == nullptr) {
    print("Allocation failed!")
    return
}

# Check bounds
cuda kernel def safe_kernel(data, n) {
    tid = threadIdx_x + blockIdx_x * blockDim_x
    if (tid < n) {  # Always check bounds!
        data[tid] = process(tid)
    }
}
```

### Memory Leaks

**Problem**: GPU memory not freed

**Solutions**:
- Always free allocated memory
- Use memory pools for frequent allocations
- Check with cuda-memcheck

```moonlight
# Always pair malloc with free
d_data = device[1000]
# ... use data ...
free(d_data)  # Don't forget!
```

### Poor Performance

**Problem**: Code runs slower than expected

**Solutions**:
- Profile with nvprof/Nsight
- Check GPU utilization
- Verify memory coalescing
- Minimize branches
- Use shared memory when appropriate

```moonlight
# Profile your code
# Use nvprof or Nsight Compute
# Identify bottlenecks
```

### Dynamic Parallelism Not Working

**Problem**: Nested kernel launches fail

**Solutions**:
- Verify compute capability 3.5+
- Compile with `-rdc=true`
- Link with `-lcudadevrt`
- Check recursion depth (max 24)

```moonlight
# Check depth
cuda kernel def recursive(n, depth) {
    if (depth >= 24) {
        return  # CUDA limit
    }
    # ...
}
```

### P2P Transfer Fails

**Problem**: GPU-to-GPU transfer doesn't work

**Solutions**:
- Check P2P capability: `enable_p2p(0, 1)`
- Verify GPUs are compatible
- May need NVLink for best performance
- Fallback to CPU-mediated transfer

```moonlight
if (enable_p2p(0, 1)) {
    p2p_copy(dest, src, size)
} else {
    # Fallback
    # cudaMemcpyPeer(dest, 1, src, 0, size)
}
```

### Stream Synchronization Issues

**Problem**: Results not ready when expected

**Solutions**:
- Always sync streams before using results
- Use `sync_stream()` explicitly
- Check stream dependencies

```moonlight
gpu[blocks, threads, stream=stream1] kernel1(args1)
gpu[blocks, threads, stream=stream2] kernel2(args2)
sync_stream(stream1)  # Wait for stream1
sync_stream(stream2)  # Wait for stream2
```

### Compilation Errors

**Problem**: Code doesn't compile

**Solutions**:
- Check syntax errors
- Verify all functions are defined
- Check for missing imports
- Validate CUDA SDK installation

### Runtime Errors

**Problem**: Program crashes at runtime

**Solutions**:
- Use `gpu_printf()` for debugging
- Check with cuda-gdb
- Validate memory accesses
- Check for null pointers

```moonlight
# Debug output
if (tid == 0) {
    gpu_printf("Debug: n = %d\n", n)
}
```

## Performance Issues

### Low GPU Utilization

**Causes**:
- Small workloads
- Memory-bound operations
- Poor kernel design

**Solutions**:
- Increase workload size
- Optimize memory access
- Use streams for concurrency

### High Launch Overhead

**Causes**:
- Many small kernel launches
- Frequent CPU-GPU synchronization

**Solutions**:
- Use persistent kernels
- Batch operations
- Use CUDA Graph API

### Memory Transfer Bottleneck

**Causes**:
- Frequent CPU-GPU transfers
- Large data transfers

**Solutions**:
- Use GPU-resident data
- Use unified memory
- Overlap transfers with computation

## Getting Help

1. Check this guide
2. Review examples in `examples/`
3. Check benchmarks in `benchmarks/`
4. Review test cases in `tests/`
5. Consult CUDA documentation

## Debugging Tools

- **cuda-gdb**: GPU debugger
- **Nsight Debugger**: Visual debugging
- **nvprof**: Profiler
- **Nsight Compute**: Detailed analysis
- **cuda-memcheck**: Memory error detection

## See Also

- `BEST_PRACTICES.md` - Best practices
- `OPTIMIZATION_GUIDE.md` - Optimization techniques
- `GPU_FIRST_COMPLETE.md` - Complete guide

