# Benchmark Suite - MoonLight

## Benchmarks Disponiveis

### 1. SAXPY (Adicao de Vetores)
- **Arquivo:** `saxpy.gpu`
- **Tipo:** Memory-bound
- **Metrica:** Throughput (GB/s)
- **Objetivo:** Mede largura de banda de memoria

### 2. GEMM (Multiplicacao de Matrizes)
- **Arquivo:** `gemm.gpu`
- **Tipo:** Compute-bound
- **Metrica:** GFLOPs
- **Objetivo:** Testa intensidade computacional

### 3. FFT (Transformada Rapida de Fourier)
- **Arquivo:** `fft.gpu` (a implementar)
- **Tipo:** Memory access patterns complexos
- **Metrica:** Tempo de Execucao

### 4. Reducao Paralela
- **Arquivo:** `reduction.gpu`
- **Tipo:** Sincronizacao e memoria compartilhada
- **Metrica:** Tempo de Execucao

### 5. Ordenacao Paralela
- **Arquivo:** `sort.gpu` (a implementar)
- **Tipo:** Coordenacao entre threads
- **Metrica:** Tempo de Execucao

### 6. Conv2D (Camada Convolucional)
- **Arquivo:** `conv2d.gpu` (a implementar)
- **Tipo:** Alta intensidade computacional
- **Metrica:** Giga-Ops/s

### 7. Histograma
- **Arquivo:** `histogram.gpu`
- **Tipo:** Operacoes atomicas
- **Metrica:** Tempo de Execucao

## Como Executar

### Executar Todos os Benchmarks:
```powershell
cd benchmarks
.\benchmark_suite.ps1
```

### Executar Benchmark Individual:
```powershell
cd benchmarks
..\build\Release\moonc.exe -r saxpy.gpu -v
```

### Executar Benchmark Especifico:
```powershell
.\benchmark_suite.ps1 -Benchmark "SAXPY"
```

## Metricas

- **Throughput (GB/s):** Largura de banda de memoria
- **GFLOPs:** Giga Floating Point Operations per second
- **Tempo (s):** Tempo total de execucao
- **Escalabilidade:** Performance por block/warp

## Notas

- Alguns benchmarks requerem funcionalidades ainda nao implementadas (FFT, Sort, Conv2D)
- Operacoes atomicas no histograma precisam de suporte completo
- Reducao paralela precisa de sincronizacao completa (bar.sync)

