#include "queue.cuh"
#include <cstdio>

template<typename T>
__device__ bool GPUQueue<T>::enqueue(const T& item) {
    int current_tail = atomicAdd(tail, 1);
    int index = current_tail & mask;
    
    // Wait until there's space
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
        // Exponential backoff to reduce contention
        for (int i = 0; i < backoff; i++) {
            __threadfence();
        }
        if (backoff < 1024) backoff *= 2;
    }
    
    return item;
}

template<typename T>
__device__ bool GPUQueue<T>::is_empty() {
    int current_head = atomicAdd(head, 0);
    int current_tail = atomicAdd(tail, 0);
    return current_head >= current_tail;
}

template<typename T>
__device__ bool GPUQueue<T>::is_full() {
    int current_head = atomicAdd(head, 0);
    int current_tail = atomicAdd(tail, 0);
    return (current_tail - current_head) >= capacity;
}

template<typename T>
__device__ int GPUQueue<T>::size() {
    int current_head = atomicAdd(head, 0);
    int current_tail = atomicAdd(tail, 0);
    return current_tail - current_head;
}

// Host functions
template<typename T>
GPUQueue<T>* create_gpu_queue(int capacity) {
    // Validate capacity
    if (capacity <= 0) {
        fprintf(stderr, "Error: GPU queue capacity must be > 0, got %d\n", capacity);
        return nullptr;
    }
    
    if (capacity > 1024 * 1024 * 1024) {  // 1GB limit
        fprintf(stderr, "Error: GPU queue capacity too large: %d\n", capacity);
        return nullptr;
    }
    
    // Capacity must be power of 2
    int cap = 1;
    while (cap < capacity) cap *= 2;
    
    GPUQueue<T>* h_queue = new GPUQueue<T>();
    GPUQueue<T>* d_queue = nullptr;
    
    cudaError_t err;
    
    // Allocate queue structure
    err = cudaMalloc(&d_queue, sizeof(GPUQueue<T>));
    if (err != cudaSuccess) {
        fprintf(stderr, "Error allocating GPU queue structure: %s\n", cudaGetErrorString(err));
        delete h_queue;
        return nullptr;
    }
    
    // Allocate buffer
    err = cudaMalloc(&h_queue->buffer, cap * sizeof(T));
    if (err != cudaSuccess) {
        fprintf(stderr, "Error allocating GPU queue buffer: %s\n", cudaGetErrorString(err));
        cudaFree(d_queue);
        delete h_queue;
        return nullptr;
    }
    
    // Allocate head counter
    err = cudaMalloc(&h_queue->head, sizeof(int));
    if (err != cudaSuccess) {
        fprintf(stderr, "Error allocating GPU queue head: %s\n", cudaGetErrorString(err));
        cudaFree(h_queue->buffer);
        cudaFree(d_queue);
        delete h_queue;
        return nullptr;
    }
    
    // Allocate tail counter
    err = cudaMalloc(&h_queue->tail, sizeof(int));
    if (err != cudaSuccess) {
        fprintf(stderr, "Error allocating GPU queue tail: %s\n", cudaGetErrorString(err));
        cudaFree(h_queue->head);
        cudaFree(h_queue->buffer);
        cudaFree(d_queue);
        delete h_queue;
        return nullptr;
    }
    
    h_queue->capacity = cap;
    h_queue->mask = cap - 1;
    
    // Initialize counters
    err = cudaMemset(h_queue->head, 0, sizeof(int));
    if (err != cudaSuccess) {
        fprintf(stderr, "Error initializing queue head: %s\n", cudaGetErrorString(err));
    }
    
    err = cudaMemset(h_queue->tail, 0, sizeof(int));
    if (err != cudaSuccess) {
        fprintf(stderr, "Error initializing queue tail: %s\n", cudaGetErrorString(err));
    }
    
    // Copy to device
    err = cudaMemcpy(d_queue, h_queue, sizeof(GPUQueue<T>), cudaMemcpyHostToDevice);
    if (err != cudaSuccess) {
        fprintf(stderr, "Error copying queue to device: %s\n", cudaGetErrorString(err));
        cudaFree(h_queue->tail);
        cudaFree(h_queue->head);
        cudaFree(h_queue->buffer);
        cudaFree(d_queue);
        delete h_queue;
        return nullptr;
    }
    
    delete h_queue;
    return d_queue;
}

