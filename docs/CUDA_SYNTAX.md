# MoonLight CUDA Syntax Guide

## Visão Geral

MoonLight oferece sintaxe simplificada para programação CUDA, permitindo escrever kernels GPU de forma mais intuitiva que CUDA C++.

## Sintaxe Básica

### 1. Definir Kernel CUDA

```moonlight
cuda kernel def kernel_name(params...) {
    # Código do kernel
}
```

**Exemplo:**
```moonlight
cuda kernel def add_vectors(a, b, c, n) {
    i = threadIdx_x + blockIdx_x * blockDim_x
    if (i < n) {
        c[i] = a[i] + b[i]
    }
}
```

### 2. Alocar Memória na GPU

```moonlight
d_array = device[size]
```

**Equivalente CUDA C++:**
```cpp
float* d_array;
cudaMalloc(&d_array, size * sizeof(float));
```

### 3. Transferência Host ↔ Device

```moonlight
# Host → Device
d_array <- h_array

# Device → Host
h_result <- d_result
```

**Equivalente CUDA C++:**
```cpp
// Host → Device
cudaMemcpy(d_array, h_array, size*sizeof(float), cudaMemcpyHostToDevice);

// Device → Host
cudaMemcpy(h_result, d_result, size*sizeof(float), cudaMemcpyDeviceToHost);
```

### 4. Lançar Kernel

#### Grid 1D
```moonlight
gpu[blocks, threads] kernel_name(args...)
```

**Exemplo:**
```moonlight
threads_per_block = 256
blocks = (n + threads_per_block - 1) / threads_per_block
gpu[blocks, threads_per_block] add_vectors(d_a, d_b, d_c, n)
```

#### Grid 2D
```moonlight
gpu[(blocks_x, blocks_y), (threads_x, threads_y)] kernel_name(args...)
```

**Exemplo:**
```moonlight
block_size = 16
grid_size = (N + block_size - 1) / block_size
gpu[(grid_size, grid_size), (block_size, block_size)] matmul(d_A, d_B, d_C, N)
```

### 5. Liberar Memória

```moonlight
free(d_array)
```

**Equivalente CUDA C++:**
```cpp
cudaFree(d_array);
```

## Built-in Variables CUDA

MoonLight mapeia as variáveis built-in do CUDA:

| MoonLight | CUDA C++ | Descrição |
|-----------|----------|-----------|
| `threadIdx_x` | `threadIdx.x` | Índice X do thread no bloco |
| `threadIdx_y` | `threadIdx.y` | Índice Y do thread no bloco |
| `threadIdx_z` | `threadIdx.z` | Índice Z do thread no bloco |
| `blockIdx_x` | `blockIdx.x` | Índice X do bloco no grid |
| `blockIdx_y` | `blockIdx.y` | Índice Y do bloco no grid |
| `blockIdx_z` | `blockIdx.z` | Índice Z do bloco no grid |
| `blockDim_x` | `blockDim.x` | Dimensão X do bloco |
| `blockDim_y` | `blockDim.y` | Dimensão Y do bloco |
| `blockDim_z` | `blockDim.z` | Dimensão Z do bloco |
| `gridDim_x` | `gridDim.x` | Dimensão X do grid |
| `gridDim_y` | `gridDim.y` | Dimensão Y do grid |
| `gridDim_z` | `gridDim.z` | Dimensão Z do grid |

## Shared Memory (Planejado para Entrega 7)

```moonlight
cuda kernel def kernel_with_shared() {
    # Declarar shared memory
    shared_data = shared[256]
    
    # Usar shared memory
    tid = threadIdx_x
    shared_data[tid] = input[tid]
    
    # Sincronizar threads
    syncthreads()
    
    # Usar dados compartilhados
    result[tid] = shared_data[tid] * 2
}
```

## Exemplos Completos

### Vector Addition
```moonlight
cuda kernel def add_vectors(a, b, c, n) {
    i = threadIdx_x + blockIdx_x * blockDim_x
    if (i < n) {
        c[i] = a[i] + b[i]
    }
}

def main() {
    n = 1024
    
    # Alocar host
    h_a = [float(i) for i in range(n)]
    h_b = [float(i*2) for i in range(n)]
    h_c = [0.0] * n
    
    # Alocar device
    d_a = device[n]
    d_b = device[n]
    d_c = device[n]
    
    # Copiar para device
    d_a <- h_a
    d_b <- h_b
    
    # Lançar kernel
    gpu[4, 256] add_vectors(d_a, d_b, d_c, n)
    
    # Copiar resultado
    h_c <- d_c
    
    # Cleanup
    free(d_a)
    free(d_b)
    free(d_c)
}
```

### Matrix Multiplication
```moonlight
cuda kernel def matmul(A, B, C, N) {
    row = blockIdx_y * blockDim_y + threadIdx_y
    col = blockIdx_x * blockDim_x + threadIdx_x
    
    if (row < N and col < N) {
        sum = 0.0
        for (k = 0; k < N; k = k + 1) {
            sum = sum + A[row * N + k] * B[k * N + col]
        }
        C[row * N + col] = sum
    }
}

def main() {
    N = 64
    size = N * N
    
    # Inicializar matrizes
    h_A = [float(i) for i in range(size)]
    h_B = [float(i) for i in range(size)]
    h_C = [0.0] * size
    
    # Alocar GPU
    d_A = device[size]
    d_B = device[size]
    d_C = device[size]
    
    # Copiar
    d_A <- h_A
    d_B <- h_B
    
    # Lançar kernel 2D
    block_size = 16
    grid_size = (N + block_size - 1) / block_size
    gpu[(grid_size, grid_size), (block_size, block_size)] matmul(d_A, d_B, d_C, N)
    
    # Resultado
    h_C <- d_C
    
    # Cleanup
    free(d_A)
    free(d_B)
    free(d_C)
}
```

## Limitações Atuais

1. **Tipos**: Apenas `float` suportado inicialmente
2. **Dimensões**: Máximo 3D (x, y, z)
3. **Shared Memory**: Planejado para Entrega 7
4. **Textures**: Não implementado
5. **Streams**: Planejado para Entrega 7
6. **Multi-GPU**: Planejado para Entrega 7

## Roadmap CUDA

### Entrega 6 (Atual): Básico ✅
- Sintaxe para kernels
- Alocação de memória
- Transferência host↔device
- Lançamento de kernels 1D/2D

### Entrega 7: Avançado ⬜
- Shared memory
- syncthreads()
- Múltiplos streams
- Multi-GPU
- Otimizações (coalescing, etc)

## Compilação e Execução

Para executar código CUDA MoonLight:

```bash
# Transpile para CUDA C++
python transpiler_cuda.py programa.gpu -o programa.cu

# Compilar com nvcc
nvcc programa.cu -o programa

# Executar
./programa
```

## Referências

- [CUDA C Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)
- [CUDA Best Practices](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/)
- [CUDA Toolkit Documentation](https://docs.nvidia.com/cuda/)

## Suporte

Para relatar problemas ou sugerir melhorias na sintaxe CUDA do MoonLight, abra uma issue no repositório.










