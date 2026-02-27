// MoonLight Multi-GPU Runtime Utilities
// Provides P2P transfers, topology detection, and load balancing

#include <cuda_runtime.h>
#include <stdio.h>

// GPU topology information
struct GPUTopology {
    int num_gpus;
    int devices[8];  // Max 8 GPUs
    int p2p_matrix[8][8];  // P2P capability matrix
    int nvlink_matrix[8][8];  // NVLink connectivity
};

// Detect GPU topology
extern "C" GPUTopology detect_gpu_topology() {
    GPUTopology topo;
    topo.num_gpus = 0;
    
    // Initialize matrices
    for (int i = 0; i < 8; i++) {
        topo.devices[i] = -1;  // Invalid device
        for (int j = 0; j < 8; j++) {
            topo.p2p_matrix[i][j] = 0;
            topo.nvlink_matrix[i][j] = 0;
        }
    }
    
    cudaError_t err = cudaGetDeviceCount(&topo.num_gpus);
    if (err != cudaSuccess) {
        fprintf(stderr, "Error detecting GPU count: %s\n", cudaGetErrorString(err));
        return topo;
    }
    
    if (topo.num_gpus == 0) {
        fprintf(stderr, "Warning: No CUDA devices found\n");
        return topo;
    }
    
    if (topo.num_gpus > 8) {
        fprintf(stderr, "Warning: More than 8 GPUs detected, only first 8 will be used\n");
        topo.num_gpus = 8;
    }
    
    // Check P2P capabilities
    for (int i = 0; i < topo.num_gpus; i++) {
        topo.devices[i] = i;
        for (int j = 0; j < topo.num_gpus; j++) {
            if (i != j) {
                int canAccessPeer = 0;
                err = cudaDeviceCanAccessPeer(&canAccessPeer, i, j);
                if (err == cudaSuccess) {
                    topo.p2p_matrix[i][j] = canAccessPeer;
                } else {
                    fprintf(stderr, "Warning: Error checking P2P capability between GPU %d and %d: %s\n", 
                            i, j, cudaGetErrorString(err));
                    topo.p2p_matrix[i][j] = 0;
                }
            }
        }
    }
    
    return topo;
}

// Enable P2P access between two GPUs
extern "C" int enable_p2p_access(int gpu0, int gpu1) {
    // Validate GPU indices
    int num_gpus;
    cudaError_t err = cudaGetDeviceCount(&num_gpus);
    if (err != cudaSuccess) {
        fprintf(stderr, "Error getting device count: %s\n", cudaGetErrorString(err));
        return 0;
    }
    
    if (gpu0 < 0 || gpu0 >= num_gpus) {
        fprintf(stderr, "Error: Invalid GPU index %d (valid range: 0-%d)\n", gpu0, num_gpus - 1);
        return 0;
    }
    
    if (gpu1 < 0 || gpu1 >= num_gpus) {
        fprintf(stderr, "Error: Invalid GPU index %d (valid range: 0-%d)\n", gpu1, num_gpus - 1);
        return 0;
    }
    
    if (gpu0 == gpu1) {
        fprintf(stderr, "Warning: Cannot enable P2P access between GPU and itself (%d)\n", gpu0);
        return 0;
    }
    
    int canAccessPeer = 0;
    err = cudaDeviceCanAccessPeer(&canAccessPeer, gpu0, gpu1);
    if (err != cudaSuccess) {
        fprintf(stderr, "Error checking P2P capability: %s\n", cudaGetErrorString(err));
        return 0;
    }
    
    if (!canAccessPeer) {
        fprintf(stderr, "Warning: P2P access not supported between GPU %d and GPU %d\n", gpu0, gpu1);
        return 0;  // P2P not supported
    }
    
    err = cudaSetDevice(gpu0);
    if (err != cudaSuccess) {
        fprintf(stderr, "Error setting device %d: %s\n", gpu0, cudaGetErrorString(err));
        return 0;
    }
    
    err = cudaDeviceEnablePeerAccess(gpu1, 0);
    
    if (err != cudaSuccess && err != cudaErrorPeerAccessAlreadyEnabled) {
        fprintf(stderr, "Error enabling P2P access: %s\n", cudaGetErrorString(err));
        return 0;  // Failed to enable
    }
    
    return 1;  // Success
}

