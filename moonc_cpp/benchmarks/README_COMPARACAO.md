# Comparativo de Performance: MoonLight vs Outras Linguagens

Este diretório contém scripts e benchmarks para comparar a performance do MoonLight com:
- **CUDA C++** (linguagem compilada)
- **Python/CuPy** (linguagem interpretada)

## Benchmarks Disponíveis

- **SAXPY**: Adição de vetores (memory-bound)
- **GEMM**: Multiplicação de matrizes (compute-bound)
- **Reduction**: Redução paralela

## Como Executar o Comparativo

### Pré-requisitos

1. **MoonLight**: Compilado e disponível em `../build/Release/moonc.exe`
2. **CUDA Toolkit**: `nvcc` no PATH
3. **Python 3**: Com `cupy` instalado (`pip install cupy-cuda11x` ou similar)

### Executar Comparativo

```powershell
# Comparar SAXPY
.\compare_performance.ps1 -Benchmark saxpy -Iterations 5

# Comparar GEMM
.\compare_performance.ps1 -Benchmark gemm -Iterations 5
```

## Interpretação dos Resultados

### Overhead vs CUDA C++
- **< 10%**: Performance excelente, muito próxima do CUDA C++
- **10-30%**: Overhead moderado, aceitável para uma linguagem de alto nível
- **> 30%**: Overhead significativo, pode precisar de otimizações

### Speedup vs Python/CuPy
- **> 1.5x**: MoonLight é significativamente mais rápido
- **1.0-1.5x**: MoonLight é mais rápido, mas com ganho moderado
- **< 1.0x**: MoonLight está mais lento (problema a investigar)

## Estrutura dos Arquivos

- `compare_performance.ps1`: Script principal de comparação
- `*_cuda.cu`: Implementações em CUDA C++
- `*_cupy.py`: Implementações em Python/CuPy
- `*.gpu`: Implementações em MoonLight

## Notas

- Os benchmarks devem usar os mesmos parâmetros (tamanho de dados, etc.)
- Múltiplas execuções são feitas para obter média, min e max
- O tempo medido é apenas do kernel GPU (usando CUDA Events)

