#ifndef MOONLIGHT_RUNTIME_H
#define MOONLIGHT_RUNTIME_H

#include <cuda_runtime.h>
#include <stdio.h>

// Função para alocar memória na GPU
inline void* gpu_malloc(size_t size) {
    void* ptr;
    cudaError_t err = cudaMalloc(&ptr, size);
    if(err != cudaSuccess) {
        fprintf(stderr, "Erro ao alocar memória na GPU: %s\n", cudaGetErrorString(err));
        return nullptr;
    }
    return ptr;
}

// Função para liberar memória na GPU
inline void gpu_free(void* ptr) {
    cudaFree(ptr);
}

// Funções de I/O
inline void print_int(int value) {
    printf("%d\n", value);
}

inline void print_str(const char* str) {
    printf("%s\n", str);
}

#endif // MOONLIGHT_RUNTIME_H
