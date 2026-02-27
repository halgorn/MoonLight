# MoonLight CUDA - Features Avançadas

## Shared Memory

### Declaração
```moonlight
cuda kernel def kernel_with_shared() {
    shared_data = shared[256]
    # Usar shared_data como array local ao bloco
}
```

### Benefícios
- **100x mais rápido** que global memory
- Compartilhada entre threads do mesmo bloco
- Ideal para redução e comunicação inter-thread

## Sincronização

```moonlight
syncthreads()  # Sincroniza todas as threads do bloco
```

**Importante**: Obrigatório após escrever em shared memory e antes de ler.

## Streams Paralelos

### Criar Stream
```moonlight
stream = cuda_stream()
```

### Lançar Kernel Assíncrono
```moonlight
gpu[blocks, threads, stream] kernel(args)
```

### Cópia Assíncrona
```moonlight
d_array <-async[stream] h_array
```

### Sincronizar Stream
```moonlight
cuda_stream_sync(stream)
```

### Destruir Stream
```moonlight
cuda_stream_destroy(stream)
```

## Multi-GPU

### Contar GPUs
```moonlight
gpu_count = cuda_device_count()
```

### Selecionar GPU
```moonlight
cuda_set_device(gpu_id)
```

### Processar em Múltiplas GPUs
```moonlight
for (gpu_id = 0; gpu_id < gpu_count; gpu_id = gpu_id + 1) {
    cuda_set_device(gpu_id)
    # Alocar e processar nesta GPU
}
```

## Redução Paralela

Algoritmo otimizado para somar/reduzir arrays grandes:

```moonlight
cuda kernel def reduce_sum(input, output, n) {
    shared_data = shared[256]
    
    tid = threadIdx_x
    i = blockIdx_x * blockDim_x + threadIdx_x
    
    # Carregar para shared
    if (i < n) {
        shared_data[tid] = input[i]
    } else {
        shared_data[tid] = 0.0
    }
    
    syncthreads()
    
    # Redução em árvore
    s = blockDim_x / 2
    while (s > 0) {
        if (tid < s) {
            shared_data[tid] = shared_data[tid] + shared_data[tid + s]
        }
        syncthreads()
        s = s / 2
    }
    
    if (tid == 0) {
        output[blockIdx_x] = shared_data[0]
    }
}
```

## Matrix Multiplication Otimizada

Com tiling e shared memory:

```moonlight
cuda kernel def matmul_shared(A, B, C, N, TILE_SIZE) {
    tile_A = shared[TILE_SIZE * TILE_SIZE]
    tile_B = shared[TILE_SIZE * TILE_SIZE]
    
    tx = threadIdx_x
    ty = threadIdx_y
    row = blockIdx_y * TILE_SIZE + ty
    col = blockIdx_x * TILE_SIZE + tx
    
    sum = 0.0
    
    for (tile = 0; tile < (N / TILE_SIZE); tile = tile + 1) {
        # Carregar tiles
        tile_A[ty * TILE_SIZE + tx] = A[row * N + tile * TILE_SIZE + tx]
        tile_B[ty * TILE_SIZE + tx] = B[(tile * TILE_SIZE + ty) * N + col]
        
        syncthreads()
        
        # Computar
        for (k = 0; k < TILE_SIZE; k = k + 1) {
            sum = sum + tile_A[ty * TILE_SIZE + k] * tile_B[k * TILE_SIZE + tx]
        }
        
        syncthreads()
    }
    
    C[row * N + col] = sum
}
```

## Otimizações

### 1. Coalesced Memory Access
```moonlight
# BOM: Acessos consecutivos
for (i = tid; i < n; i = i + stride) {
    data[i] = ...
}

# RUIM: Acessos aleatórios
for (i = 0; i < n; i = i + 1) {
    data[random_index[i]] = ...
}
```

### 2. Occupancy
- Use múltiplos de 32 threads (warp size)
- Blocks de 128-512 threads geralmente ótimos

### 3. Shared Memory
- Minimize bank conflicts
- Use padding se necessário

### 4. Register Usage
- Menos variáveis locais = mais occupancy

## Exemplos Disponíveis

Ver `examples/cuda/`:
- `parallel_reduction.gpu` - Redução paralela
- `multi_stream.gpu` - Streams assíncronos
- `multi_gpu.gpu` - Distribuição multi-GPU
- `optimized_matmul.gpu` - Multiplicação otimizada









