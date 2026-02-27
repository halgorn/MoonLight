# Script de teste de performance simplificado
# Captura saída de forma mais confiável

param(
    [string]$Benchmark = "saxpy"
)

$ErrorActionPreference = "Continue"

Write-Host "=== Teste de Performance: MoonLight ===" -ForegroundColor Cyan
Write-Host "Benchmark: $Benchmark" -ForegroundColor Yellow
Write-Host ""

$benchmark_file = "$Benchmark.gpu"
$moonc_path = "..\build\Release\moonc.exe"

if (-not (Test-Path $benchmark_file)) {
    Write-Host "ERRO: Arquivo $benchmark_file nao encontrado!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $moonc_path)) {
    Write-Host "ERRO: Compilador nao encontrado em $moonc_path" -ForegroundColor Red
    exit 1
}

Write-Host "Executando: $moonc_path -r $benchmark_file" -ForegroundColor Green
Write-Host ""

# Executar e capturar saída completa
$processInfo = New-Object System.Diagnostics.ProcessStartInfo
$processInfo.FileName = $moonc_path
$processInfo.Arguments = "-r $benchmark_file"
$processInfo.UseShellExecute = $false
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true
$processInfo.CreateNoWindow = $true

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $processInfo

# Capturar saída
$outputBuilder = New-Object System.Text.StringBuilder
$errorBuilder = New-Object System.Text.StringBuilder

$outputEvent = Register-ObjectEvent -InputObject $process -EventName OutputDataReceived -Action {
    if ($EventArgs.Data) {
        [void]$Event.MessageData.AppendLine($EventArgs.Data)
    }
} -MessageData $outputBuilder

$errorEvent = Register-ObjectEvent -InputObject $process -EventName ErrorDataReceived -Action {
    if ($EventArgs.Data) {
        [void]$Event.MessageData.AppendLine($EventArgs.Data)
    }
} -MessageData $errorBuilder

# Iniciar processo
$process.Start() | Out-Null
$process.BeginOutputReadLine()
$process.BeginErrorReadLine()

# Aguardar conclusão (com timeout de 30 segundos)
$completed = $process.WaitForExit(30000)

if (-not $completed) {
    Write-Host "ERRO: Processo demorou mais de 30 segundos!" -ForegroundColor Red
    $process.Kill()
    exit 1
}

# Aguardar eventos terminarem
Start-Sleep -Milliseconds 500

# Mostrar saída
$output = $outputBuilder.ToString()
$error = $errorBuilder.ToString()

if ($output) {
    Write-Host $output
}

if ($error) {
    Write-Host "=== ERROS ===" -ForegroundColor Red
    Write-Host $error -ForegroundColor Red
}

Write-Host ""
Write-Host "Exit Code: $($process.ExitCode)" -ForegroundColor $(if ($process.ExitCode -eq 0) { "Green" } else { "Red" })

# Limpar eventos
Unregister-Event -SourceIdentifier $outputEvent.Name
Unregister-Event -SourceIdentifier $errorEvent.Name

exit $process.ExitCode

