$bin = "C:\Users\Bruno\Documents\GitHub\MoonLight\moonc_cpp\build\Release\moonc.exe"

if (-not (Test-Path $bin)) {
    Write-Host "Binary not found at $bin"
    exit 1
}

Write-Host "Testing with debug flag..."
Write-Host "File: test0.gpu"
Write-Host ""

& $bin -v -c test0.gpu

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Exit code: $LASTEXITCODE"
}

