// Pure CUDA C++ Benchmark: Vector Addition
// Equivalent to gpu_vector_add.gpu for comparison

#include <cuda_runtime.h>
#include <iostream>
#include <chrono>

__global__ void vector_add(float* a, float* b, float* c, int n) {
    int i = threadIdx.x + blockIdx.x * blockDim.x;
    if (i < n) {
        c[i] = a[i] + b[i];
    }
}

int main() {
    const int n = 10000000;  // 10 million elements
    size_t size = n * sizeof(float);
    
    std::cout << "Allocating memory..." << std::endl;
    
    // Allocate host memory
    float *h_a = new float[n];
    float *h_b = new float[n];
    float *h_c = new float[n];
    
    // Initialize host arrays
    for (int i = 0; i < n; i++) {
        h_a[i] = static_cast<float>(i);
        h_b[i] = static_cast<float>(i * 2);
    }
    
    // Allocate device memory
    float *d_a, *d_b, *d_c;
    cudaMalloc(&d_a, size);
    cudaMalloc(&d_b, size);
    cudaMalloc(&d_c, size);
    
    std::cout << "Transferring data to GPU..." << std::endl;
    auto start_transfer = std::chrono::high_resolution_clock::now();
    
    // Copy data to device
    cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, h_b, size, cudaMemcpyHostToDevice);
    
    auto end_transfer = std::chrono::high_resolution_clock::now();
    
    // Launch kernel
    int threads_per_block = 256;
    int blocks = (n + threads_per_block - 1) / threads_per_block;
    
    std::cout << "Launching kernel..." << std::endl;
    std::cout << "Grid: " << blocks << " blocks x " << threads_per_block << " threads" << std::endl;
    
    auto start_kernel = std::chrono::high_resolution_clock::now();
    
    vector_add<<<blocks, threads_per_block>>>(d_a, d_b, d_c, n);
    cudaDeviceSynchronize();
    
    auto end_kernel = std::chrono::high_resolution_clock::now();
    
    std::cout << "Kernel completed!" << std::endl;
    
    // Copy result back
    auto start_back = std::chrono::high_resolution_clock::now();
    cudaMemcpy(h_c, d_c, size, cudaMemcpyDeviceToHost);
    auto end_back = std::chrono::high_resolution_clock::now();
    
    // Verify result
    bool correct = true;
    for (int i = 0; i < 10; i++) {
        if (h_c[i] != h_a[i] + h_b[i]) {
            correct = false;
            break;
        }
    }
    std::cout << "Result: " << (correct ? "CORRECT" : "INCORRECT") << std::endl;
    
    // Print timing
    auto transfer_time = std::chrono::duration<double, std::milli>(end_transfer - start_transfer).count();
    auto kernel_time = std::chrono::duration<double, std::milli>(end_kernel - start_kernel).count();
    auto back_time = std::chrono::duration<double, std::milli>(end_back - start_back).count();
    
    std::cout << "\nTiming:" << std::endl;
    std::cout << "  H->D Transfer: " << transfer_time << " ms" << std::endl;
    std::cout << "  Kernel:        " << kernel_time << " ms" << std::endl;
    std::cout << "  D->H Transfer: " << back_time << " ms" << std::endl;
    std::cout << "  Total:         " << (transfer_time + kernel_time + back_time) << " ms" << std::endl;
    
    // Clean up
    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);
    delete[] h_a;
    delete[] h_b;
    delete[] h_c;
    
    std::cout << "Benchmark complete!" << std::endl;
    
    return 0;
}

