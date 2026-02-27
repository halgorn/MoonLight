// MoonLight Runtime: Device-Side Memory Allocation
// Provides malloc/free functionality within CUDA kernels

#include <cuda_runtime.h>
#include <device_launch_parameters.h>

// Device-side memory allocator
// Uses CUDA's device-side malloc (requires compute capability 2.0+)
// Note: Requires compilation with -rdc=true and linking with -lcudadevrt

// Wrapper for device-side malloc with validation
__device__ void* device_malloc_wrapper(size_t size) {
    if (size == 0) {
        return nullptr;  // Invalid size
    }
    
    // Reasonable size limit (1GB)
    if (size > 1024 * 1024 * 1024) {
        return nullptr;  // Too large
    }
    
    void* ptr = malloc(size);
    
    // Note: In device code, we can't easily report errors
    // The caller should check for nullptr
    return ptr;
}

// Wrapper for device-side free with validation
__device__ void device_free_wrapper(void* ptr) {
    if (ptr != nullptr) {
        free(ptr);
    }
    // Note: Double-free is undefined behavior in CUDA
    // Caller should set pointer to nullptr after free
}

// Helper for allocating arrays with validation
__device__ float* device_malloc_float(int n) {
    if (n <= 0) {
        return nullptr;  // Invalid size
    }
    
    // Check for overflow
    size_t size = (size_t)n * sizeof(float);
    if (size / sizeof(float) != (size_t)n) {
        return nullptr;  // Overflow
    }
    
    return (float*)malloc(size);
}

__device__ int* device_malloc_int(int n) {
    if (n <= 0) {
        return nullptr;  // Invalid size
    }
    
    // Check for overflow
    size_t size = (size_t)n * sizeof(int);
    if (size / sizeof(int) != (size_t)n) {
        return nullptr;  // Overflow
    }
    
    return (int*)malloc(size);
}

__device__ double* device_malloc_double(int n) {
    if (n <= 0) {
        return nullptr;  // Invalid size
    }
    
    // Check for overflow
    size_t size = (size_t)n * sizeof(double);
    if (size / sizeof(double) != (size_t)n) {
        return nullptr;  // Overflow
    }
    
    return (double*)malloc(size);
}

// Memory pool for faster allocation (optional optimization)
__device__ struct DeviceMemoryPool {
    void* pool;
    size_t pool_size;
    size_t used;
    
    __device__ DeviceMemoryPool(size_t size) {
        pool = malloc(size);
        pool_size = size;
        used = 0;
    }
    
    __device__ void* allocate(size_t size) {
        if (size == 0) {
            return nullptr;  // Invalid size
        }
        
        // Check for overflow
        if (used > pool_size - size) {
            return nullptr;  // Pool exhausted or overflow
        }
        
        if (used + size <= pool_size) {
            void* ptr = (char*)pool + used;
            used += size;
            return ptr;
        }
        return nullptr;  // Pool exhausted
    }
    
    __device__ void reset() {
        used = 0;
    }
    
    __device__ ~DeviceMemoryPool() {
        if (pool != nullptr) {
            free(pool);
        }
    }
};

