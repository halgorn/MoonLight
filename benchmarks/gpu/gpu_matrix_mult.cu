// Pure CUDA C++ Benchmark: Matrix Multiplication
// Equivalent to gpu_matrix_mult.gpu for comparison

#include <cuda_runtime.h>
#include <iostream>
#include <chrono>

__global__ void matrix_mult(float* A, float* B, float* C, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (row < N && col < N) {
        float sum = 0.0f;
        for (int k = 0; k < N; k++) {
            sum += A[row * N + k] * B[k * N + col];
        }
        C[row * N + col] = sum;
    }
}

int main() {
    const int N = 1024;  // 1024x1024 matrices
    const int size = N * N;
    size_t bytes = size * sizeof(float);
    
    std::cout << "Matrix size: " << N << " x " << N << std::endl;
    std::cout << "Total elements: " << size << std::endl;
    std::cout << "Memory: " << bytes << " bytes per matrix" << std::endl;
    
    // Allocate host memory
    float *h_A = new float[size];
    float *h_B = new float[size];
    float *h_C = new float[size];
    
    // Initialize matrices
    for (int i = 0; i < size; i++) {
        h_A[i] = static_cast<float>(i % 100) / 100.0f;
        h_B[i] = static_cast<float>((i + 1) % 100) / 100.0f;
    }
    
    // Allocate device memory
    float *d_A, *d_B, *d_C;
    cudaMalloc(&d_A, bytes);
    cudaMalloc(&d_B, bytes);
    cudaMalloc(&d_C, bytes);
    
    std::cout << "Memory allocated on GPU" << std::endl;
    
    // Copy data to device
    auto start_transfer = std::chrono::high_resolution_clock::now();
    cudaMemcpy(d_A, h_A, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B, bytes, cudaMemcpyHostToDevice);
    auto end_transfer = std::chrono::high_resolution_clock::now();
    
    // Configure 2D grid
    int block_size = 16;
    int grid_size = (N + block_size - 1) / block_size;
    
    dim3 dimGrid(grid_size, grid_size);
    dim3 dimBlock(block_size, block_size);
    
    std::cout << "Launching kernel..." << std::endl;
    std::cout << "Grid: (" << grid_size << ", " << grid_size << ")" << std::endl;
    std::cout << "Block: (" << block_size << ", " << block_size << ")" << std::endl;
    
    // Launch kernel
    auto start_kernel = std::chrono::high_resolution_clock::now();
    matrix_mult<<<dimGrid, dimBlock>>>(d_A, d_B, d_C, N);
    cudaDeviceSynchronize();
    auto end_kernel = std::chrono::high_resolution_clock::now();
    
    std::cout << "Matrix multiplication complete!" << std::endl;
    
    // Copy result back
    auto start_back = std::chrono::high_resolution_clock::now();
    cudaMemcpy(h_C, d_C, bytes, cudaMemcpyDeviceToHost);
    auto end_back = std::chrono::high_resolution_clock::now();
    
    // Verify result (check first few elements)
    std::cout << "First element: " << h_C[0] << std::endl;
    
    // Print timing
    auto transfer_time = std::chrono::duration<double, std::milli>(end_transfer - start_transfer).count();
    auto kernel_time = std::chrono::duration<double, std::milli>(end_kernel - start_kernel).count();
    auto back_time = std::chrono::duration<double, std::milli>(end_back - start_back).count();
    
    std::cout << "\nTiming:" << std::endl;
    std::cout << "  H->D Transfer: " << transfer_time << " ms" << std::endl;
    std::cout << "  Kernel:        " << kernel_time << " ms" << std::endl;
    std::cout << "  D->H Transfer: " << back_time << " ms" << std::endl;
    std::cout << "  Total:         " << (transfer_time + kernel_time + back_time) << " ms" << std::endl;
    
    // Calculate GFLOPS
    double gflops = (2.0 * N * N * N) / (kernel_time / 1000.0) / 1e9;
    std::cout << "  Performance:   " << gflops << " GFLOPS" << std::endl;
    
    // Clean up
    cudaFree(d_A);
    cudaFree(d_B);
    cudaFree(d_C);
    delete[] h_A;
    delete[] h_B;
    delete[] h_C;
    
    std::cout << "Benchmark complete!" << std::endl;
    
    return 0;
}

