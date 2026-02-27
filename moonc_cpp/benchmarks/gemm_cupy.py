# Benchmark GEMM em Python/CuPy (linguagem interpretada)
# Comparacao com MoonLight

import cupy as cp
import numpy as np
import time

def main():
    N = 2048  # Matriz NxN
    size = N * N
    
    # Alocar memoria CPU
    h_A = np.zeros((N, N), dtype=np.float32)
    h_B = np.zeros((N, N), dtype=np.float32)
    
    # Inicializar
    for i in range(size):
        h_A.flat[i] = i * 0.001
        h_B.flat[i] = i * 0.001
    
    # Alocar GPU
    d_A = cp.asarray(h_A)
    d_B = cp.asarray(h_B)
    
    # Sincronizar antes de medir
    cp.cuda.Stream.null.synchronize()
    
    # Criar eventos para medir tempo
    start = cp.cuda.Event()
    stop = cp.cuda.Event()
    
    # Medir tempo de execucao
    start.record()
    
    # GEMM: C = A * B
    d_C = cp.dot(d_A, d_B)
    
    stop.record()
    stop.synchronize()
    
    # Calcular tempo decorrido
    elapsed_ms = cp.cuda.get_elapsed_time(start, stop)
    
    # Transfer D->H
    h_C = cp.asnumpy(d_C)
    
    # Calcular GFLOPs
    operations = 2 * N * N * N  # 2*N^3
    elapsed_s = elapsed_ms / 1000.0
    gflops = operations / elapsed_s / 1e9
    
    print("GEMM concluido (Python/CuPy)!")
    print(f"Matriz: {N}x{N}")
    print(f"Operacoes: 2 * {N}^3 = {operations}")
    print(f"Tempo GPU (ms): {elapsed_ms}")
    print(f"GFLOPs: {gflops}")
    
    # Cleanup
    del d_A, d_B, d_C

if __name__ == "__main__":
    main()

