// MoonLight Runtime: Dynamic Parallelism Support
// Headers and utilities for nested kernel launches

#ifndef DYNAMIC_LAUNCH_H
#define DYNAMIC_LAUNCH_H

#include <cuda_runtime.h>
#include <device_launch_parameters.h>

// Dynamic parallelism requires:
// - CUDA compute capability 3.5+
// - Compilation with -rdc=true (relocatable device code)
// - Linking with -lcudadevrt

// Device-side synchronization
// Use this to wait for child kernels to complete
__device__ void sync_child_kernels() {
    // In CUDA, use cudaDeviceSynchronize() in device code
    // This is a wrapper for clarity
    cudaDeviceSynchronize();
}

// Helper for launching child kernels with error checking
__device__ void launch_child_kernel_safe(
    void (*kernel)(),
    dim3 gridDim,
    dim3 blockDim,
    void** args,
    size_t sharedMem = 0,
    cudaStream_t stream = 0
) {
    // Launch child kernel
    kernel<<<gridDim, blockDim, sharedMem, stream>>>(args);
    
    // Check for errors (optional but recommended)
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        // Handle error (in real app: proper error handling)
        printf("Child kernel launch error: %s\n", cudaGetErrorString(err));
    }
}

// Recursion depth tracking
// Helps prevent stack overflow in recursive kernels
__device__ struct RecursionTracker {
    int depth;
    int max_depth;
    
    __device__ RecursionTracker(int max) {
        depth = 0;
        max_depth = max;
    }
    
    __device__ bool can_recurse() {
        return depth < max_depth;
    }
    
    __device__ void enter() {
        depth = depth + 1;
    }
    
    __device__ void exit() {
        depth = depth - 1;
    }
    
    __device__ int get_depth() {
        return depth;
    }
};

// Work queue for dynamic work generation
// Allows kernels to generate work for other kernels
__device__ struct DynamicWorkQueue {
    int* work_items;
    int* head;
    int* tail;
    int capacity;
    
    __device__ bool enqueue_work(int item) {
        int current_tail = atomicAdd(tail, 1);
        if (current_tail - *head >= capacity) {
            return false;  // Queue full
        }
        work_items[current_tail % capacity] = item;
        return true;
    }
    
    __device__ bool dequeue_work(int* item) {
        int current_head = *head;
        if (current_head >= *tail) {
            return false;  // Queue empty
        }
        *item = work_items[current_head % capacity];
        atomicAdd(head, 1);
        return true;
    }
};

#endif // DYNAMIC_LAUNCH_H

