// Benchmark GEMM em CUDA C++ (linguagem compilada)
// Comparacao com MoonLight

#include <cuda_runtime.h>
#include <iostream>
#include <chrono>
#include <vector>

#define TILE_SIZE 16

__global__ void gemm_kernel(const float* A, const float* B, float* C, int N) {
    __shared__ float shared_A[TILE_SIZE * TILE_SIZE];
    __shared__ float shared_B[TILE_SIZE * TILE_SIZE];
    
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    int tid_y = threadIdx.y;
    int tid_x = threadIdx.x;
    
    float sum = 0.0f;
    
    // Loop sobre tiles
    for (int tile = 0; tile < (N + TILE_SIZE - 1) / TILE_SIZE; tile++) {
        // Carregar tile de A
        int a_row = row;
        int a_col = tile * TILE_SIZE + tid_x;
        if (a_row < N && a_col < N) {
            shared_A[tid_y * TILE_SIZE + tid_x] = A[a_row * N + a_col];
        } else {
            shared_A[tid_y * TILE_SIZE + tid_x] = 0.0f;
        }
        
        // Carregar tile de B
        int b_row = tile * TILE_SIZE + tid_y;
        int b_col = col;
        if (b_row < N && b_col < N) {
            shared_B[tid_y * TILE_SIZE + tid_x] = B[b_row * N + b_col];
        } else {
            shared_B[tid_y * TILE_SIZE + tid_x] = 0.0f;
        }
        
        __syncthreads();
        
        // Computar produto interno
        for (int k = 0; k < TILE_SIZE; k++) {
            sum += shared_A[tid_y * TILE_SIZE + k] * shared_B[k * TILE_SIZE + tid_x];
        }
        
        __syncthreads();
    }
    
    // Escrever resultado
    if (row < N && col < N) {
        C[row * N + col] = sum;
    }
}

int main() {
    const int N = 2048;  // Matriz NxN
    const size_t size = N * N * sizeof(float);
    
    // Alocar memoria CPU
    std::vector<float> h_A(N * N);
    std::vector<float> h_B(N * N);
    std::vector<float> h_C(N * N);
    
    // Inicializar
    for (int i = 0; i < N * N; i++) {
        h_A[i] = i * 0.001f;
        h_B[i] = i * 0.001f;
    }
    
    // Alocar GPU
    float *d_A, *d_B, *d_C;
    cudaMalloc(&d_A, size);
    cudaMalloc(&d_B, size);
    cudaMalloc(&d_C, size);
    
    // Transfer H->D
    cudaMemcpy(d_A, h_A.data(), size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B.data(), size, cudaMemcpyHostToDevice);
    
    // Configurar kernel
    const int block_size = 16;
    const int grid_x = (N + block_size - 1) / block_size;
    const int grid_y = (N + block_size - 1) / block_size;
    dim3 grid(grid_x, grid_y);
    dim3 block(block_size, block_size);
    
    // Criar eventos para medir tempo
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    
    // Medir tempo de execucao
    cudaEventRecord(start);
    gemm_kernel<<<grid, block>>>(d_A, d_B, d_C, N);
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    
    float elapsed_ms = 0.0f;
    cudaEventElapsedTime(&elapsed_ms, start, stop);
    
    // Transfer D->H
    cudaMemcpy(h_C.data(), d_C, size, cudaMemcpyDeviceToHost);
    
    // Calcular GFLOPs
    const long long operations = 2LL * N * N * N;  // 2*N^3
    const double elapsed_s = elapsed_ms / 1000.0;
    const double gflops = operations / elapsed_s / 1e9;
    
    std::cout << "GEMM concluido (CUDA C++)!" << std::endl;
    std::cout << "Matriz: " << N << "x" << N << std::endl;
    std::cout << "Operacoes: 2 * " << N << "^3 = " << operations << std::endl;
    std::cout << "Tempo GPU (ms): " << elapsed_ms << std::endl;
    std::cout << "GFLOPs: " << gflops << std::endl;
    
    // Cleanup
    cudaFree(d_A);
    cudaFree(d_B);
    cudaFree(d_C);
    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    
    return 0;
}

