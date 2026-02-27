# Dynamic Parallelism Guide

## What is Dynamic Parallelism?

Dynamic parallelism allows GPU kernels to launch other GPU kernels, enabling recursive algorithms and adaptive work generation directly on the GPU.

## Benefits

- **Recursive Algorithms**: Implement quicksort, tree traversal, etc.
- **Adaptive Processing**: Generate work based on GPU-side conditions
- **No CPU Round-trip**: Decisions made on GPU
- **Flexible Work Generation**: Create work dynamically

## Requirements

- Compute capability 3.5+
- Compile with `-rdc=true`
- Link with `-lcudadevrt`
- Maximum recursion depth: 24 levels

## Syntax

```moonlight
cuda kernel def parent(data, n) {
    if (n > threshold) {
        # Launch child kernel
        gpu[1, 256] child(data, n / 2)
    }
}
```

## Example: Recursive Quicksort

```moonlight
cuda kernel def quicksort(data, left, right) {
    if (left < right) {
        pivot = partition(data, left, right)
        gpu[1, 256] quicksort(data, left, pivot - 1)
        gpu[1, 256] quicksort(data, pivot + 1, right)
    }
}
```

## Example: Adaptive Mesh Refinement

```moonlight
cuda kernel def refine_mesh(cell, error_threshold) {
    error = calculate_error(cell)
    if (error > error_threshold) {
        # Subdivide and refine
        gpu[1, 256] refine_cell(cell)
    }
}
```

## Depth Limits

CUDA limits recursion depth to 24 levels. Always check depth:

```moonlight
cuda kernel def recursive(n, depth) {
    if (depth >= 24) {
        return  # Respect CUDA limit
    }
    if (n > 1) {
        gpu[1, 256] recursive(n / 2, depth + 1)
    }
}
```

## Memory Management

Be careful with memory allocation in recursive kernels:

```moonlight
cuda kernel def safe_recursive(n) {
    if (n <= 1) {
        return
    }
    # Use stack/local variables, not malloc
    result = n * n
    gpu[1, 256] safe_recursive(n - 1)
}
```

## Best Practices

1. **Check Depth**: Always validate recursion depth
2. **Avoid Malloc in Recursion**: Use stack variables when possible
3. **Base Cases**: Ensure proper termination conditions
4. **Synchronization**: Child kernels complete before parent continues

## Performance Considerations

- **Launch Overhead**: Each nested launch has overhead
- **Depth Limit**: 24 levels maximum
- **Memory**: Each level may use device memory

## See Also

- `examples/dynamic/` - Complete examples
- `benchmarks/dynamic/` - Performance benchmarks
- `tests/test_dynamic_parallelism.py` - Test suite

