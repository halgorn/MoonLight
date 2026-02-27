# Script para executar um benchmark individual
# Uso: .\run_benchmark.ps1 -Benchmark "SAXPY"

param(
    [Parameter(Mandatory=$true)]
    [string]$Benchmark
)

$moonc = ".\build\Release\moonc.exe"
if (-not (Test-Path $moonc)) {
    $moonc = ".\build\Debug\moonc.exe"
}
if (-not (Test-Path $moonc)) {
    $moonc = "..\build\Release\moonc.exe"
    if (-not (Test-Path $moonc)) {
        $moonc = "..\build\Debug\moonc.exe"
    }
}

$benchmark_map = @{
    "SAXPY" = "saxpy.gpu"
    "GEMM" = "gemm.gpu"
    "FFT" = "fft.gpu"
    "REDUCTION" = "reduction.gpu"
    "SORT" = "sort.gpu"
    "CONV2D" = "conv2d.gpu"
    "HISTOGRAM" = "histogram.gpu"
}

$file = $benchmark_map[$Benchmark.ToUpper()]
if (-not $file) {
    Write-Host "Benchmark desconhecido: $Benchmark" -ForegroundColor Red
    Write-Host "Benchmarks disponiveis: $($benchmark_map.Keys -join ', ')" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $file)) {
    Write-Host "Arquivo nao encontrado: $file" -ForegroundColor Red
    exit 1
}

Write-Host "=== Executando Benchmark: $Benchmark ===" -ForegroundColor Green
Write-Host "Arquivo: $file" -ForegroundColor Cyan
Write-Host ""

$times = @()
for ($i = 1; $i -le 5; $i++) {
    Write-Host "Execucao $i..." -ForegroundColor Gray
    $result = Measure-Command { 
        & $moonc -r $file 2>&1 | Out-Null
    }
    $times += $result.TotalSeconds
    $time_str = $result.TotalSeconds.ToString('F3')
    Write-Host "  Tempo: ${time_str}s" -ForegroundColor White
}

$avg = ($times | Measure-Object -Average).Average
$min = ($times | Measure-Object -Minimum).Minimum
$max = ($times | Measure-Object -Maximum).Maximum

Write-Host ""
Write-Host "=== Resultados ===" -ForegroundColor Green
$avg_str = $avg.ToString('F3')
$min_str = $min.ToString('F3')
$max_str = $max.ToString('F3')
Write-Host "Media: ${avg_str}s" -ForegroundColor Cyan
Write-Host "Min: ${min_str}s" -ForegroundColor Cyan
Write-Host "Max: ${max_str}s" -ForegroundColor Cyan

