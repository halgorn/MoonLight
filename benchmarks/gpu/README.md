# MoonLight GPU Benchmarks

Compare MoonLight-generated CUDA code against hand-written CUDA C++.

## Requirements

- CUDA Toolkit (nvcc compiler)
- NVIDIA GPU with compute capability 3.5+
- Python 3.8+
- MoonLight compiler

## Quick Start

```bash
# Run all GPU benchmarks
python benchmarks/gpu/run_gpu_benchmarks.py
```

## Benchmarks

### 1. Vector Addition
- **File**: `gpu_vector_add.gpu` vs `gpu_vector_add.cu`
- **Size**: 10 million elements
- **Tests**: Basic kernel launch, memory transfers, 1D grid
- **Expected**: MoonLight should be within 5% of pure CUDA

### 2. Matrix Multiplication
- **File**: `gpu_matrix_mult.gpu` vs `gpu_matrix_mult.cu`  
- **Size**: 1024x1024 matrices
- **Tests**: 2D grid/block configuration, compute-intensive kernel
- **Expected**: MoonLight should be within 10% of pure CUDA

## What is Measured

For each benchmark:
- **H->D Transfer**: Time to copy data from host (CPU) to device (GPU)
- **Kernel Execution**: Time for GPU kernel to complete
- **D->H Transfer**: Time to copy results back to host
- **Total Time**: End-to-end execution time
- **GFLOPS**: Floating-point operations per second (when applicable)

## Understanding Results

### Good Performance (Target)
```
Speedup: 0.95x - 1.05x (within 5% of pure CUDA)
```

### Acceptable Performance
```
Speedup: 0.80x - 0.95x (some optimization opportunities)
```

### Needs Optimization
```
Speedup: < 0.80x (transpiler needs improvement)
```

## Interpreting Speedup

- **Speedup > 1.0**: MoonLight faster than pure CUDA (unlikely, but possible with better defaults)
- **Speedup ≈ 1.0**: Equivalent performance (ideal)
- **Speedup < 1.0**: Pure CUDA faster (CUDA time / MoonLight time)

Example:
- Pure CUDA: 100ms
- MoonLight: 105ms
- Speedup: 100/105 = 0.95x (MoonLight is 5% slower)

## Manual Testing

### Compile and run pure CUDA:
```bash
nvcc gpu_vector_add.cu -o vector_add_cuda -O3
./vector_add_cuda
```

### Compile and run MoonLight:
```bash
python ../../moonc.py gpu_vector_add.gpu -o vector_add_moonlight --cuda
./vector_add_moonlight
```

## Adding New Benchmarks

1. Create `.gpu` file with MoonLight code
2. Create `.cu` file with equivalent CUDA code
3. Add entry to `run_gpu_benchmarks.py` in `benchmarks` list
4. Follow existing patterns for consistency

## Troubleshooting

### CUDA not found
```
Install CUDA Toolkit from: https://developer.nvidia.com/cuda-downloads
Add nvcc to PATH
```

### No GPU detected
```
Verify with: nvidia-smi
Check CUDA installation
Update GPU drivers
```

### Compilation fails
```
Check MoonLight syntax matches expected format
Verify CUDA code compiles standalone
Check for missing #includes in generated code
```

## Performance Tips

- Use `-O3` optimization for both MoonLight and CUDA
- Run multiple times and average (first run may include warmup overhead)
- Close other GPU applications during benchmarking
- Monitor GPU temperature (throttling affects results)

## Current Limitations

1. MoonLight transpiler is under development
2. Some CUDA features not yet fully supported
3. Optimization passes being added incrementally
4. Error messages may need improvement

## Future Benchmarks

Planned additions:
- [ ] Parallel reduction (sum, max, min)
- [ ] Sorting algorithms (bitonic sort, radix sort)
- [ ] Stencil computations
- [ ] Dynamic parallelism examples
- [ ] Multi-GPU workload distribution
- [ ] Persistent kernels with work queues

## Performance Goals

| Feature | Target | Status |
|---------|--------|--------|
| Basic kernels | 95% of CUDA | 🔄 In Progress |
| Memory transfers | 100% (same API) | ✅ Should match |
| 2D/3D grids | 95% of CUDA | 🔄 In Progress |
| Shared memory | 95% of CUDA | ⏳ Planned |
| Dynamic parallelism | 90% of CUDA | ⏳ Planned |
| Multi-GPU | 95% of CUDA | ⏳ Planned |

## Contributing

To add benchmarks:
1. Ensure fair comparison (identical algorithm)
2. Include timing breakdowns
3. Document expected performance
4. Test on multiple GPUs if possible

## License

Same as MoonLight project.

