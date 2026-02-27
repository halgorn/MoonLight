# MoonLight GPU-First Programming Guide

Complete guide to writing GPU-first programs in MoonLight where computation stays on the GPU.

## Philosophy

Traditional GPU programming:
```
CPU → transfer → GPU → compute → transfer → CPU → transfer → GPU → compute...
```
**Problem**: Transfers are 10-100x slower than compute!

GPU-First programming:
```
CPU → transfer → GPU → compute → compute → compute → compute → transfer → CPU
```
**Solution**: Keep data on GPU, chain operations, minimize transfers!

## Table of Contents

1. [Basic CUDA Syntax](#basic-cuda-syntax)
2. [Memory Management](#memory-management)
3. [Kernel Launches](#kernel-launches)
4. [Built-in Variables](#built-in-variables)
5. [Synchronization](#synchronization)
6. [Atomic Operations](#atomic-operations)
7. [Dynamic Parallelism](#dynamic-parallelism)
8. [GPU-Resident Data](#gpu-resident-data)
9. [Persistent Kernels](#persistent-kernels)
10. [Multi-GPU](#multi-gpu)
11. [Best Practices](#best-practices)
12. [Performance Tips](#performance-tips)

## Basic CUDA Syntax

### Defining a Kernel

```moonlight
cuda kernel def my_kernel(data, n) {
    i = threadIdx_x + blockIdx_x * blockDim_x
    
    if (i < n) {
        data[i] = data[i] * 2
    }
}
```

**Transpiles to:**
```cpp
__global__ void my_kernel(float* data, int n) {
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    
    if (i < n) {
        data[i] = data[i] * 2;
    }
}
```

### Persistent Kernels

For long-running GPU tasks:

```moonlight
cuda persistent kernel def gpu_server(work_queue, results) {
    while (true) {
        task = dequeue(work_queue)
        if (task == STOP_SIGNAL) { break }
        
        result = process(task)
        enqueue(results, result)
    }
}
```

## Memory Management

### Device Allocation

```moonlight
# Allocate on GPU
d_data = device[1000000]  # 1M elements
```

**Transpiles to:**
```cpp
float* d_data;
cudaMalloc(&d_data, 1000000 * sizeof(float));
```

### Shared Memory (within kernel)

```moonlight
cuda kernel def use_shared(data, n) {
    shared_cache = shared[256]
    
    tid = threadIdx_x
    shared_cache[tid] = data[blockIdx_x * blockDim_x + tid]
    
    syncthreads()
    
    # Use shared memory (fast!)
    result = shared_cache[tid] * 2
    data[blockIdx_x * blockDim_x + tid] = result
}
```

### Memory Transfers

```moonlight
# Host to Device
d_data <- h_data

# Device to Host
h_result <- d_result
```

**Transpiles to:**
```cpp
// Host to Device
cudaMemcpy(d_data, h_data, size * sizeof(float), cudaMemcpyHostToDevice);

// Device to Host
cudaMemcpy(h_result, d_result, size * sizeof(float), cudaMemcpyDeviceToHost);
```

### Freeing Memory

```moonlight
free(d_data)
```

## Kernel Launches

### 1D Grid

```moonlight
threads = 256
blocks = (n + threads - 1) / threads

gpu[blocks, threads] my_kernel(d_data, n)
```

### 2D Grid

```moonlight
block_size = 16
grid_size = (N + block_size - 1) / block_size

gpu[(grid_size, grid_size), (block_size, block_size)] matrix_kernel(d_A, d_B, d_C, N)
```

**Transpiles to:**
```cpp
dim3 dimGrid(grid_size, grid_size);
dim3 dimBlock(block_size, block_size);
matrix_kernel<<<dimGrid, dimBlock>>>(d_A, d_B, d_C, N);
cudaDeviceSynchronize();
```

### Multi-GPU Launch

```moonlight
# Launch on specific GPU
gpu[0][blocks, threads] kernel1(d_data1)
gpu[1][blocks, threads] kernel2(d_data2)
```

## Built-in Variables

MoonLight provides clean syntax for CUDA built-in variables:

| MoonLight | CUDA C++ | Description |
|-----------|----------|-------------|
| `threadIdx_x` | `threadIdx.x` | Thread index in block (X) |
| `threadIdx_y` | `threadIdx.y` | Thread index in block (Y) |
| `threadIdx_z` | `threadIdx.z` | Thread index in block (Z) |
| `blockIdx_x` | `blockIdx.x` | Block index in grid (X) |
| `blockIdx_y` | `blockIdx.y` | Block index in grid (Y) |
| `blockIdx_z` | `blockIdx.z` | Block index in grid (Z) |
| `blockDim_x` | `blockDim.x` | Block dimension (X) |
| `blockDim_y` | `blockDim.y` | Block dimension (Y) |
| `blockDim_z` | `blockDim.z` | Block dimension (Z) |
| `gridDim_x` | `gridDim.x` | Grid dimension (X) |
| `gridDim_y` | `gridDim.y` | Grid dimension (Y) |
| `gridDim_z` | `gridDim.z` | Grid dimension (Z) |

**Example:**
```moonlight
cuda kernel def matrix_mult(A, B, C, N) {
    row = blockIdx_y * blockDim_y + threadIdx_y
    col = blockIdx_x * blockDim_x + threadIdx_x
    
    if (row < N and col < N) {
        # Compute...
    }
}
```

## Synchronization

### Thread Synchronization

```moonlight
cuda kernel def reduce_sum(data, output) {
    shared_sum = shared[256]
    
    tid = threadIdx_x
    shared_sum[tid] = data[blockIdx_x * blockDim_x + tid]
    
    # Wait for all threads in block
    syncthreads()
    
    # Reduce in shared memory
    if (tid == 0) {
        total = 0
        for (i = 0; i < blockDim_x; i = i + 1) {
            total = total + shared_sum[i]
        }
        output[blockIdx_x] = total
    }
}
```

### Warp Synchronization

```moonlight
cuda kernel def warp_reduce(data) {
    # Synchronize threads in same warp
    syncwarp()
}
```

## Atomic Operations

For thread-safe operations:

```moonlight
cuda kernel def histogram(data, hist, n) {
    i = threadIdx_x + blockIdx_x * blockDim_x
    
    if (i < n) {
        bin = data[i] / 10
        atomic_add(hist[bin], 1)  # Thread-safe increment
    }
}
```

Available atomic operations:
- `atomic_add(addr, val)` - Add
- `atomic_sub(addr, val)` - Subtract
- `atomic_min(addr, val)` - Minimum
- `atomic_max(addr, val)` - Maximum
- `atomic_cas(addr, compare, val)` - Compare-and-swap
- `atomic_exch(addr, val)` - Exchange

## Dynamic Parallelism

Launch kernels FROM kernels (GPU-only):

```moonlight
cuda kernel def parent_kernel(data, n) {
    i = threadIdx_x + blockIdx_x * blockDim_x
    
    if (i < n and data[i] > threshold) {
        # Launch child kernel from GPU!
        gpu[1, 256] child_kernel(data, i, n)
    }
}

cuda kernel def child_kernel(data, index, n) {
    # Process subdivision
    j = threadIdx_x
    data[index * 256 + j] = compute_value(j)
}
```

**Use cases:**
- Adaptive mesh refinement
- Tree traversal
- Recursive algorithms
- Dynamic work generation

## GPU-Resident Data

Keep data on GPU across multiple operations:

```moonlight
def gpu_intensive_pipeline() {
    # Allocate once
    d_data = device[1000000]
    d_temp1 = device[1000000]
    d_temp2 = device[1000000]
    d_result = device[1000000]
    
    # Initial transfer
    d_data <- h_data
    
    # ALL computation on GPU!
    gpu[blocks, threads] step1(d_data, d_temp1, n)
    gpu[blocks, threads] step2(d_temp1, d_temp2, n)
    gpu[blocks, threads] step3(d_temp2, d_result, n)
    
    # Final transfer only
    h_result <- d_result
    
    # Cleanup
    free(d_data)
    free(d_temp1)
    free(d_temp2)
    free(d_result)
}
```

**Benefits:**
- 10-100x faster (no transfers between steps)
- Better GPU utilization
- Lower latency

## Persistent Kernels

For streaming/continuous processing:

```moonlight
cuda persistent kernel def stream_processor(input_queue, output_queue) {
    tid = threadIdx_x + blockIdx_x * blockDim_x
    
    while (true) {
        # Get work from queue
        task = dequeue_wait(input_queue, tid)
        
        if (task.type == STOP) { break }
        
        # Process on GPU
        result = process_task(task)
        
        # Put result in queue
        enqueue(output_queue, result, tid)
    }
}

def main() {
    # Setup queues on GPU
    input_q = create_gpu_queue(10000)
    output_q = create_gpu_queue(10000)
    
    # Launch persistent kernel (runs forever)
    gpu[128, 256] stream_processor(input_q, output_q)
    
    # Feed work continuously
    while (has_work) {
        enqueue_from_host(input_q, next_task())
    }
    
    # Signal stop
    enqueue_from_host(input_q, STOP_TASK)
}
```

**Use cases:**
- Real-time processing
- Stream processing
- Event-driven systems
- Low-latency pipelines

## Multi-GPU

Distribute work across multiple GPUs:

```moonlight
def multi_gpu_processing(data, n) {
    gpu_count = get_device_count()
    chunk_size = n / gpu_count
    
    # Allocate on each GPU
    for (i = 0; i < gpu_count; i = i + 1) {
        gpu[i] {
            d_chunk = device[chunk_size]
            d_chunk <- data[i * chunk_size:(i + 1) * chunk_size]
            
            # Process on this GPU
            gpu[blocks, threads] process_chunk(d_chunk, chunk_size)
        }
    }
    
    # Synchronize all GPUs
    sync_all_devices()
}
```

## Best Practices

### 1. Minimize Transfers

❌ **Bad**: Transfer after every operation
```moonlight
gpu[blocks, threads] step1(d_data)
h_temp <- d_data  # Transfer!
d_data <- h_temp  # Transfer!
gpu[blocks, threads] step2(d_data)
```

✅ **Good**: Keep on GPU
```moonlight
gpu[blocks, threads] step1(d_data)
gpu[blocks, threads] step2(d_data)  # No transfers!
```

### 2. Use Shared Memory

❌ **Bad**: Global memory access
```moonlight
cuda kernel def slow_reduce(data) {
    for (i = 0; i < 256; i = i + 1) {
        sum = sum + data[i]  # Slow!
    }
}
```

✅ **Good**: Shared memory
```moonlight
cuda kernel def fast_reduce(data) {
    shared_data = shared[256]
    shared_data[threadIdx_x] = data[threadIdx_x]
    syncthreads()
    
    # Reduce from shared memory (10x faster!)
}
```

### 3. Coalesce Memory Access

Threads in same warp should access consecutive memory.

### 4. Occupancy

Aim for 100% occupancy:
- Use 256 or 512 threads per block
- Minimize register usage
- Limit shared memory

## Performance Tips

### Measure Everything

```moonlight
start = cuda_event_create()
end = cuda_event_create()

cuda_event_record(start)
gpu[blocks, threads] my_kernel(data)
cuda_event_record(end)

cuda_event_synchronize(end)
elapsed = cuda_event_elapsed_time(start, end)
print("Kernel time:", elapsed, "ms")
```

### Profile with nvprof

```bash
nvprof ./my_moonlight_program
```

### Use cuda-memcheck

```bash
cuda-memcheck ./my_moonlight_program
```

### Optimize Block Size

```moonlight
# Try different block sizes
for block_size in [128, 256, 512, 1024]:
    blocks = (n + block_size - 1) / block_size
    gpu[blocks, block_size] kernel(data)
    # Measure and compare
```

## Complete Example: GPU-First Pipeline

```moonlight
cuda kernel def preprocess(input, output, n) {
    i = threadIdx_x + blockIdx_x * blockDim_x
    if (i < n) {
        output[i] = normalize(input[i])
    }
}

cuda kernel def compute(data, result, n) {
    i = threadIdx_x + blockIdx_x * blockDim_x
    if (i < n) {
        result[i] = expensive_function(data[i])
    }
}

cuda kernel def postprocess(data, output, n) {
    i = threadIdx_x + blockIdx_x * blockDim_x
    if (i < n) {
        output[i] = denormalize(data[i])
    }
}

def main() {
    n = 10000000
    
    # Allocate GPU memory
    d_input = device[n]
    d_temp1 = device[n]
    d_temp2 = device[n]
    d_output = device[n]
    
    # Transfer data once
    d_input <- h_input
    
    # Entire pipeline on GPU!
    threads = 256
    blocks = (n + threads - 1) / threads
    
    gpu[blocks, threads] preprocess(d_input, d_temp1, n)
    gpu[blocks, threads] compute(d_temp1, d_temp2, n)
    gpu[blocks, threads] postprocess(d_temp2, d_output, n)
    
    # Transfer result once
    h_output <- d_output
    
    # Cleanup
    free(d_input)
    free(d_temp1)
    free(d_temp2)
    free(d_output)
    
    print("GPU pipeline complete!")
}

main()
```

## Conclusion

GPU-first programming in MoonLight:
- ✅ Clean syntax (vs verbose CUDA C++)
- ✅ Maximum performance (data stays on GPU)
- ✅ Advanced features (dynamic parallelism, persistent kernels)
- ✅ Multi-GPU support
- ✅ Safe abstractions (automatic cleanup, type safety)

**Result**: Python-like ergonomics with C++/CUDA performance! 🚀

