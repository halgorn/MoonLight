# Script de Comparacao de Performance
# Compara MoonLight vs CUDA C++ (compilada) vs Python/CuPy (interpretada)

param(
    [string]$Benchmark = "saxpy",
    [int]$Iterations = 5
)

$ErrorActionPreference = "Stop"

Write-Host "=== Comparativo de Performance: MoonLight vs CUDA C++ vs Python/CuPy ===" -ForegroundColor Cyan
Write-Host "Benchmark: $Benchmark" -ForegroundColor Yellow
Write-Host "Iteracoes: $Iterations" -ForegroundColor Yellow
Write-Host ""

$results = @{
    MoonLight = @{}
    CUDA_CPP = @{}
    Python_CuPy = @{}
}

# Funcao para executar benchmark MoonLight
function Run-MoonLightBenchmark {
    param([string]$benchmark_name)
    
    $benchmark_file = "$benchmark_name.gpu"
    if (-not (Test-Path $benchmark_file)) {
        Write-Host "Arquivo $benchmark_file nao encontrado!" -ForegroundColor Red
        return $null
    }
    
    Write-Host "Executando MoonLight: $benchmark_file..." -ForegroundColor Green
    
    $times = @()
    for ($i = 1; $i -le $Iterations; $i++) {
        $output = & "..\build\Release\moonc.exe" -r $benchmark_file 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Erro ao executar MoonLight: $output" -ForegroundColor Red
            return $null
        }
        
        # Extrair tempo da saida
        if ($output -match "Tempo GPU \(ms\):\s*([\d.]+)") {
            $time = [double]$Matches[1]
            $times += $time
            Write-Host "  Execucao ${i}: $time ms" -ForegroundColor Gray
        } elseif ($output -match "Throughput \(GB\/s\):\s*([\d.]+)") {
            # Para SAXPY, podemos usar throughput
            Write-Host "  Execucao ${i}: Throughput encontrado" -ForegroundColor Gray
        }
    }
    
    if ($times.Count -gt 0) {
        $avg = ($times | Measure-Object -Average).Average
        $min = ($times | Measure-Object -Minimum).Minimum
        $max = ($times | Measure-Object -Maximum).Maximum
        
        return @{
            Average = $avg
            Min = $min
            Max = $max
            Times = $times
            Output = $output
        }
    }
    
    return @{
        Output = $output
    }
}

# Funcao para executar benchmark CUDA C++
function Run-CUDABenchmark {
    param([string]$benchmark_name)
    
    $cuda_file = "${benchmark_name}_cuda.cu"
    if (-not (Test-Path $cuda_file)) {
        Write-Host "Arquivo CUDA $cuda_file nao encontrado (sera criado)" -ForegroundColor Yellow
        return $null
    }
    
    Write-Host "Compilando CUDA C++: $cuda_file..." -ForegroundColor Green
    
    # Compilar com nvcc
    $exe_name = "${benchmark_name}_cuda.exe"
    $compile_output = & nvcc -O3 -arch=sm_75 $cuda_file -o $exe_name 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erro ao compilar CUDA: $compile_output" -ForegroundColor Red
        return $null
    }
    
    Write-Host "Executando CUDA C++..." -ForegroundColor Green
    
    $times = @()
    for ($i = 1; $i -le $Iterations; $i++) {
        $output = & ".\$exe_name" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Erro ao executar CUDA: $output" -ForegroundColor Red
            return $null
        }
        
        # Extrair tempo da saida
        if ($output -match "Tempo GPU \(ms\):\s*([\d.]+)") {
            $time = [double]$Matches[1]
            $times += $time
            Write-Host "  Execucao ${i}: $time ms" -ForegroundColor Gray
        }
    }
    
    if ($times.Count -gt 0) {
        $avg = ($times | Measure-Object -Average).Average
        $min = ($times | Measure-Object -Minimum).Minimum
        $max = ($times | Measure-Object -Maximum).Maximum
        
        return @{
            Average = $avg
            Min = $min
            Max = $max
            Times = $times
        }
    }
    
    return $null
}

# Funcao para executar benchmark Python/CuPy
function Run-PythonBenchmark {
    param([string]$benchmark_name)
    
    $python_file = "${benchmark_name}_cupy.py"
    if (-not (Test-Path $python_file)) {
        Write-Host "Arquivo Python $python_file nao encontrado (sera criado)" -ForegroundColor Yellow
        return $null
    }
    
    Write-Host "Executando Python/CuPy: $python_file..." -ForegroundColor Green
    
    $times = @()
    for ($i = 1; $i -le $Iterations; $i++) {
        $output = & python $python_file 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Erro ao executar Python: $output" -ForegroundColor Red
            return $null
        }
        
        # Extrair tempo da saida
        if ($output -match "Tempo GPU \(ms\):\s*([\d.]+)") {
            $time = [double]$Matches[1]
            $times += $time
            Write-Host "  Execucao ${i}: $time ms" -ForegroundColor Gray
        }
    }
    
    if ($times.Count -gt 0) {
        $avg = ($times | Measure-Object -Average).Average
        $min = ($times | Measure-Object -Minimum).Minimum
        $max = ($times | Measure-Object -Maximum).Maximum
        
        return @{
            Average = $avg
            Min = $min
            Max = $max
            Times = $times
        }
    }
    
    return $null
}