template<typename T>
void destroy_gpu_queue(GPUQueue<T>* d_queue) {
    if (d_queue == nullptr) {
        return;  // Already destroyed or invalid
    }
    
    GPUQueue<T> h_queue;
    cudaError_t err = cudaMemcpy(&h_queue, d_queue, sizeof(GPUQueue<T>), cudaMemcpyDeviceToHost);
    if (err != cudaSuccess) {
        fprintf(stderr, "Warning: Error reading queue structure during destroy: %s\n", cudaGetErrorString(err));
        // Try to free anyway
        cudaFree(d_queue);
        return;
    }
    
    // Free all components
    if (h_queue.buffer != nullptr) {
        err = cudaFree(h_queue.buffer);
        if (err != cudaSuccess) {
            fprintf(stderr, "Warning: Error freeing queue buffer: %s\n", cudaGetErrorString(err));
        }
    }
    
    if (h_queue.head != nullptr) {
        err = cudaFree(h_queue.head);
        if (err != cudaSuccess) {
            fprintf(stderr, "Warning: Error freeing queue head: %s\n", cudaGetErrorString(err));
        }
    }
    
    if (h_queue.tail != nullptr) {
        err = cudaFree(h_queue.tail);
        if (err != cudaSuccess) {
            fprintf(stderr, "Warning: Error freeing queue tail: %s\n", cudaGetErrorString(err));
        }
    }
    
    err = cudaFree(d_queue);
    if (err != cudaSuccess) {
        fprintf(stderr, "Warning: Error freeing queue structure: %s\n", cudaGetErrorString(err));
    }
}

template<typename T>
bool enqueue_from_host(GPUQueue<T>* d_queue, const T& item) {
    GPUQueue<T> h_queue;
    cudaMemcpy(&h_queue, d_queue, sizeof(GPUQueue<T>), cudaMemcpyDeviceToHost);
    
    int current_tail, current_head;
    cudaMemcpy(&current_tail, h_queue.tail, sizeof(int), cudaMemcpyDeviceToHost);
    cudaMemcpy(&current_head, h_queue.head, sizeof(int), cudaMemcpyDeviceToHost);
    
    if ((current_tail - current_head) >= h_queue.capacity) {
        return false;  // Queue full
    }
    
    int index = current_tail & h_queue.mask;
    cudaMemcpy(&h_queue.buffer[index], &item, sizeof(T), cudaMemcpyHostToDevice);
    
    current_tail++;
    cudaMemcpy(h_queue.tail, &current_tail, sizeof(int), cudaMemcpyHostToDevice);
    
    return true;
}

template<typename T>
bool dequeue_to_host(GPUQueue<T>* d_queue, T* item) {
    GPUQueue<T> h_queue;
    cudaMemcpy(&h_queue, d_queue, sizeof(GPUQueue<T>), cudaMemcpyDeviceToHost);
    
    int current_head, current_tail;
    cudaMemcpy(&current_head, h_queue.head, sizeof(int), cudaMemcpyDeviceToHost);
    cudaMemcpy(&current_tail, h_queue.tail, sizeof(int), cudaMemcpyDeviceToHost);
    
    if (current_head >= current_tail) {
        return false;  // Queue empty
    }
    
    int index = current_head & h_queue.mask;
    cudaMemcpy(item, &h_queue.buffer[index], sizeof(T), cudaMemcpyDeviceToHost);
    
    current_head++;
    cudaMemcpy(h_queue.head, &current_head, sizeof(int), cudaMemcpyHostToDevice);
    
    return true;
}

// Explicit template instantiation for common types
template struct GPUQueue<int>;
template struct GPUQueue<float>;
template struct GPUQueue<double>;

template GPUQueue<int>* create_gpu_queue<int>(int);
template GPUQueue<float>* create_gpu_queue<float>(int);
template GPUQueue<double>* create_gpu_queue<double>(int);

template void destroy_gpu_queue<int>(GPUQueue<int>*);
template void destroy_gpu_queue<float>(GPUQueue<float>*);
template void destroy_gpu_queue<double>(GPUQueue<double>*);

template bool enqueue_from_host<int>(GPUQueue<int>*, const int&);
template bool enqueue_from_host<float>(GPUQueue<float>*, const float&);
template bool enqueue_from_host<double>(GPUQueue<double>*, const double&);

template bool dequeue_to_host<int>(GPUQueue<int>*, int*);
template bool dequeue_to_host<float>(GPUQueue<float>*, float*);
template bool dequeue_to_host<double>(GPUQueue<double>*, double*);

