# Dynamic Parallelism Walkthrough

## What is Dynamic Parallelism?

Kernels launching other kernels directly on the GPU.

## Simple Example

```moonlight
cuda kernel def parent(data, n) {
    if (n > 100) {
        gpu[1, 256] child(data, n / 2)
    }
}
```

## Recursive Example

```moonlight
cuda kernel def quicksort(data, left, right) {
    if (left < right) {
        pivot = partition(data, left, right)
        gpu[1, 256] quicksort(data, left, pivot - 1)
        gpu[1, 256] quicksort(data, pivot + 1, right)
    }
}
```

## Requirements

- Compute capability 3.5+
- Compile with `-rdc=true`
- Link with `-lcudadevrt`

## Depth Limits

Always check depth:
```moonlight
cuda kernel def recursive(n, depth) {
    if (depth >= 24) return  # CUDA limit
    # ...
}
```

## Complete Examples

- `examples/dynamic/nested_kernel.gpu`
- `examples/dynamic/recursive_sort.gpu`
- `examples/dynamic/tree_traversal.gpu`

## Next Steps

- Read `DYNAMIC_PARALLELISM.md` for details
- Try the examples
- Check benchmarks

