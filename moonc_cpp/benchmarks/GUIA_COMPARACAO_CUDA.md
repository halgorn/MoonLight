# Guia Completo: Comparar MoonLight com CUDA C++

## 🎯 Resumo Rápido

Para comparar MoonLight com CUDA C++, você precisa:

1. **Compilar o benchmark CUDA C++** com `nvcc`
2. **Executar ambos** (MoonLight e CUDA C++)
3. **Comparar os tempos** de execução

## 📋 Pré-requisitos

### 1. CUDA Toolkit Instalado
- Verificar: `nvcc --version`
- Se não tiver: Baixar de https://developer.nvidia.com/cuda-downloads

### 2. Visual Studio (para compilador C++)
- nvcc precisa do `cl.exe` do Visual Studio
- VS 2019/2022 Community funciona

### 3. MoonLight Compilado
- `moonc.exe` em `../build/Release/`

## 🚀 Passo a Passo

### Passo 1: Configurar Ambiente Visual Studio

Abra PowerShell **como Administrador** e execute:

```powershell
# Para Visual Studio 2022
& "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

# OU para Visual Studio 2019
& "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"
```

**Alternativa**: Abra "Developer Command Prompt for VS" que já tem o ambiente configurado.

### Passo 2: Compilar Benchmark CUDA

```powershell
cd C:\Users\Bruno\Documents\GitHub\MoonLight\moonc_cpp\benchmarks

# Descobrir compute capability da sua GPU
nvidia-smi --query-gpu=compute_cap --format=csv

# Compilar (ajuste -arch conforme sua GPU)
nvcc -O3 -arch=sm_75 saxpy_cuda.cu -o saxpy_cuda.exe
```

**Compute Capabilities comuns:**
- RTX 20xx (Turing): `sm_75`
- RTX 30xx (Ampere): `sm_86`
- RTX 40xx (Ada): `sm_89`

### Passo 3: Executar Comparação

```powershell
# Usar script automático
.\comparar_cuda.ps1 -Benchmark saxpy

# OU manualmente:
# 1. Executar MoonLight
..\build\Release\moonc.exe -r saxpy.gpu

# 2. Executar CUDA C++
.\saxpy_cuda.exe

# 3. Comparar os tempos manualmente
```

## 📊 Exemplo de Saída Esperada

### MoonLight:
```
Compiling and executing saxpy.gpu...
Tempo GPU (ms): 12.345
Throughput (GB/s): 123.45
```

### CUDA C++:
```
SAXPY CUDA Benchmark
N = 1000000
Tempo GPU (ms): 11.200
Throughput (GB/s): 133.92
```

### Comparação:
```
=== Resultados ===
MoonLight:  12.345 ms
CUDA C++:   11.200 ms

Overhead:   10.22%
Speedup:    1.10x

Status: Performance excelente! Muito proximo do CUDA C++
```

## 🔧 Solução de Problemas

### Erro: "Cannot find compiler 'cl.exe'"

**Solução 1**: Abrir Developer Command Prompt
- Procure "Developer Command Prompt for VS" no menu Iniciar
- Execute os comandos nesse terminal

**Solução 2**: Configurar ambiente manualmente
```powershell
# No PowerShell (como Admin)
& "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
```

**Solução 3**: Adicionar ao PATH permanentemente
```powershell
# Adicionar ao PATH do sistema (ajuste versão)
$env:PATH += ";C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.xx.xxxxx\bin\Hostx64\x64"
```

### Erro: "arch=sm_XX não suportado"

Descobrir sua GPU:
```powershell
nvidia-smi --query-gpu=name,compute_cap --format=csv
```

Usar arch apropriado no nvcc.

### Erro: "moonc.exe não encontrado"

Compilar MoonLight:
```powershell
cd ..\build
cmake --build . --config Release
```

## 💡 Dicas

1. **Execute múltiplas vezes** para obter média confiável
2. **Use mesmos parâmetros** (N, tamanhos) em ambas implementações
3. **Meça apenas tempo GPU** (não inclua transferências de memória)
4. **Warm-up**: Primeira execução pode ser mais lenta

## 📝 Script Completo de Comparação

Crie `comparar_completo.ps1`:

```powershell
# Configurar ambiente Visual Studio
& "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

# Compilar CUDA
nvcc -O3 -arch=sm_75 saxpy_cuda.cu -o saxpy_cuda.exe

# Executar comparação
.\comparar_cuda.ps1 -Benchmark saxpy
```

## 🎯 Interpretação dos Resultados

### Overhead < 10%
✅ **Excelente!** MoonLight está muito próximo do CUDA C++

### Overhead 10-30%
⚠️ **Aceitável** para uma linguagem de alto nível com runtime

### Overhead > 30%
❌ **Significativo** - pode precisar de otimizações

## 📚 Arquivos Disponíveis

- `saxpy_cuda.cu` - SAXPY em CUDA C++
- `gemm_cuda.cu` - GEMM em CUDA C++
- `comparar_cuda.ps1` - Script de comparação automática
- `COMO_COMPARAR_CUDA.md` - Este guia

## 🚀 Próximos Passos

Após comparar:

1. **Analise os resultados**: MoonLight está competitivo?
2. **Identifique gargalos**: Onde está o overhead?
3. **Otimize**: Foque nas áreas com maior impacto
4. **Documente**: Registre melhorias e trade-offs

---

**Boa sorte com os testes! 🚀**

