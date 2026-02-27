# Como Usar os Benchmarks

## Executar Todos os Benchmarks

```powershell
cd moonc_cpp
cd benchmarks
.\benchmark_suite.ps1
```

Ou de qualquer lugar:
```powershell
cd moonc_cpp\benchmarks
.\benchmark_suite.ps1
```

## Executar Benchmark Individual

### Opcao 1: Usando o script
```powershell
cd moonc_cpp\benchmarks
.\run_benchmark.ps1 -Benchmark "SAXPY"
.\run_benchmark.ps1 -Benchmark "GEMM"
.\run_benchmark.ps1 -Benchmark "HISTOGRAM"
```

### Opcao 2: Diretamente
```powershell
cd moonc_cpp
.\build\Release\moonc.exe -r benchmarks\saxpy.gpu -v
.\build\Release\moonc.exe -r benchmarks\gemm.gpu -v
```

## Benchmarks Disponiveis

| Benchmark | Arquivo | Tipo | Metrica |
|-----------|---------|------|---------|
| SAXPY | saxpy.gpu | Memory-bound | Throughput (GB/s) |
| GEMM | gemm.gpu | Compute-bound | GFLOPs |
| FFT | fft.gpu | Memory patterns | Tempo (s) |
| Reduction | reduction.gpu | Sincronizacao | Tempo (s) |
| Sort | sort.gpu | Coordenacao | Tempo (s) |
| Conv2D | conv2d.gpu | Compute-intensive | Giga-Ops/s |
| Histogram | histogram.gpu | Atomicas | Tempo (s) |

## Interpretar Resultados

### SAXPY (Throughput)
- **Bom:** >100 GB/s
- **Medio:** 50-100 GB/s
- **Baixo:** <50 GB/s

### GEMM (GFLOPs)
- **Bom:** >500 GFLOPs
- **Medio:** 100-500 GFLOPs
- **Baixo:** <100 GFLOPs

### Tempo de Execucao
- Compare com implementacoes CUDA C++ nativas
- Menor tempo = melhor performance

## Troubleshooting

### Se um benchmark nao executar:
- Verifique se o arquivo .gpu existe
- Verifique se ha erros de sintaxe: `.\build\Release\moonc.exe -c benchmarks\saxpy.gpu`
- Alguns benchmarks podem precisar de funcionalidades ainda nao implementadas

### Se demorar muito:
- Normal para benchmarks grandes (GEMM, FFT)
- Aguarde alguns segundos
- Se travar, pode haver erro no parser

