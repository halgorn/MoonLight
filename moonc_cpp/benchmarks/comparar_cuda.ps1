# Script de Comparacao Simples: MoonLight vs CUDA C++
param([string]$Benchmark = "saxpy")

$moonc = "..\build\Release\moonc.exe"
$cuda_exe = "${Benchmark}_cuda.exe"

Write-Host "=== Comparacao: MoonLight vs CUDA C++ ===" -ForegroundColor Cyan
Write-Host "Benchmark: $Benchmark" -ForegroundColor Yellow
Write-Host ""

# Verificar se moonc existe
if (-not (Test-Path $moonc)) {
    Write-Host "Erro: $moonc nao encontrado!" -ForegroundColor Red
    Write-Host "Compile o projeto primeiro: cd ..\build && cmake --build . --config Release" -ForegroundColor Yellow
    exit 1
}

# Verificar se arquivo .gpu existe
$gpu_file = "${Benchmark}.gpu"
if (-not (Test-Path $gpu_file)) {
    Write-Host "Erro: $gpu_file nao encontrado!" -ForegroundColor Red
    exit 1
}

# Executar MoonLight
Write-Host "1. Executando MoonLight..." -ForegroundColor Green
$ml_output = & $moonc -r $gpu_file 2>&1
$ml_time = $null
$ml_throughput = $null

if ($ml_output -match "Tempo GPU \(ms\):\s*([\d.]+)") {
    $ml_time = [double]$Matches[1]
    Write-Host "   Tempo GPU: $ml_time ms" -ForegroundColor Gray
}
if ($ml_output -match "Throughput \(GB\/s\):\s*([\d.]+)") {
    $ml_throughput = [double]$Matches[1]
    Write-Host "   Throughput: $ml_throughput GB/s" -ForegroundColor Gray
}

# Executar CUDA C++
Write-Host "2. Executando CUDA C++..." -ForegroundColor Green
if (-not (Test-Path $cuda_exe)) {
    Write-Host "   Arquivo $cuda_exe nao encontrado!" -ForegroundColor Red
    Write-Host "   Compile primeiro: nvcc -O3 -arch=sm_75 ${Benchmark}_cuda.cu -o $cuda_exe" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Para descobrir sua GPU:" -ForegroundColor Yellow
    Write-Host "   nvidia-smi --query-gpu=compute_cap --format=csv" -ForegroundColor Gray
    exit 1
}

$cuda_output = & ".\$cuda_exe" 2>&1
$cuda_time = $null
$cuda_throughput = $null

if ($cuda_output -match "Tempo GPU \(ms\):\s*([\d.]+)") {
    $cuda_time = [double]$Matches[1]
    Write-Host "   Tempo GPU: $cuda_time ms" -ForegroundColor Gray
}
if ($cuda_output -match "Throughput \(GB\/s\):\s*([\d.]+)") {
    $cuda_throughput = [double]$Matches[1]
    Write-Host "   Throughput: $cuda_throughput GB/s" -ForegroundColor Gray
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
        Write-Host ""
        Write-Host "Status: Performance excelente! Muito proximo do CUDA C++" -ForegroundColor Green
    } elseif ($overhead -lt 30) {
        Write-Host ""
        Write-Host "Status: Overhead moderado, aceitavel para linguagem de alto nivel" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "Status: Overhead significativo, pode precisar de otimizacoes" -ForegroundColor Red
    }
    
    # Throughput comparison
    if ($ml_throughput -and $cuda_throughput) {
        Write-Host ""
        Write-Host "Throughput:" -ForegroundColor Cyan
        Write-Host "MoonLight:  $ml_throughput GB/s" -ForegroundColor White
        Write-Host "CUDA C++:   $cuda_throughput GB/s" -ForegroundColor White
        $throughput_ratio = ($ml_throughput / $cuda_throughput) * 100
        Write-Host "Ratio:      $([math]::Round($throughput_ratio, 2))%" -ForegroundColor $(if ($throughput_ratio -gt 90) { "Green" } elseif ($throughput_ratio -gt 70) { "Yellow" } else { "Red" })
    }
} else {
    Write-Host "Nao foi possivel extrair tempos da saida" -ForegroundColor Red
    Write-Host ""
    Write-Host "MoonLight output:" -ForegroundColor Yellow
    $ml_output | Select-Object -Last 15
    Write-Host ""
    Write-Host "CUDA output:" -ForegroundColor Yellow
    $cuda_output | Select-Object -Last 15
}

