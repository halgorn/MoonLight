# Script para compilar sem CMake (usando g++ diretamente)
# Requer: g++ ou MinGW instalado

Write-Host "=== Compilação Manual (Sem CMake) ===" -ForegroundColor Cyan
Write-Host ""

# Verificar g++
if (-not (Get-Command g++ -ErrorAction SilentlyContinue)) {
    Write-Host "❌ g++ não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instale MinGW-w64:" -ForegroundColor Yellow
    Write-Host "  1. Baixe: https://sourceforge.net/projects/mingw-w64/" -ForegroundColor White
    Write-Host "  2. Ou use: choco install mingw" -ForegroundColor White
    Write-Host "  3. Adicione ao PATH: C:\mingw64\bin" -ForegroundColor White
    exit 1
}

Write-Host "✅ g++ encontrado" -ForegroundColor Green
g++ --version | Select-Object -First 1
Write-Host ""

# Diretórios
$SRC_DIR = "src"
$INCLUDE_DIR = "include"
$BUILD_DIR = "build_manual"
$OUTPUT = "$BUILD_DIR\moonc.exe"

# Criar diretório de build
if (-not (Test-Path $BUILD_DIR)) {
    New-Item -ItemType Directory -Path $BUILD_DIR | Out-Null
}

Write-Host "Compilando..." -ForegroundColor Yellow

# Flags de compilação
$CXXFLAGS = "-std=c++17", "-Wall", "-O2", "-I$INCLUDE_DIR"

# Arquivos fonte
$SOURCES = @(
    "$SRC_DIR\lexer\token.cpp",
    "$SRC_DIR\lexer\lexer.cpp",
    "$SRC_DIR\parser\parser.cpp",
    "$SRC_DIR\ast\ast_node.cpp",
    "$SRC_DIR\codegen\ptx_generator.cpp",
    "$SRC_DIR\runtime\cuda_loader.cpp",
    "$SRC_DIR\runtime\executor.cpp",
    "$SRC_DIR\runtime\memory_manager.cpp",
    "$SRC_DIR\runtime\value.cpp",
    "$SRC_DIR\main.cpp"
)

# Verificar se todos os arquivos existem
$missing = @()
foreach ($src in $SOURCES) {
    if (-not (Test-Path $src)) {
        $missing += $src
    }
}

if ($missing.Count -gt 0) {
    Write-Host "❌ Arquivos não encontrados:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    exit 1
}

# Compilar
$cmd = "g++ $CXXFLAGS $($SOURCES -join ' ') -o $OUTPUT"
Write-Host "Comando: $cmd" -ForegroundColor Gray
Write-Host ""

try {
    Invoke-Expression $cmd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Compilação bem-sucedida!" -ForegroundColor Green
        Write-Host "Executável: $OUTPUT" -ForegroundColor Cyan
        
        # Testar
        Write-Host ""
        Write-Host "Testando..." -ForegroundColor Yellow
        & $OUTPUT --version
    } else {
        Write-Host "❌ Erro na compilação" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Erro: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Pronto! ===" -ForegroundColor Green
Write-Host "Use: .\$OUTPUT -r test_vector_add.gpu" -ForegroundColor Cyan

