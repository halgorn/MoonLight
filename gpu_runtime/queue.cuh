#ifndef GPU_QUEUE_H
#define GPU_QUEUE_H

#include <cuda_runtime.h>

template<typename T>
struct GPUQueue {
    T* buffer;
    int* head;
    int* tail;
    int capacity;
    int mask;  // capacity - 1 (for optimization)
    
    // Device functions
    __device__ bool enqueue(const T& item);
    __device__ bool dequeue(T* item);
    __device__ T dequeue_wait();  // Spin-wait until item available
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

#endif // GPU_QUEUE_H

