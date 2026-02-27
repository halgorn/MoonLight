# Script para executar teste 100% independente
# Windows PowerShell

Write-Host "=== MoonLight 100% Independente - Teste ===" -ForegroundColor Green
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "test_vector_add.gpu")) {
    Write-Host "Erro: Execute este script de dentro de moonc_cpp/" -ForegroundColor Red
    Write-Host "  cd moonc_cpp" -ForegroundColor Yellow
    exit 1
}

# Verificar se compilador existe
$moonc_release = ".\build\Release\moonc.exe"
$moonc_debug = ".\build\Debug\moonc.exe"
$moonc = $null

if (Test-Path $moonc_release) {
    $moonc = $moonc_release
    Write-Host "✅ Compilador encontrado (Release)" -ForegroundColor Green
} elseif (Test-Path $moonc_debug) {
    $moonc = $moonc_debug
    Write-Host "✅ Compilador encontrado (Debug)" -ForegroundColor Green
} else {
    Write-Host "❌ Compilador não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Compile primeiro:" -ForegroundColor Yellow
    Write-Host "  cd build" -ForegroundColor White
    Write-Host "  cmake .. -G `"Visual Studio 16 2019`" -A x64" -ForegroundColor White
    Write-Host "  cmake --build . --config Release" -ForegroundColor White
    Write-Host ""
    Write-Host "Ou com MinGW:" -ForegroundColor Yellow
    Write-Host "  cd build" -ForegroundColor White
    Write-Host "  cmake .. -G `"MinGW Makefiles`"" -ForegroundColor White
    Write-Host "  cmake --build . --config Release" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "=== Executando Teste ===" -ForegroundColor Cyan
Write-Host ""

# Teste 1: Verificar sintaxe
Write-Host "1. Verificando sintaxe..." -ForegroundColor Yellow
& $moonc -c test_vector_add.gpu
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro de sintaxe!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Sintaxe OK" -ForegroundColor Green
Write-Host ""

# Teste 2: Gerar PTX
Write-Host "2. Gerando PTX..." -ForegroundColor Yellow
$ptx_time = Measure-Command { & $moonc test_vector_add.gpu -S -o test.ptx 2>&1 | Out-Null }
Write-Host "   Tempo: $($ptx_time.TotalSeconds.ToString('F3')) segundos" -ForegroundColor White
if (Test-Path "test.ptx") {
    $size = (Get-Item "test.ptx").Length
    Write-Host "   PTX: $size bytes" -ForegroundColor Gray
    Write-Host "✅ PTX gerado" -ForegroundColor Green
} else {
    Write-Host "❌ PTX não gerado" -ForegroundColor Red
}
Write-Host ""

# Teste 3: Executar programa completo
Write-Host "3. Executando programa completo..." -ForegroundColor Yellow
$exec_time = Measure-Command { 
    & $moonc -r test_vector_add.gpu -v 2>&1 | Tee-Object -Variable output
}
Write-Host "   Tempo: $($exec_time.TotalSeconds.ToString('F3')) segundos" -ForegroundColor White

# Verificar se executou com sucesso
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Programa executado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== Resumo ===" -ForegroundColor Cyan
    Write-Host "Geração PTX: $($ptx_time.TotalSeconds.ToString('F3'))s" -ForegroundColor White
    Write-Host "Execução:    $($exec_time.TotalSeconds.ToString('F3'))s" -ForegroundColor White
    Write-Host "Total:        $(($ptx_time.TotalSeconds + $exec_time.TotalSeconds).ToString('F3'))s" -ForegroundColor Green
} else {
    Write-Host "❌ Erro na execução" -ForegroundColor Red
    Write-Host $output
    exit 1
}

Write-Host ""
Write-Host "=== Teste Concluído! ===" -ForegroundColor Green

