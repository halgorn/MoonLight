# 🚀 Quick Start: Implementando 100% GPU

## Começando HOJE!

Este guia mostra como começar a implementar as features GPU-first **imediatamente**.

---

## ✅ Fase 1 - Semana 1: Work Queue (COMEÇAR AQUI!)

### O que implementar:

#### 1. Lock-Free Queue na GPU

Criar arquivo: `gpu_runtime/queue.cuh`

```cpp
#ifndef GPU_QUEUE_H
#define GPU_QUEUE_H

#include <cuda_runtime.h>

template<typename T>
struct GPUQueue {
    T* buffer;
    int* head;
    int* tail;
    int capacity;
    int mask;  // capacity - 1 (para otimização)
    
    // Device functions
    __device__ bool enqueue(const T& item);
    __device__ bool dequeue(T* item);
    __device__ T dequeue_wait();  // Spin-wait até ter item
    __device__ bool is_empty();
    __device__ bool is_full();
    __device__ int size();
};

// Host functions
template<typename T>
GPUQueue<T>* create_gpu_queue(int capacity);

template<typename T>
void destroy_gpu_queue(GPUQueue<T>* queue);

template<typename T>
bool enqueue_from_host(GPUQueue<T>* queue, const T& item);

template<typename T>
bool dequeue_to_host(GPUQueue<T>* queue, T* item);

#endif
```

#### 2. Implementação

Criar arquivo: `gpu_runtime/queue.cu`

```cpp
#include "queue.cuh"

template<typename T>
__device__ bool GPUQueue<T>::enqueue(const T& item) {
    int current_tail = atomicAdd(tail, 1);
    int index = current_tail & mask;
    
    // Espera até ter espaço
    while ((current_tail - atomicAdd(head, 0)) >= capacity) {
        __threadfence();
    }
    
    buffer[index] = item;
    __threadfence();
    return true;
}

template<typename T>
__device__ bool GPUQueue<T>::dequeue(T* item) {
    int current_head = atomicAdd(head, 0);
    int current_tail = atomicAdd(tail, 0);
    
    if (current_head >= current_tail) {
        return false;  // Queue empty
    }
    
    int old_head = atomicAdd(head, 1);
    int index = old_head & mask;
    
    *item = buffer[index];
    __threadfence();
    return true;
}

template<typename T>
__device__ T GPUQueue<T>::dequeue_wait() {
    T item;
    int backoff = 1;
    
    while (!dequeue(&item)) {
        // Exponential backoff para reduzir contenção
        for (int i = 0; i < backoff; i++) {
            __threadfence();
        }
        if (backoff < 1024) backoff *= 2;
    }
    
    return item;
}

// Host functions
template<typename T>
GPUQueue<T>* create_gpu_queue(int capacity) {
    // Capacity deve ser potência de 2
    int cap = 1;
    while (cap < capacity) cap *= 2;
    
    GPUQueue<T>* h_queue = new GPUQueue<T>();
    GPUQueue<T>* d_queue;
    
    cudaMalloc(&d_queue, sizeof(GPUQueue<T>));
    cudaMalloc(&h_queue->buffer, cap * sizeof(T));
    cudaMalloc(&h_queue->head, sizeof(int));
    cudaMalloc(&h_queue->tail, sizeof(int));
    
    h_queue->capacity = cap;
    h_queue->mask = cap - 1;
    
    cudaMemset(h_queue->head, 0, sizeof(int));
    cudaMemset(h_queue->tail, 0, sizeof(int));
    
    cudaMemcpy(d_queue, h_queue, sizeof(GPUQueue<T>), cudaMemcpyHostToDevice);
    
    return d_queue;
}
```

#### 3. Teste Básico

Criar: `tests/test_gpu_queue.cu`

```cpp
#include "queue.cuh"
#include <iostream>

struct Task {
    int id;
    float data[4];
};

__global__ void producer(GPUQueue<Task>* queue, int n) {
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    
    if (tid < n) {
        Task task;
        task.id = tid;
        queue->enqueue(task);
    }
}

__global__ void consumer(GPUQueue<Task>* queue, int* results, int n) {
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    
    if (tid < n) {
        Task task = queue->dequeue_wait();
        results[tid] = task.id;
    }
}

int main() {
    const int N = 1000;
    
    // Create queue
    auto queue = create_gpu_queue<Task>(2048);
    
    int* d_results;
    cudaMalloc(&d_results, N * sizeof(int));
    
    // Launch producer and consumer concurrently
    producer<<<4, 256>>>(queue, N);
    consumer<<<4, 256>>>(queue, d_results, N);
    
    cudaDeviceSynchronize();
    
    // Verify
    int* h_results = new int[N];
    cudaMemcpy(h_results, d_results, N * sizeof(int), cudaMemcpyDeviceToHost);
    
    bool success = true;
    for (int i = 0; i < N; i++) {
        if (h_results[i] < 0 || h_results[i] >= N) {
            success = false;
            break;
        }
    }
    
    std::cout << "Test " << (success ? "PASSED" : "FAILED") << std::endl;
    
    return success ? 0 : 1;
}
```

### Compilar e Testar:

```bash
nvcc -o test_queue tests/test_gpu_queue.cu gpu_runtime/queue.cu -std=c++11
./test_queue
```

---

## ✅ Fase 2: Integrar com MoonLight

