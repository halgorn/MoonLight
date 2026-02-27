# Best Practices Guide

## Memory Management

### Use GPU-Resident Data

Keep frequently used data on the GPU:
```moonlight
gpu_resident d_model = device[1000000]
# Model stays on GPU, no transfers
```

### Free All Allocations

Always free allocated memory:
```moonlight
d_data = device[1000]
# Use data
free(d_data)  # Don't forget!
```

### Use Memory Pools

For frequent allocations:
```moonlight
pool = create_gpu_pool(1000000)
ptr = allocate_from_pool(pool, 1024)
# Use ptr
free_to_pool(pool, ptr)
```

## Kernel Design

### Minimize Launch Overhead

Use persistent kernels for continuous work:
```moonlight
cuda persistent kernel def worker(queue) {
    # Runs continuously, no launch overhead
}
```

### Optimize Grid/Block Sizes

Choose sizes for good occupancy:
```moonlight
# Good: 256 threads per block
gpu[blocks, 256] kernel(args)

# Avoid: Very small or very large blocks
```

### Use Streams for Concurrency

```moonlight
stream1 = cuda_stream()
stream2 = cuda_stream()
gpu[blocks, threads, stream=stream1] kernel1(args1)
gpu[blocks, threads, stream=stream2] kernel2(args2)
```

## Performance

### Profile Regularly

Use profiling tools:
```moonlight
# @profile decorator (future)
# Or use nvprof/Nsight
```

### Measure Before Optimizing

Don't optimize blindly - measure first:
```moonlight
# Start timer
gpu[blocks, threads] kernel(args)
# Stop timer
# Compare with baseline
```

### Use Appropriate Features

- **Persistent Kernels**: Continuous workloads
- **Dynamic Parallelism**: Recursive/adaptive algorithms
- **Multi-GPU**: Large datasets
- **Streams**: Concurrent execution

## Code Organization

### Keep Kernels Focused

One kernel, one purpose:
```moonlight
# GOOD: Focused kernel
cuda kernel def process_data(data, n) {
    # Single purpose
}

# BAD: Too many responsibilities
```

### Use Meaningful Names

```moonlight
# GOOD
cuda kernel def matrix_multiply(A, B, C, N)

# BAD
cuda kernel def k1(a, b, c, n)
```

### Document Complex Logic

```moonlight
cuda kernel def complex_algorithm(data, n) {
    # Step 1: Preprocessing
    # Step 2: Main computation
    # Step 3: Post-processing
}
```

## Error Handling

### Check Allocation Success

```moonlight
d_data = device[1000]
if (d_data == nullptr) {
    # Handle error
}
```

### Validate Inputs

```moonlight
cuda kernel def safe_kernel(data, n) {
    if (n <= 0) return
    # Process
}
```

## Multi-GPU

### Enable P2P When Available

```moonlight
if (enable_p2p(0, 1)) {
    # Use P2P transfers
} else {
    # Fallback to CPU-mediated
}
```

### Balance Workload

```moonlight
# Partition data evenly
chunk_size = total_size / num_gpus
for (i = 0; i < num_gpus; i = i + 1) {
    gpu[i] process_chunk(data + i * chunk_size, chunk_size)
}
```

## Debugging

### Use gpu_printf Sparingly

```moonlight
if (debug_flag and tid == 0) {
    gpu_printf("Debug: value = %f\n", value)
}
```

### Use Breakpoints Strategically

```moonlight
if (anomaly_detected) {
    gpu_breakpoint()  # Pause for inspection
}
```

## See Also

- `OPTIMIZATION_GUIDE.md` - Optimization techniques
- `TROUBLESHOOTING.md` - Common issues
- `examples/` - Example code

