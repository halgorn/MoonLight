# Suite de Benchmarks - MoonLight

## Correcoes Aplicadas

1. **Encoding corrigido** - Caracteres especiais agora aparecem corretamente
2. **7 benchmarks criados** - Todos os tipos de teste solicitados
3. **Scripts de execucao** - Facilita rodar benchmarks individuais ou todos

## Benchmarks Disponiveis

### 1. SAXPY (Adicao de Vetores)
- **Arquivo:** `benchmarks/saxpy.gpu`
- **Tipo:** Memory-bound
- **Metrica:** Throughput (GB/s)
- **Executar:** `.\run_benchmark.ps1 -Benchmark SAXPY`

### 2. GEMM (Multiplicacao de Matrizes)
- **Arquivo:** `benchmarks/gemm.gpu`
- **Tipo:** Compute-bound
- **Metrica:** GFLOPs
- **Executar:** `.\run_benchmark.ps1 -Benchmark GEMM`

### 3. FFT (Transformada Rapida de Fourier)
- **Arquivo:** `benchmarks/fft.gpu`
- **Tipo:** Memory patterns complexos
- **Metrica:** Tempo (s)
- **Executar:** `.\run_benchmark.ps1 -Benchmark FFT`

### 4. Reducao Paralela
- **Arquivo:** `benchmarks/reduction.gpu`
- **Tipo:** Sincronizacao e memoria compartilhada
- **Metrica:** Tempo (s)
- **Executar:** `.\run_benchmark.ps1 -Benchmark REDUCTION`

### 5. Ordenacao Paralela
- **Arquivo:** `benchmarks/sort.gpu`
- **Tipo:** Coordenacao entre threads
- **Metrica:** Tempo (s)
- **Executar:** `.\run_benchmark.ps1 -Benchmark SORT`

### 6. Conv2D (Camada Convolucional)
- **Arquivo:** `benchmarks/conv2d.gpu`
- **Tipo:** Compute-intensive
- **Metrica:** Giga-Ops/s
- **Executar:** `.\run_benchmark.ps1 -Benchmark CONV2D`

### 7. Histograma
- **Arquivo:** `benchmarks/histogram.gpu`
- **Tipo:** Operacoes atomicas
- **Metrica:** Tempo (s)
- **Executar:** `.\run_benchmark.ps1 -Benchmark HISTOGRAM`

## Como Executar

### Executar Todos os Benchmarks:
```powershell
cd moonc_cpp
cd benchmarks
.\benchmark_suite.ps1
```

### Executar Benchmark Individual:
```powershell
cd moonc_cpp\benchmarks
.\run_benchmark.ps1 -Benchmark SAXPY
```

### Executar Diretamente:
```powershell
cd moonc_cpp
.\build\Release\moonc.exe -r benchmarks\saxpy.gpu -v
```

## Benchmark Basico (Original)
```powershell
cd moonc_cpp
.\benchmark.ps1
```

## Notas Importantes

- Alguns benchmarks podem precisar de funcionalidades ainda nao implementadas completamente
- Operacoes atomicas no histograma precisam de suporte completo
- Reducao paralela precisa de sincronizacao completa (bar.sync)
- FFT e Sort sao versoes simplificadas - implementacoes completas requerem mais funcionalidades

## Interpretacao de Resultados

- **Throughput (GB/s):** Quanto maior, melhor (objetivo: >100 GB/s)
- **GFLOPs:** Quanto maior, melhor (objetivo: >500 GFLOPs)
- **Tempo (s):** Quanto menor, melhor
- Compare com implementacoes CUDA C++ nativas para referencia

