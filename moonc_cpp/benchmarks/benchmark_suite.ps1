# Benchmark Suite Completo - MoonLight
# Executa todos os benchmarks de performance

# Encontrar moonc.exe
$moonc = $null
$paths = @(
    ".\build\Release\moonc.exe",
    ".\build\Debug\moonc.exe",
    "..\build\Release\moonc.exe",
    "..\build\Debug\moonc.exe"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        $moonc = $path
        break
    }
}

if (-not $moonc) {
    Write-Host "Erro: moonc.exe nao encontrado!" -ForegroundColor Red
    Write-Host "Procurei em:" -ForegroundColor Yellow
    $paths | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MoonLight Benchmark Suite Completo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Usando: $moonc" -ForegroundColor Gray
Write-Host ""

$benchmarks = @(
    @{Name="1. Adicao de Vetores (SAXPY)"; File="saxpy.gpu"; Metric="Throughput (GB/s)"},
    @{Name="2. Multiplicacao de Matrizes (GEMM)"; File="gemm.gpu"; Metric="GFLOPs"},
    @{Name="3. Transformada Rapida de Fourier (FFT)"; File="fft.gpu"; Metric="Tempo (s)"},
    @{Name="4. Reducao Paralela"; File="reduction.gpu"; Metric="Tempo (s)"},
    @{Name="5. Ordenacao Paralela"; File="sort.gpu"; Metric="Tempo (s)"},
    @{Name="6. Camada Convolucional (Conv2D)"; File="conv2d.gpu"; Metric="Giga-Ops/s"},
    @{Name="7. Histograma"; File="histogram.gpu"; Metric="Tempo (s)"}
)

$results = @()

foreach ($bench in $benchmarks) {
    $file = $bench.File
    if (-not (Test-Path $file)) {
        Write-Host "[PULADO] $($bench.Name) - Arquivo $file nao encontrado" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Host "Executando: $($bench.Name)" -ForegroundColor Yellow
    Write-Host "Arquivo: $file" -ForegroundColor Gray
    Write-Host ""
    
    $times = @()
    for ($i = 1; $i -le 3; $i++) {
        $result = Measure-Command { 
            & $moonc -r $file 2>&1 | Out-Null
        }
        $times += $result.TotalSeconds
        $time_str = $result.TotalSeconds.ToString('F3')
        Write-Host "  Execucao ${i}: ${time_str}s" -ForegroundColor Gray
    }
    
    $avg = ($times | Measure-Object -Average).Average
    $min = ($times | Measure-Object -Minimum).Minimum
    $max = ($times | Measure-Object -Maximum).Maximum
    
    $avg_str = $avg.ToString('F3')
    $min_str = $min.ToString('F3')
    $max_str = $max.ToString('F3')
    Write-Host "  Media: ${avg_str}s | Min: ${min_str}s | Max: ${max_str}s" -ForegroundColor Green
    Write-Host "  Metrica: $($bench.Metric)" -ForegroundColor Cyan
    Write-Host ""
    
    $results += [PSCustomObject]@{
        Benchmark = $bench.Name
        Media = $avg
        Min = $min
        Max = $max
        Metrica = $bench.Metric
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Resumo dos Resultados" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$results | Format-Table -AutoSize

Write-Host ""
Write-Host "=== Benchmark Suite Concluido ===" -ForegroundColor Green