// P2P memory copy (GPU to GPU direct)
extern "C" cudaError_t p2p_memcpy(void* dst, int dst_device, 
                                   const void* src, int src_device,
                                   size_t count, cudaStream_t stream) {
    // Validate parameters
    if (dst == nullptr) {
        fprintf(stderr, "Error: Destination pointer is null\n");
        return cudaErrorInvalidValue;
    }
    
    if (src == nullptr) {
        fprintf(stderr, "Error: Source pointer is null\n");
        return cudaErrorInvalidValue;
    }
    
    if (count == 0) {
        return cudaSuccess;  // Nothing to copy
    }
    
    int num_gpus;
    cudaError_t err = cudaGetDeviceCount(&num_gpus);
    if (err != cudaSuccess) {
        fprintf(stderr, "Error getting device count: %s\n", cudaGetErrorString(err));
        return err;
    }
    
    if (dst_device < 0 || dst_device >= num_gpus) {
        fprintf(stderr, "Error: Invalid destination GPU index %d\n", dst_device);
        return cudaErrorInvalidDevice;
    }
    
    if (src_device < 0 || src_device >= num_gpus) {
        fprintf(stderr, "Error: Invalid source GPU index %d\n", src_device);
        return cudaErrorInvalidDevice;
    }
    
    err = cudaSetDevice(dst_device);
    if (err != cudaSuccess) {
        fprintf(stderr, "Error setting destination device %d: %s\n", dst_device, cudaGetErrorString(err));
        return err;
    }
    
    err = cudaMemcpyPeerAsync(dst, dst_device, src, src_device, count, stream);
    if (err != cudaSuccess) {
        fprintf(stderr, "Error in P2P memory copy: %s\n", cudaGetErrorString(err));
    }
    
    return err;
}

// Automatic data partitioning for multi-GPU
extern "C" void partition_data_multi_gpu(int num_gpus, size_t total_size,
                                          size_t* sizes, size_t* offsets) {
    size_t chunk_size = total_size / num_gpus;
    size_t remainder = total_size % num_gpus;
    
    size_t offset = 0;
    for (int i = 0; i < num_gpus; i++) {
        sizes[i] = chunk_size + (i < remainder ? 1 : 0);
        offsets[i] = offset;
        offset += sizes[i];
    }
}

// Work stealing queue for multi-GPU load balancing
struct WorkStealingQueue {
    int* work_items;
    int front;
    int back;
    int size;
    int capacity;
};

extern "C" WorkStealingQueue* create_work_queue(int capacity) {
    if (capacity <= 0) {
        fprintf(stderr, "Error: Work queue capacity must be > 0, got %d\n", capacity);
        return nullptr;
    }
    
    if (capacity > 1000000) {  // Reasonable limit
        fprintf(stderr, "Error: Work queue capacity too large: %d\n", capacity);
        return nullptr;
    }
    
    WorkStealingQueue* queue = (WorkStealingQueue*)malloc(sizeof(WorkStealingQueue));
    if (queue == nullptr) {
        fprintf(stderr, "Error: Failed to allocate work queue structure\n");
        return nullptr;
    }
    
    queue->work_items = (int*)malloc(capacity * sizeof(int));
    if (queue->work_items == nullptr) {
        fprintf(stderr, "Error: Failed to allocate work queue items array\n");
        free(queue);
        return nullptr;
    }
    
    queue->front = 0;
    queue->back = 0;
    queue->size = 0;
    queue->capacity = capacity;
    return queue;
}

extern "C" void enqueue_work(WorkStealingQueue* queue, int item) {
    if (queue->size < queue->capacity) {
        queue->work_items[queue->back] = item;
        queue->back = (queue->back + 1) % queue->capacity;
        queue->size++;
    }
}

extern "C" int dequeue_work(WorkStealingQueue* queue) {
    if (queue->size > 0) {
        int item = queue->work_items[queue->front];
        queue->front = (queue->front + 1) % queue->capacity;
        queue->size--;
        return item;
    }
    return -1;  // Empty
}

extern "C" void free_work_queue(WorkStealingQueue* queue) {
    if (queue) {
        free(queue->work_items);
        free(queue);
    }
}

