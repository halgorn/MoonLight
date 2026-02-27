# Optimization Guide

## Shared Memory Optimization

### Auto-Shared Memory

The compiler can automatically detect tiling patterns and use shared memory:

```moonlight
# @auto_shared decorator (future)
cuda kernel def matrix_mult(A, B, C, N) {
    # Compiler detects and uses shared memory
    # tile_A = shared[16][16]
    # tile_B = shared[16][16]
}
```

### Bank Conflict Avoidance

Avoid stride access patterns:
```moonlight
# BAD: Causes bank conflicts
# shared_data[tid * 4] = data[tid]

# GOOD: Sequential access
# shared_data[tid] = data[tid]
```

## Warp Primitives

### Warp Reduction

```moonlight
cuda kernel def reduce(data, result) {
    val = data[threadIdx_x]
    reduced = warp_reduce_sum(val)
    if (lane_id() == 0) {
        result[warp_id()] = reduced
    }
}
```

### Warp Shuffle

```moonlight
cuda kernel def shuffle(data) {
    val = data[threadIdx_x]
    shuffled = warp_shuffle(val, lane_id() + 1)
    data[threadIdx_x] = shuffled
}
```

## Kernel Fusion

Multiple sequential kernels can be fused into one:

```moonlight
# Separate kernels
gpu[blocks, threads] step1(data, n)
gpu[blocks, threads] step2(data, n)
gpu[blocks, threads] step3(data, n)

# Fused kernel (automatic with @optimize(level=3))
cuda kernel def fused(data, n) {
    # Step 1, 2, 3 combined
}
```

## Optimization Levels

```moonlight
# @optimize(level=1) - Basic optimizations
# @optimize(level=2) - Aggressive optimizations
# @optimize(level=3) - Maximum optimizations (includes fusion)
```

## Performance Hints

```moonlight
# @hints(occupancy=100, registers=32, shared_memory=48KB, threads_per_block=256)
cuda kernel def optimized(data, n) {
    # Compiler uses hints for optimization
}
```

## Branch Optimization

### Minimize Divergence

```moonlight
# BAD: Divergent branches
if (data[tid] > threshold) {
    path_a()
} else {
    path_b()
}

# GOOD: Warp-aligned branches when possible
# Or use arithmetic instead
result = data[tid] * (condition ? 2.0 : 0.5)
```

## Memory Coalescing

Access memory sequentially:
```moonlight
# GOOD: Coalesced access
data[tid] = value

# BAD: Strided access
data[tid * 4] = value
```

## Best Practices

1. **Use Shared Memory**: For frequently accessed data
2. **Minimize Branches**: Use arithmetic when possible
3. **Coalesce Memory**: Sequential access patterns
4. **Fuse Kernels**: When beneficial
5. **Profile First**: Measure before optimizing

## See Also

- `examples/optimization/` - Optimization examples
- `benchmarks/optimization/` - Performance benchmarks

