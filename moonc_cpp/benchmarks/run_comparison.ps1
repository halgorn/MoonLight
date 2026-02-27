# Script simplificado para executar comparativo de performance
# Executa MoonLight e mostra resultados

param(
    [string]$Benchmark = "saxpy"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Comparativo de Performance: MoonLight ===" -ForegroundColor Cyan
Write-Host "Benchmark: $Benchmark" -ForegroundColor Yellow
Write-Host ""

$benchmark_file = "$Benchmark.gpu"
if (-not (Test-Path $benchmark_file)) {
    Write-Host "Arquivo $benchmark_file nao encontrado!" -ForegroundColor Red
    exit 1
}

$moonc_path = "..\build\Release\moonc.exe"
if (-not (Test-Path $moonc_path)) {
    Write-Host "Compilador MoonLight nao encontrado em $moonc_path" -ForegroundColor Red
    Write-Host "Por favor, compile o projeto primeiro:" -ForegroundColor Yellow
    Write-Host "  cd ..\build" -ForegroundColor Yellow
    Write-Host "  cmake --build . --config Release" -ForegroundColor Yellow
    exit 1
}

Write-Host "Executando MoonLight: $benchmark_file..." -ForegroundColor Green
Write-Host ""

$iterations = 3
$times = @()

for ($i = 1; $i -le $iterations; $i++) {
    Write-Host "Execucao ${i}:" -ForegroundColor Gray -NoNewline
    $output = & $moonc_path -r $benchmark_file 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host " ERRO" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
        exit 1
    }
    
    # Extrair tempo da saida
    if ($output -match "Tempo GPU \(ms\):\s*([\d.]+)") {
        $time = [double]$Matches[1]
        $times += $time
        Write-Host " $time ms" -ForegroundColor Green
    } elseif ($output -match "Throughput \(GB\/s\):\s*([\d.]+)") {
        $throughput = [double]$Matches[1]
        Write-Host " Throughput: $throughput GB/s" -ForegroundColor Green
    } elseif ($output -match "GFLOPs:\s*([\d.]+)") {
        $gflops = [double]$Matches[1]
        Write-Host " GFLOPs: $gflops" -ForegroundColor Green
    } else {
        Write-Host " (sem metrica de tempo)" -ForegroundColor Yellow
    }
}

Write-Host ""

if ($times.Count -gt 0) {
    $avg = ($times | Measure-Object -Average).Average
    $min = ($times | Measure-Object -Minimum).Minimum
    $max = ($times | Measure-Object -Maximum).Maximum
    
    Write-Host "=== Resultados MoonLight ===" -ForegroundColor Cyan
    Write-Host "Tempo Medio: $([math]::Round($avg, 3)) ms" -ForegroundColor White
    Write-Host "Min: $([math]::Round($min, 3)) ms" -ForegroundColor White
    Write-Host "Max: $([math]::Round($max, 3)) ms" -ForegroundColor White
    Write-Host ""
    
    Write-Host "=== Comparacao ===" -ForegroundColor Cyan
    Write-Host "Para comparar com CUDA C++ e Python/CuPy:" -ForegroundColor Yellow
    Write-Host "  1. Compile os arquivos *_cuda.cu com nvcc" -ForegroundColor Yellow
    Write-Host "  2. Execute os arquivos *_cupy.py com Python" -ForegroundColor Yellow
    Write-Host "  3. Use: .\compare_performance.ps1 -Benchmark $Benchmark" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Nota: MoonLight compila para PTX e executa diretamente na GPU," -ForegroundColor Gray
    Write-Host "      similar ao CUDA C++, mas com sintaxe de alto nivel." -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Concluido ===" -ForegroundColor Cyan

