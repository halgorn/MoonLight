# Como Comparar Performance: MoonLight vs Outras Linguagens

## 🎯 Objetivo

Comparar a performance do MoonLight com:
- **CUDA C++** (linguagem compilada - referência de performance)
- **Python/CuPy** (linguagem interpretada - comparação com linguagem de alto nível)

## 📋 Pré-requisitos

1. **MoonLight compilado**: `moonc.exe` em `../build/Release/`
2. **CUDA Toolkit**: Para compilar `*_cuda.cu` com `nvcc`
3. **Python 3** com **CuPy**: `pip install cupy-cuda11x` (ajuste para sua versão CUDA)

## 🚀 Execução Rápida

### Opção 1: Apenas MoonLight (mais simples)

```powershell
.\run_comparison.ps1 -Benchmark saxpy
```

Isso executa apenas o MoonLight e mostra os resultados.

### Opção 2: Comparação Completa (requer CUDA e Python)

```powershell
.\compare_performance.ps1 -Benchmark saxpy -Iterations 5
```

Isso executa MoonLight, CUDA C++ e Python/CuPy e compara os resultados.

## 📊 Benchmarks Disponíveis

- **saxpy**: Adição de vetores (memory-bound)
- **gemm**: Multiplicação de matrizes (compute-bound)

## 🔧 Preparação (Primeira Vez)

### 1. Compilar Benchmarks CUDA C++

```powershell
# SAXPY
nvcc -O3 -arch=sm_75 saxpy_cuda.cu -o saxpy_cuda.exe

# GEMM
nvcc -O3 -arch=sm_75 gemm_cuda.cu -o gemm_cuda.exe
```

**Nota**: Ajuste `-arch=sm_75` para sua GPU (verifique com `nvidia-smi`)

### 2. Instalar CuPy (Python)

```powershell
# Para CUDA 11.x
pip install cupy-cuda11x

# Para CUDA 12.x
pip install cupy-cuda12x
```

## 📈 Interpretação dos Resultados

### Overhead vs CUDA C++

- **< 10%**: Performance excelente! MoonLight está muito próximo do CUDA C++
- **10-30%**: Overhead moderado, aceitável para uma linguagem de alto nível
- **> 30%**: Overhead significativo, pode precisar de otimizações

### Speedup vs Python/CuPy

- **> 1.5x**: MoonLight é significativamente mais rápido
- **1.0-1.5x**: MoonLight é mais rápido, mas com ganho moderado
- **< 1.0x**: MoonLight está mais lento (problema a investigar)

## 💡 O que Esperar

### Performance Esperada

1. **MoonLight vs CUDA C++**:
   - MoonLight compila para PTX (mesmo que CUDA C++)
   - Overhead esperado: **5-20%** (devido a interpretação da AST e gerenciamento de runtime)
   - Se estiver > 30%, há espaço para otimizações

2. **MoonLight vs Python/CuPy**:
   - MoonLight deve ser **1.5-3x mais rápido**
   - Python tem overhead de interpretação e chamadas de função
   - CuPy ainda é rápido, mas MoonLight compila diretamente para PTX

### Exemplo de Saída

```
=== Relatorio Comparativo ===

MoonLight:
  Tempo Medio: 12.345 ms
  Min: 12.100 ms
  Max: 12.500 ms

CUDA C++:
  Tempo Medio: 11.200 ms
  Min: 11.000 ms
  Max: 11.400 ms
  Speedup vs MoonLight: 1.10x

Python/CuPy:
  Tempo Medio: 18.500 ms
  Min: 18.200 ms
  Max: 18.800 ms
  Speedup vs MoonLight: 1.50x

=== Analise de Performance ===
MoonLight esta com performance muito proxima do CUDA C++ (overhead: 10.2%)
MoonLight e 1.50x mais rapido que Python/CuPy
```

## 🔍 Troubleshooting

### Erro: "nvcc não encontrado"
- Instale CUDA Toolkit
- Adicione ao PATH: `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.x\bin`

### Erro: "cupy não encontrado"
- Instale: `pip install cupy-cuda11x` (ajuste versão)
- Verifique GPU: `nvidia-smi`

### Erro: "moonc.exe não encontrado"
- Compile o projeto: `cd ../build && cmake --build . --config Release`

## 📝 Notas Importantes

1. **Primeira execução pode ser mais lenta** (warm-up)
2. **Múltiplas execuções** são feitas para obter média confiável
3. **Tempo medido** é apenas do kernel GPU (usando CUDA Events)
4. **Mesmos parâmetros** são usados em todas as implementações

## 🎯 Próximos Passos

Após executar os comparativos:

1. **Analise os resultados**: MoonLight está competitivo?
2. **Identifique gargalos**: Onde está o overhead?
3. **Otimize**: Foque nas áreas com maior impacto
4. **Documente**: Registre melhorias e trade-offs

---

**Boa sorte com os testes! 🚀**

