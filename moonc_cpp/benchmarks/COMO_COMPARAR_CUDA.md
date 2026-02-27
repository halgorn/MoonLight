# Como Comparar MoonLight com CUDA C++

## 🎯 Guia Rápido

### Passo 1: Verificar Pré-requisitos

```powershell
# Verificar se nvcc está disponível
nvcc --version

# Verificar se moonc.exe existe
Test-Path ..\build\Release\moonc.exe
```

### Passo 2: Compilar Benchmark CUDA C++

```powershell
# Para SAXPY
nvcc -O3 -arch=sm_75 saxpy_cuda.cu -o saxpy_cuda.exe

# Para GEMM
nvcc -O3 -arch=sm_75 gemm_cuda.cu -o gemm_cuda.exe
```

**Nota**: Ajuste `-arch=sm_75` para sua GPU:
- RTX 20xx/30xx: `sm_75` ou `sm_86`
- RTX 40xx: `sm_89`
- Verifique com: `nvidia-smi` ou `nvcc --help`

### Passo 3: Executar Comparação

#### Opção A: Script Automático (Recomendado)

```powershell
.\compare_performance.ps1 -Benchmark saxpy -Iterations 5
```

#### Opção B: Manual

```powershell
# 1. Executar MoonLight
..\build\Release\moonc.exe -r saxpy.gpu

# 2. Executar CUDA C++
.\saxpy_cuda.exe

# 3. Comparar os tempos manualmente
```

## 📊 Exemplo de Comparação Manual

### 1. Executar MoonLight

```powershell
cd moonc_cpp\benchmarks
..\build\Release\moonc.exe -r saxpy.gpu
```

**Saída esperada:**
```
Compiling and executing saxpy.gpu...
Tempo GPU (ms): 12.345
Throughput (GB/s): 123.45
```

### 2. Executar CUDA C++

```powershell
.\saxpy_cuda.exe
```

**Saída esperada:**
```
SAXPY CUDA Benchmark
N = 1000000
Tempo GPU (ms): 11.200
Throughput (GB/s): 133.92
```

### 3. Calcular Overhead

```
Overhead = (Tempo_MoonLight - Tempo_CUDA) / Tempo_CUDA * 100
Overhead = (12.345 - 11.200) / 11.200 * 100 = 10.2%
```

## 🔧 Script de Comparação Automática

Crie um script simples `comparar_cuda.ps1`:

```powershell
param([string]$Benchmark = "saxpy")

$moonc = "..\build\Release\moonc.exe"
$cuda_exe = "${Benchmark}_cuda.exe"

Write-Host "=== Comparacao: MoonLight vs CUDA C++ ===" -ForegroundColor Cyan
Write-Host "Benchmark: $Benchmark" -ForegroundColor Yellow
Write-Host ""

# Executar MoonLight
Write-Host "1. Executando MoonLight..." -ForegroundColor Green
$ml_output = & $moonc -r "${Benchmark}.gpu" 2>&1
$ml_time = if ($ml_output -match "Tempo GPU \(ms\):\s*([\d.]+)") { [double]$Matches[1] } else { $null }

# Executar CUDA C++
Write-Host "2. Executando CUDA C++..." -ForegroundColor Green
if (Test-Path $cuda_exe) {
    $cuda_output = & ".\$cuda_exe" 2>&1
    $cuda_time = if ($cuda_output -match "Tempo GPU \(ms\):\s*([\d.]+)") { [double]$Matches[1] } else { $null }
} else {
    Write-Host "  Arquivo $cuda_exe nao encontrado!" -ForegroundColor Red
    Write-Host "  Compile primeiro: nvcc -O3 -arch=sm_75 ${Benchmark}_cuda.cu -o $cuda_exe" -ForegroundColor Yellow
    exit 1
}

# Comparar
Write-Host ""
Write-Host "=== Resultados ===" -ForegroundColor Cyan
if ($ml_time -and $cuda_time) {
    Write-Host "MoonLight:  $ml_time ms" -ForegroundColor White
    Write-Host "CUDA C++:   $cuda_time ms" -ForegroundColor White
    
    $overhead = (($ml_time - $cuda_time) / $cuda_time) * 100
    $speedup = $cuda_time / $ml_time
    
    Write-Host ""
    Write-Host "Overhead:   $([math]::Round($overhead, 2))%" -ForegroundColor $(if ($overhead -lt 10) { "Green" } elseif ($overhead -lt 30) { "Yellow" } else { "Red" })
    Write-Host "Speedup:    $([math]::Round($speedup, 2))x" -ForegroundColor $(if ($speedup -gt 1.1) { "Green" } else { "Yellow" })
    
    if ($overhead -lt 10) {
        Write-Host "Status: Performance excelente! Muito proximo do CUDA C++" -ForegroundColor Green
    } elseif ($overhead -lt 30) {
        Write-Host "Status: Overhead moderado, aceitavel" -ForegroundColor Yellow
    } else {
        Write-Host "Status: Overhead significativo, pode precisar de otimizacoes" -ForegroundColor Red
    }
} else {
    Write-Host "Nao foi possivel extrair tempos da saida" -ForegroundColor Red
    Write-Host "MoonLight output:" -ForegroundColor Yellow
    $ml_output | Select-Object -Last 10
    Write-Host "CUDA output:" -ForegroundColor Yellow
    $cuda_output | Select-Object -Last 10
}
```

## 🚀 Execução Rápida

```powershell
# 1. Compilar CUDA (apenas primeira vez)
nvcc -O3 -arch=sm_75 saxpy_cuda.cu -o saxpy_cuda.exe

# 2. Executar comparação
.\comparar_cuda.ps1 -Benchmark saxpy
```

## 📈 Interpretação dos Resultados

### Overhead < 10%
✅ **Excelente!** MoonLight está muito próximo do CUDA C++

### Overhead 10-30%
⚠️ **Aceitável** para uma linguagem de alto nível com runtime

### Overhead > 30%
❌ **Significativo** - pode precisar de otimizações no compilador/runtime

## 🔍 Troubleshooting

### Erro: "nvcc não encontrado"
```powershell
# Adicionar CUDA ao PATH (ajuste versão)
$env:PATH += ";C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0\bin"
```

### Erro: "arch=sm_XX não suportado"
```powershell
# Verificar compute capability da GPU
nvidia-smi --query-gpu=compute_cap --format=csv

# Usar arch apropriado:
# sm_75 = Turing (RTX 20xx)
# sm_86 = Ampere (RTX 30xx)
# sm_89 = Ada (RTX 40xx)
```

### Erro: "moonc.exe não encontrado"
```powershell
# Compilar MoonLight
cd ..\build
cmake --build . --config Release
```

## 💡 Dicas

1. **Execute múltiplas vezes** para obter média confiável
2. **Use mesmos parâmetros** (N, tamanhos) em ambas implementações
3. **Meça apenas tempo GPU** (não inclua transferências de memória)
4. **Warm-up**: Primeira execução pode ser mais lenta

## 📝 Exemplo Completo

```powershell
# Compilar CUDA
nvcc -O3 -arch=sm_75 saxpy_cuda.cu -o saxpy_cuda.exe

# Executar comparação
.\comparar_cuda.ps1 saxpy

# Saída esperada:
# === Comparacao: MoonLight vs CUDA C++ ===
# Benchmark: saxpy
# 
# 1. Executando MoonLight...
# 2. Executando CUDA C++...
# 
# === Resultados ===
# MoonLight:  12.345 ms
# CUDA C++:   11.200 ms
# 
# Overhead:   10.22%
# Speedup:    1.10x
# Status: Performance excelente! Muito proximo do CUDA C++
```

