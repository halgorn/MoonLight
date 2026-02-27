# Benchmark MoonLight 100% Independente
# Windows PowerShell Script

$moonc = ".\build\Release\moonc.exe"
if (-not (Test-Path $moonc)) {
    $moonc = ".\build\Debug\moonc.exe"
}
if (-not (Test-Path $moonc)) {
    Write-Host "Erro: moonc.exe nao encontrado. Compile primeiro!" -ForegroundColor Red
    exit 1
}

$test_file = "test_vector_add.gpu"
if (-not (Test-Path $test_file)) {
    Write-Host "Erro: $test_file nao encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host "=== MoonLight Performance Test ===" -ForegroundColor Green
Write-Host "Compilador: $moonc" -ForegroundColor Cyan
Write-Host "Teste: $test_file" -ForegroundColor Cyan
Write-Host ""

# Teste 1: Apenas gerar PTX
Write-Host "Teste 1: Geracao de PTX..." -ForegroundColor Yellow
$result1 = Measure-Command { & $moonc $test_file -S -o test.ptx 2>&1 | Out-Null }
Write-Host "  Tempo: $($result1.TotalSeconds) segundos" -ForegroundColor White
if (Test-Path "test.ptx") {
    $ptx_size = (Get-Item "test.ptx").Length
    Write-Host "  PTX gerado: $ptx_size bytes" -ForegroundColor Gray
}

# Teste 2: Compilar e executar (primeira vez)
Write-Host ""
Write-Host "Teste 2: Compilacao + Execucao (primeira vez)..." -ForegroundColor Yellow
$result2 = Measure-Command { & $moonc -r $test_file -v 2>&1 | Out-Null }
Write-Host "  Tempo: $($result2.TotalSeconds) segundos" -ForegroundColor White

# Teste 3: Multiplas execucoes (warmup + media)
Write-Host ""
Write-Host "Teste 3: Multiplas execucoes (5x)..." -ForegroundColor Yellow
$times = @()
for ($i = 1; $i -le 5; $i++) {
    $result = Measure-Command { & $moonc -r $test_file 2>&1 | Out-Null }
    $times += $result.TotalSeconds
    $time_str = $result.TotalSeconds.ToString('F3')
    Write-Host "  Execucao ${i} : ${time_str} segundos" -ForegroundColor Gray
}
$avg = ($times | Measure-Object -Average).Average
$min = ($times | Measure-Object -Minimum).Minimum
$max = ($times | Measure-Object -Maximum).Maximum
$avg_str = $avg.ToString('F3')
$min_str = $min.ToString('F3')
$max_str = $max.ToString('F3')
Write-Host "  Media: ${avg_str} segundos" -ForegroundColor Green
Write-Host "  Min: ${min_str} segundos" -ForegroundColor Green
Write-Host "  Max: ${max_str} segundos" -ForegroundColor Green

Write-Host ""
Write-Host "=== Teste Concluido ===" -ForegroundColor Green
