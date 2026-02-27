// Benchmark SAXPY em CUDA C++ (linguagem compilada)
// Comparacao com MoonLight

#include <cuda_runtime.h>
#include <iostream>
#include <chrono>
#include <vector>

__global__ void saxpy_kernel(float* x, float* y, float a, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        y[i] = a * x[i] + y[i];
    }
}

int main() {
    const int n = 10000000;  // 10M elementos
    const float a = 2.5f;
    const size_t size = n * sizeof(float);
    
    // Alocar memoria CPU
    std::vector<float> h_x(n);
    std::vector<float> h_y(n);
    
    // Inicializar
    for (int i = 0; i < n; i++) {
        h_x[i] = i * 0.001f;
        h_y[i] = i * 0.002f;
    }
    
    // Alocar GPU
    float *d_x, *d_y;
    cudaMalloc(&d_x, size);
    cudaMalloc(&d_y, size);
    
    // Transfer H->D
    cudaMemcpy(d_x, h_x.data(), size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_y, h_y.data(), size, cudaMemcpyHostToDevice);
    
    // Configurar kernel
    const int threads = 256;
    const int blocks = (n + threads - 1) / threads;
    
    // Criar eventos para medir tempo
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    
    // Medir tempo de execucao
    cudaEventRecord(start);
    saxpy_kernel<<<blocks, threads>>>(d_x, d_y, a, n);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    
    float elapsed_ms = 0.0f;
    cudaEventElapsedTime(&elapsed_ms, start, stop);
    
    // Transfer D->H
    cudaMemcpy(h_y.data(), d_y, size, cudaMemcpyDeviceToHost);
    
    // Calcular throughput
    const double bytes_transferred = 3.0 * n * sizeof(float);
    const double throughput_gbs = bytes_transferred / (elapsed_ms / 1000.0) / 1e9;
    
    std::cout << "SAXPY concluido (CUDA C++)!" << std::endl;
    std::cout << "Elementos: " << n << std::endl;
    std::cout << "Tempo GPU (ms): " << elapsed_ms << std::endl;
    std::cout << "Throughput (GB/s): " << throughput_gbs << std::endl;
    
    // Cleanup
    cudaFree(d_x);
    cudaFree(d_y);
    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    
    return 0;
}

