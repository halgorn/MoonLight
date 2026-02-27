#include "../../gpu_runtime/queue.cuh"
#include <iostream>
#include <cstdlib>

struct Task {
    int id;
    float data[4];
};

__global__ void producer(GPUQueue<Task>* queue, int n) {
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    
    if (tid < n) {
        Task task;
        task.id = tid;
        for (int i = 0; i < 4; i++) {
            task.data[i] = (float)tid + i * 0.1f;
        }
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

__global__ void test_concurrent(GPUQueue<Task>* queue, int* results, int n) {
    int tid = threadIdx.x + blockIdx.x * blockDim.x;
    
    if (tid < n) {
        // Half threads produce
        if (tid < n / 2) {
            Task task;
            task.id = tid;
            queue->enqueue(task);
        }
        __syncthreads();
        
        // Half threads consume
        if (tid >= n / 2) {
            Task task = queue->dequeue_wait();
            results[tid - n / 2] = task.id;
        }
    }
}

int main() {
    const int N = 1000;
    bool all_tests_passed = true;
    
    std::cout << "GPU Work Queue Test Suite\n";
    std::cout << "==========================\n\n";
    
    // Test 1: Basic producer-consumer
    std::cout << "Test 1: Basic producer-consumer...  ";
    {
        auto queue = create_gpu_queue<Task>(2048);
        
        int* d_results;
        cudaMalloc(&d_results, N * sizeof(int));
        cudaMemset(d_results, 0, N * sizeof(int));
        
        // Launch producer and consumer concurrently
        producer<<<4, 256>>>(queue, N);
        consumer<<<4, 256>>>(queue, d_results, N);
        
        cudaDeviceSynchronize();
        
        // Verify
        int* h_results = new int[N];
        cudaMemcpy(h_results, d_results, N * sizeof(int), cudaMemcpyDeviceToHost);
        
        bool success = true;
        bool* found = new bool[N]();
        for (int i = 0; i < N; i++) {
            if (h_results[i] < 0 || h_results[i] >= N) {
                success = false;
                break;
            }
            found[h_results[i]] = true;
        }
        
        // Check all IDs were processed
        for (int i = 0; i < N; i++) {
            if (!found[i]) {
                success = false;
                break;
            }
        }
        
        std::cout << (success ? "PASSED" : "FAILED") << std::endl;
        all_tests_passed &= success;
        
        delete[] h_results;
        delete[] found;
        cudaFree(d_results);
        destroy_gpu_queue(queue);
    }
    
    // Test 2: Concurrent producer-consumer in same kernel
    std::cout << "Test 2: Concurrent operations...    ";
    {
        auto queue = create_gpu_queue<Task>(2048);
        
        int* d_results;
        cudaMalloc(&d_results, N / 2 * sizeof(int));
        cudaMemset(d_results, 0, N / 2 * sizeof(int));
        
        test_concurrent<<<4, 256>>>(queue, d_results, N);
        
        cudaDeviceSynchronize();
        
        // Verify
        int* h_results = new int[N / 2];
        cudaMemcpy(h_results, d_results, N / 2 * sizeof(int), cudaMemcpyDeviceToHost);
        
        bool success = true;
        for (int i = 0; i < N / 2; i++) {
            if (h_results[i] < 0 || h_results[i] >= N / 2) {
                success = false;
                break;
            }
        }
        
        std::cout << (success ? "PASSED" : "FAILED") << std::endl;
        all_tests_passed &= success;
        
        delete[] h_results;
        cudaFree(d_results);
        destroy_gpu_queue(queue);
    }
    
    // Test 3: Host enqueue/dequeue
    std::cout << "Test 3: Host operations...           ";
    {
        auto queue = create_gpu_queue<Task>(128);
        
        bool success = true;
        
        // Enqueue from host
        for (int i = 0; i < 10; i++) {
            Task task;
            task.id = i;
            if (!enqueue_from_host(queue, task)) {
                success = false;
                break;
            }
        }
        
        // Dequeue to host
        for (int i = 0; i < 10; i++) {
            Task task;
            if (!dequeue_to_host(queue, &task)) {
                success = false;
                break;
            }
            if (task.id != i) {
                success = false;
                break;
            }
        }
        
        std::cout << (success ? "PASSED" : "FAILED") << std::endl;
        all_tests_passed &= success;
        
        destroy_gpu_queue(queue);
    }
    
    // Final result
    std::cout << "\n==========================\n";
    std::cout << "Overall: " << (all_tests_passed ? "ALL TESTS PASSED ✓" : "SOME TESTS FAILED ✗") << std::endl;
    
    return all_tests_passed ? 0 : 1;
}

