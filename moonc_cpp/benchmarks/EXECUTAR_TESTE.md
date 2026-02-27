# Como Executar o Teste de Performance

## Status Atual

Foi criado um sistema completo de comparação de performance, mas há um problema com a captura de saída no PowerShell que impede a execução automática completa.

## Solução: Executar Manualmente

### Opção 1: Executar Diretamente no Terminal

```powershell
cd C:\Users\Bruno\Documents\GitHub\MoonLight\moonc_cpp\benchmarks
..\build\Release\moonc.exe -r saxpy.gpu
```

Isso deve mostrar a saída completa com:
- Tempo GPU (ms)
- Throughput (GB/s)

### Opção 2: Executar Múltiplas Vezes Manualmente

Para obter média, execute 3-5 vezes e anote os tempos:

```powershell
# Execução 1
..\build\Release\moonc.exe -r saxpy.gpu

# Execução 2
..\build\Release\moonc.exe -r saxpy.gpu

# Execução 3
..\build\Release\moonc.exe -r saxpy.gpu
```

### Opção 3: Usar CMD em vez de PowerShell

Abra CMD e execute:

```cmd
cd C:\Users\Bruno\Documents\GitHub\MoonLight\moonc_cpp\benchmarks
..\build\Release\moonc.exe -r saxpy.gpu
```

## Comparação com Outras Linguagens

### 1. Compilar CUDA C++ (se disponível)

```powershell
nvcc -O3 -arch=sm_75 saxpy_cuda.cu -o saxpy_cuda.exe
.\saxpy_cuda.exe
```

### 2. Executar Python/CuPy (se disponível)

```powershell
python saxpy_cupy.py
```

## O que Esperar

### Saída Esperada do MoonLight:

```
Compiling and executing saxpy.gpu...
[SUCCESS] PTX loaded on GPU successfully
Executing program...
SAXPY concluido!
Elementos: 10000000
Tempo GPU (ms): 12.345
Throughput (GB/s): 9.678
[SUCCESS] Program executed successfully
```

### Análise de Performance

- **Tempo GPU**: Deve ser similar ao CUDA C++ (overhead esperado: 5-20%)
- **Throughput**: Deve estar próximo do CUDA C++
- **Comparação**: MoonLight deve ser 1.5-3x mais rápido que Python/CuPy

## Troubleshooting

### Se não aparecer saída:

1. Verifique se há erros silenciosos
2. Tente executar com `-v` para verbose:
   ```powershell
   ..\build\Release\moonc.exe -r saxpy.gpu -v
   ```

3. Verifique se a GPU está disponível:
   ```powershell
   nvidia-smi
   ```

### Se houver erro de CUDA:

- Verifique se CUDA está instalado
- Verifique se a GPU é compatível
- Tente executar um teste mais simples primeiro

## Próximos Passos

Após executar manualmente e obter os resultados:

1. **Anote os tempos** de cada execução
2. **Compare com CUDA C++** (se disponível)
3. **Compare com Python/CuPy** (se disponível)
4. **Analise o overhead** do MoonLight vs CUDA C++
5. **Identifique oportunidades de otimização**

## Arquivos Disponíveis

- `saxpy.gpu` - Benchmark MoonLight
- `saxpy_cuda.cu` - Benchmark CUDA C++
- `saxpy_cupy.py` - Benchmark Python/CuPy
- `gemm.gpu` - GEMM MoonLight
- `gemm_cuda.cu` - GEMM CUDA C++
- `gemm_cupy.py` - GEMM Python/CuPy

---

**Execute manualmente e compartilhe os resultados para análise!**