### 1. Adicionar Tokens ao Lexer

Editar `lexer.py`:

```python
reserved = {
    # ... existing ...
    'gpu_queue': 'GPU_QUEUE',
    'enqueue_host': 'ENQUEUE_HOST',
    'dequeue_host': 'DEQUEUE_HOST',
    'dequeue_wait': 'DEQUEUE_WAIT',
}
```

### 2. Adicionar Parser Rules

Editar `parser.py`:

```python
def p_statement_queue_declaration(p):
    '''statement : IDENTIFIER ASSIGN GPU_QUEUE LBRACKET IDENTIFIER COMMA expression RBRACKET'''
    # queue_name = gpu_queue[Type, capacity]
    p[0] = ('gpu_queue_decl', p[1], p[5], p[7])

def p_statement_enqueue_host(p):
    '''statement : ENQUEUE_HOST LPAREN IDENTIFIER COMMA expression RPAREN'''
    p[0] = ('enqueue_host', p[3], p[5])

def p_expression_dequeue_wait(p):
    '''expression : DEQUEUE_WAIT LPAREN IDENTIFIER RPAREN'''
    p[0] = ('dequeue_wait', p[3])
```

### 3. Transpiler Support

Editar `transpiler.py`:

```python
elif op == 'gpu_queue_decl':
    queue_name = node[1]
    elem_type = node[2]
    capacity = traduzir_ast(node[3], 0)
    
    code = f"{ind}GPUQueue<{elem_type}>* {queue_name} = "
    code += f"create_gpu_queue<{elem_type}>({capacity});\n"
    return code

elif op == 'enqueue_host':
    queue = node[1]
    item = traduzir_ast(node[2], 0)
    return f"{ind}enqueue_from_host({queue}, {item});\n"

elif op == 'dequeue_wait':
    queue = node[1]
    return f"dequeue_wait({queue})"
```

---

## ✅ Teste End-to-End

### Exemplo MoonLight:

Criar: `examples/persistent/first_persistent.gpu`

```moonlight
# Definir estrutura de tarefa
struct Task {
    id: int
    value: float
}

# Persistent kernel
cuda persistent kernel def worker(input_queue, output_queue) {
    tid = threadIdx_x + blockIdx_x * blockDim_x
    
    while (true) {
        # Espera por trabalho
        task = dequeue_wait(input_queue)
        
        # Stop signal
        if (task.id == -1) { break }
        
        # Processa
        result = task.value * 2.0
        
        # Output
        output_task = Task()
        output_task.id = task.id
        output_task.value = result
        
        enqueue(output_queue, output_task)
    }
}

def main() {
    # Criar filas
    input_q = gpu_queue[Task, 1000]
    output_q = gpu_queue[Task, 1000]
    
    # Lançar worker PERSISTENTE
    gpu[32, 256] worker(input_q, output_q)
    
    # Enviar trabalho
    for (i = 0; i < 100; i = i + 1) {
        task = Task()
        task.id = i
        task.value = float(i)
        
        enqueue_host(input_q, task)
    }
    
    # Receber resultados
    for (i = 0; i < 100; i = i + 1) {
        result = dequeue_host(output_q)
        print("Result", result.id, ":", result.value)
    }
    
    # Parar worker
    stop_task = Task()
    stop_task.id = -1
    enqueue_host(input_q, stop_task)
    
    print("Complete!")
}

main()
```

### Compilar:

```bash
python moonc.py examples/persistent/first_persistent.gpu -o persistent_test --cuda
./persistent_test
```

---

## 📊 Checklist Semana 1

- [ ] `queue.cuh` criado
- [ ] `queue.cu` implementado
- [ ] Test básico passando
- [ ] Lexer atualizado
- [ ] Parser atualizado
- [ ] Transpiler atualizado
- [ ] Exemplo end-to-end funcionando
- [ ] Documentação atualizada

**Meta**: Ao fim da semana 1, ter persistent kernels FUNCIONANDO com work queues!

---

## 🎯 Próximos Passos (Semana 2)

1. Adicionar múltiplos tipos de queue
2. Otimizar backoff strategy
3. Adicionar queue statistics
4. Implementar bounded/unbounded queues
5. Criar exemplos mais complexos

---

## 💡 Dicas de Implementação

### Performance:
- Use potências de 2 para capacity (otimização de módulo)
- Exponential backoff reduz contenção
- `__threadfence()` é crucial para consistência

### Debugging:
```cpp
__device__ void debug_queue_state(GPUQueue<Task>* q) {
    if (threadIdx.x == 0 && blockIdx.x == 0) {
        printf("Queue: head=%d tail=%d size=%d\n", 
               *q->head, *q->tail, q->size());
    }
}
```

### Testing:
- Teste com diferentes números de producers/consumers
- Teste queue vazia/cheia
- Teste com alta contenção
- Use cuda-memcheck para verificar races

---

## 🚀 Resultado Esperado Semana 1

Ao fim da semana 1, você terá:

✅ Work queue thread-safe na GPU  
✅ Persistent kernel básico funcionando  
✅ Syntax MoonLight para queues  
✅ Exemplo end-to-end compilando e rodando  

**Isso é a BASE para tudo!** Com queues funcionando, o resto é "só" adicionar features! 🔥

---

**Ready to start? Let's build the future of GPU programming! 🚀**