# Executar benchmarks
Write-Host "=== Executando Benchmarks ===" -ForegroundColor Cyan
Write-Host ""

$results.MoonLight = Run-MoonLightBenchmark -benchmark_name $Benchmark
Write-Host ""

$results.CUDA_CPP = Run-CUDABenchmark -benchmark_name $Benchmark
Write-Host ""

$results.Python_CuPy = Run-PythonBenchmark -benchmark_name $Benchmark
Write-Host ""

# Gerar relatorio comparativo
Write-Host "=== Relatorio Comparativo ===" -ForegroundColor Cyan
Write-Host ""

if ($results.MoonLight -and $results.MoonLight.Average) {
    $ml_time = $results.MoonLight.Average
    Write-Host "MoonLight:" -ForegroundColor Yellow
    Write-Host "  Tempo Medio: $([math]::Round($ml_time, 3)) ms" -ForegroundColor White
    Write-Host "  Min: $([math]::Round($results.MoonLight.Min, 3)) ms" -ForegroundColor White
    Write-Host "  Max: $([math]::Round($results.MoonLight.Max, 3)) ms" -ForegroundColor White
    Write-Host ""
    
    if ($results.CUDA_CPP -and $results.CUDA_CPP.Average) {
        $cuda_time = $results.CUDA_CPP.Average
        $speedup = $cuda_time / $ml_time
        Write-Host "CUDA C++:" -ForegroundColor Yellow
        Write-Host "  Tempo Medio: $([math]::Round($cuda_time, 3)) ms" -ForegroundColor White
        Write-Host "  Min: $([math]::Round($results.CUDA_CPP.Min, 3)) ms" -ForegroundColor White
        Write-Host "  Max: $([math]::Round($results.CUDA_CPP.Max, 3)) ms" -ForegroundColor White
        Write-Host "  Speedup vs MoonLight: $([math]::Round($speedup, 2))x" -ForegroundColor $(if ($speedup -gt 1) { "Green" } else { "Red" })
        Write-Host ""
    }
    
    if ($results.Python_CuPy -and $results.Python_CuPy.Average) {
        $py_time = $results.Python_CuPy.Average
        $speedup = $py_time / $ml_time
        Write-Host "Python/CuPy:" -ForegroundColor Yellow
        Write-Host "  Tempo Medio: $([math]::Round($py_time, 3)) ms" -ForegroundColor White
        Write-Host "  Min: $([math]::Round($results.Python_CuPy.Min, 3)) ms" -ForegroundColor White
        Write-Host "  Max: $([math]::Round($results.Python_CuPy.Max, 3)) ms" -ForegroundColor White
        Write-Host "  Speedup vs MoonLight: $([math]::Round($speedup, 2))x" -ForegroundColor $(if ($speedup -gt 1) { "Green" } else { "Red" })
        Write-Host ""
    }
    
    # Analise de performance
    Write-Host "=== Analise de Performance ===" -ForegroundColor Cyan
    Write-Host ""
    
    if ($results.CUDA_CPP -and $results.CUDA_CPP.Average) {
        $overhead = (($ml_time - $results.CUDA_CPP.Average) / $results.CUDA_CPP.Average) * 100
        if ($overhead -lt 10) {
            Write-Host "MoonLight esta com performance muito proxima do CUDA C++ (overhead: $([math]::Round($overhead, 1))%)" -ForegroundColor Green
        } elseif ($overhead -lt 30) {
            Write-Host "MoonLight tem overhead moderado vs CUDA C++ ($([math]::Round($overhead, 1))%)" -ForegroundColor Yellow
        } else {
            Write-Host "MoonLight tem overhead significativo vs CUDA C++ ($([math]::Round($overhead, 1))%)" -ForegroundColor Red
        }
    }
    
    if ($results.Python_CuPy -and $results.Python_CuPy.Average) {
        $speedup_vs_py = $results.Python_CuPy.Average / $ml_time
        if ($speedup_vs_py -gt 1.5) {
            Write-Host "MoonLight e $([math]::Round($speedup_vs_py, 1))x mais rapido que Python/CuPy" -ForegroundColor Green
        } elseif ($speedup_vs_py -gt 1.0) {
            Write-Host "MoonLight e $([math]::Round($speedup_vs_py, 1))x mais rapido que Python/CuPy" -ForegroundColor Yellow
        } else {
            Write-Host "MoonLight e mais lento que Python/CuPy (fator: $([math]::Round($speedup_vs_py, 2))x)" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== Comparativo Concluido ===" -ForegroundColor Cyan

