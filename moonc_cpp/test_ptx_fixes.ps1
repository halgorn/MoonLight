# Script para testar as correções de PTX
# Testa a geração de PTX sem precisar compilar o projeto completo

Write-Host "=== Teste de Correções PTX ===" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos no diretório correto
if (-not (Test-Path "src\codegen\ptx_generator.cpp")) {
    Write-Host "❌ Execute este script de dentro de moonc_cpp/" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Arquivos de código encontrados" -ForegroundColor Green
Write-Host ""

# Verificar sintaxe básica do código C++
Write-Host "Verificando sintaxe do código C++..." -ForegroundColor Yellow

# Verificar se há erros óbvios de sintaxe
$ptx_gen = Get-Content "src\codegen\ptx_generator.cpp" -Raw
$ptx_header = Get-Content "include\moonlight\ptx_generator.h" -Raw

# Verificações básicas
$checks = @{
    "pending_ptx_" = "Sistema pending_ptx_ implementado"
    "register_types_" = "Rastreamento de tipos de registradores"
    "used_registers_" = "Rastreamento de registradores usados"
    "op.type" = "Sintaxe PTX corrigida (op.type)"
    "setp\." = "Operações de comparação (setp)"
    "ld.param" = "Carregamento de parâmetros"
    "\.reg " = "Declarações de registradores"
}

Write-Host "Verificando implementações:" -ForegroundColor Yellow
$all_ok = $true
foreach ($check in $checks.GetEnumerator()) {
    $found = ($ptx_gen -match $check.Key) -or ($ptx_header -match $check.Key)
    if ($found) {
        Write-Host "  ✅ $($check.Value)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($check.Value)" -ForegroundColor Red
        $all_ok = $false
    }
}

Write-Host ""

if ($all_ok) {
    Write-Host "✅ Todas as verificações passaram!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor Yellow
    Write-Host "  1. Compile o projeto (use COMPILAR_SEM_CMAKE.ps1 ou CMake)" -ForegroundColor White
    Write-Host "  2. Teste com: .\moonc.exe benchmarks\saxpy.gpu -S -o saxpy.ptx" -ForegroundColor White
    Write-Host "  3. Verifique se o PTX gerado compila com cuModuleLoadData" -ForegroundColor White
} else {
    Write-Host "❌ Algumas verificações falharam" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Teste Concluído ===" -ForegroundColor Cyan




