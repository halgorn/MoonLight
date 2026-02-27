# Getting Started with MoonLight

## Installation

1. Install CUDA Toolkit 11.0+
2. Ensure Python 3.7+ is installed
3. Clone the MoonLight repository

## Your First Program

Create a file `hello.gpu`:

```moonlight
cuda kernel def hello(data, n) {
    tid = threadIdx_x + blockIdx_x * blockDim_x
    if (tid < n) {
        data[tid] = tid * 2.0
    }
}

def main() {
    n = 1000
    d_data = device[n]
    
    blocks = (n + 255) / 256
    gpu[blocks, 256] hello(d_data, n)
    
    print("Hello from MoonLight!")
    free(d_data)
}

main()
```

## Compile and Run

```bash
python moonc.py hello.gpu
./hello
```

## Next Steps

1. Read `GPU_FIRST_COMPLETE.md` for overview
2. Try examples in `examples/`
3. Explore persistent kernels
4. Learn about GPU-resident data
5. Try multi-GPU examples

## Resources

- Examples: `examples/`
- Benchmarks: `benchmarks/`
- Documentation: `docs/`
- Tests: `tests/`

