# MoonLight CUDA Examples

Exemplos de código CUDA em MoonLight demonstrando a sintaxe proposta.

## ⚠️ NOTA IMPORTANTE

Estes exemplos demonstram a **sintaxe proposta** para suporte CUDA no MoonLight.  
A implementação completa requer:
- Transpiler CUDA funcional
- Hardware GPU NVIDIA
- CUDA Toolkit instalado

## 📝 Sintaxe CUDA Proposta

### 1. Definir Kernel
```moonlight
cuda kernel def kernel_name(params) {
    # Código do kernel
    i = threadIdx_x + blockIdx_x * blockDim_x
    # ...
}
```

### 2. Alocar Memória GPU
```moonlight
d_array = device[size]  # Aloca na GPU
```

### 3. Transferência de Dados
```moonlight
d_array <- h_array  # Host → Device
h_result <- d_result  # Device → Host
```

### 4. Lançar Kernel
```moonlight
# 1D grid
gpu[blocks, threads] kernel_name(args)

# 2D grid
gpu[(blocks_x, blocks_y), (threads_x, threads_y)] kernel_name(args)
```

### 5. Liberar Memória
```moonlight
free(d_array)
```

## 📂 Exemplos

### vector_add.gpu
Soma de vetores - exemplo básico de paralelização.

### matrix_mult.gpu
Multiplicação de matrizes - grid 2D e acesso a memória.

## 🚀 Próximos Passos

Para tornar esses exemplos funcionais, é necessário:

1. **Parser**: Adicionar regras para sintaxe CUDA
   - `cuda kernel def`
   - `device[size]`
   - `gpu[blocks, threads]`
   - Operador `<-` para transferência

2. **Transpiler**: Gerar código CUDA C++
   - `__global__` kernels
   - `cudaMalloc`, `cudaMemcpy`
   - `<<<blocks, threads>>>`

3. **Runtime**: Compilar e executar com nvcc
   - Verificar hardware GPU
   - Compilar com `nvcc`
   - Executar binário

4. **Error Handling**: Verificar erros CUDA
   - `cudaGetLastError()`
   - Mensagens de erro claras

## 💡 Conceitos CUDA

### Thread Hierarchy
- **Thread**: Unidade de execução
- **Block**: Grupo de threads
- **Grid**: Conjunto de blocks

### Built-in Variables
- `threadIdx.x/y/z`: Índice do thread no bloco
- `blockIdx.x/y/z`: Índice do bloco no grid
- `blockDim.x/y/z`: Dimensão do bloco
- `gridDim.x/y/z`: Dimensão do grid

### Memory Hierarchy
- **Global Memory**: Acessível por todos os threads
- **Shared Memory**: Compartilhada dentro de um bloco
- **Local Memory**: Private para cada thread

## 📚 Referências

- [CUDA C Programming Guide](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)
- [CUDA Best Practices](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/)










