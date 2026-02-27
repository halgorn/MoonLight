# Benchmark SAXPY em Python/CuPy (linguagem interpretada)
# Comparacao com MoonLight

import cupy as cp
import numpy as np
import time

def main():
    n = 10000000  # 10M elementos
    a = 2.5
    
    # Alocar memoria CPU
    h_x = np.zeros(n, dtype=np.float32)
    h_y = np.zeros(n, dtype=np.float32)
    
    # Inicializar
    for i in range(n):
        h_x[i] = i * 0.001
        h_y[i] = i * 0.002
    
    # Alocar GPU
    d_x = cp.asarray(h_x)
    d_y = cp.asarray(h_y)
    
    # Sincronizar antes de medir
    cp.cuda.Stream.null.synchronize()
    
    # Criar eventos para medir tempo
    start = cp.cuda.Event()
    stop = cp.cuda.Event()
    
    # Medir tempo de execucao
    start.record()
    
    # SAXPY: y = a * x + y
    d_y = a * d_x + d_y
    
    stop.record()
    stop.synchronize()
    
    # Calcular tempo decorrido
    elapsed_ms = cp.cuda.get_elapsed_time(start, stop)
    
    # Transfer D->H
    h_y = cp.asnumpy(d_y)
    
    # Calcular throughput
    bytes_transferred = 3 * n * 4  # 3 arrays * n elementos * 4 bytes
    throughput_gbs = bytes_transferred / (elapsed_ms / 1000.0) / 1e9
    
    print("SAXPY concluido (Python/CuPy)!")
    print(f"Elementos: {n}")
    print(f"Tempo GPU (ms): {elapsed_ms}")
    print(f"Throughput (GB/s): {throughput_gbs}")
    
    # Cleanup
    del d_x, d_y

if __name__ == "__main__":
    main()

