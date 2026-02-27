# MoonLight: Complete GPU-First Language Guide

## Overview

MoonLight is a programming language designed from the ground up for GPU computing. It provides a GPU-first approach where computation stays on the GPU, minimizing CPU-GPU transfers and maximizing performance.

## Key Features

### 1. Persistent Kernels
Kernels that run continuously, waiting for work:
```moonlight
cuda persistent kernel def worker(queue) {
    while (true) {
        task = dequeue_wait(queue)
        if (task == -1) break
        process(task)
    }
}
```

### 2. GPU-Resident Data
Data that persists on the GPU across function calls:
```moonlight
gpu_resident d_model = device[1000000]
# Model stays on GPU, no transfers needed
```

### 3. Dynamic Parallelism
Kernels launching other kernels:
```moonlight
cuda kernel def parent(data, n) {
    if (n > 100) {
        gpu[1, 256] child(data, n / 2)
    }
}
```

### 4. Multi-Stream Execution
Concurrent kernel execution:
```moonlight
stream1 = cuda_stream()
stream2 = cuda_stream()
gpu[4, 256, stream=stream1] kernel1(data1)
gpu[4, 256, stream=stream2] kernel2(data2)
```

### 5. Multi-GPU Support
Automatic load balancing and P2P transfers:
```moonlight
enable_p2p(0, 1)
gpu[0] d_data0 = device[1000]
gpu[1] d_data1 = device[1000]
p2p_copy(d_data1, d_data0, 1000 * sizeof(float))
```

## Language Syntax

### Kernel Definition
```moonlight
cuda kernel def kernel_name(params) {
    # Kernel code
}
```

### Persistent Kernels
```moonlight
cuda persistent kernel def worker(queue) {
    # Runs continuously
}
```

### Memory Allocation
```moonlight
# Device memory
d_data = device[size]

# GPU-resident (persists)
gpu_resident d_model = device[size]

# Unified memory
unified_data = unified memory[size]

# Pinned memory
pinned_data = pinned memory[size]
```

### Kernel Launch
```moonlight
# 1D launch
gpu[blocks, threads] kernel(args)

# 2D launch
gpu[(bx, by), (tx, ty)] kernel(args)

# With stream
gpu[blocks, threads, stream=stream] kernel(args)

# On specific GPU
gpu[device_id][blocks, threads] kernel(args)
```

## Performance Features

### Warp Primitives
```moonlight
lane = lane_id()      # Thread ID within warp
warp = warp_id()      # Warp ID within block
reduced = warp_reduce_sum(value)
shuffled = warp_shuffle(value, src_lane)
```

### Shared Memory
```moonlight
# Shared memory (auto-optimized)
# tile = shared[16][16]
```

### Optimization Levels
```moonlight
# @optimize(level=3) enables maximum optimizations
# - Kernel fusion
# - Register optimization
# - Memory coalescing
```

## Best Practices

1. **Use Persistent Kernels** for continuous workloads
2. **Keep Data GPU-Resident** to avoid transfers
3. **Use Streams** for concurrent execution
4. **Enable P2P** for multi-GPU setups
5. **Profile Regularly** to identify bottlenecks

## Examples

See `examples/` directory for complete examples:
- `persistent/` - Persistent kernel examples
- `gpu_resident/` - GPU-resident data examples
- `dynamic/` - Dynamic parallelism examples
- `streams/` - Multi-stream examples
- `multi_gpu/` - Multi-GPU examples
- `production/` - Production-ready examples

## Performance Targets

- Kernel launch overhead: <1μs
- Enqueue latency: <100ns
- GPU utilization: >95%
- Multi-GPU scaling: >90%

## Requirements

- CUDA Toolkit 11.0+
- Compute capability 3.5+ (for dynamic parallelism)
- NVIDIA GPU

## Getting Started

1. Write your `.gpu` file
2. Compile: `python moonc.py your_file.gpu`
3. Run the generated executable

For more details, see the specific guides:
- `PERSISTENT_KERNELS.md` - Persistent kernels guide
- `DYNAMIC_PARALLELISM.md` - Dynamic parallelism guide
- `OPTIMIZATION_GUIDE.md` - Optimization techniques
- `BEST_PRACTICES.md` - Best practices
- `TROUBLESHOOTING.md` - Common issues

