# Guia: Teste 100% Independente - Performance

## 🎯 Objetivo
Testar o compilador MoonLight 100% independente e medir performance.

---

## 📋 Pré-requisitos

### Windows
- Visual Studio 2019+ (com C++17) OU MinGW-w64
- CMake 3.15+
- CUDA Toolkit 11.0+ (para suporte GPU)

### Linux/macOS
- g++ 7+ ou clang 7+ (com C++17)
- CMake 3.15+
- CUDA Toolkit 11.0+ (para suporte GPU)

---

## 🔨 Compilação

### Windows (PowerShell)
```powershell
cd moonc_cpp
mkdir build
cd build
cmake .. -G "Visual Studio 16 2019" -A x64
cmake --build . --config Release
```

Ou com MinGW:
```powershell
cd moonc_cpp
mkdir build
cd build
cmake .. -G "MinGW Makefiles"
cmake --build . --config Release
```

### Linux/macOS
```bash
cd moonc_cpp
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

---

## ✅ Verificar Compilação

```bash
# Windows
.\build\Release\moonc.exe --version

# Linux/macOS
./build/moonc --version
```

**Saída esperada:**
```
MoonLight Compiler v2.0.0
CUDA support: enabled
```

---

## 🚀 Teste Básico - Vector Add

### 1. Criar arquivo de teste

Crie `test_vector_add.gpu`:
```moonlight
# Teste de Performance - Vector Addition
cuda kernel def add_vectors(a, b, c, n) {
    i = threadIdx_x + blockIdx_x * blockDim_x
    if (i < n) {
        c[i] = a[i] + b[i]
    }
}

def main() {
    n = 1000000  # 1M elementos
    
    # Alocar memória CPU
    h_a = [0.0] * n
    h_b = [0.0] * n
    h_c = [0.0] * n
    
    # Inicializar
    for (i = 0; i < n; i = i + 1) {
        h_a[i] = float(i)
        h_b[i] = float(i * 2)
    }
    
    # Alocar GPU
    d_a = device[n]
    d_b = device[n]
    d_c = device[n]
    
    # Transfer H->D
    d_a <- h_a
    d_b <- h_b
    
    # Launch kernel
    threads = 256
    blocks = (n + threads - 1) / threads
    gpu[blocks, threads] add_vectors(d_a, d_b, d_c, n)
    
    # Transfer D->H
    h_c <- d_c
    
    # Verificar
    print("Teste concluído!")
    print("h_c[0] =", h_c[0])
    print("h_c[", n-1, "] =", h_c[n-1])
    
    # Cleanup
    free(d_a)
    free(d_b)
    free(d_c)
}

main()
```

### 2. Executar Teste

```bash
# Windows
.\build\Release\moonc.exe -r test_vector_add.gpu -v

# Linux/macOS
./build/moonc -r test_vector_add.gpu -v
```

---

## ⚡ Teste de Performance Completo

### Criar script de benchmark

**Windows (`benchmark.ps1`):**
```powershell
# Benchmark MoonLight 100% Independente
$moonc = ".\build\Release\moonc.exe"
$test_file = "test_vector_add.gpu"

Write-Host "=== MoonLight Performance Test ===" -ForegroundColor Green
Write-Host ""

# Teste 1: Apenas gerar PTX
Write-Host "Teste 1: Geração de PTX..." -ForegroundColor Yellow
Measure-Command { & $moonc $test_file -S -o test.ptx } | 
    Select-Object TotalSeconds | 
    ForEach-Object { Write-Host "Tempo: $($_.TotalSeconds) segundos" }

# Teste 2: Compilar e executar
Write-Host ""
Write-Host "Teste 2: Compilação + Execução..." -ForegroundColor Yellow
Measure-Command { & $moonc -r $test_file } | 
    Select-Object TotalSeconds | 
    ForEach-Object { Write-Host "Tempo: $($_.TotalSeconds) segundos" }

# Teste 3: Múltiplas execuções (warmup + média)
Write-Host ""
Write-Host "Teste 3: Múltiplas execuções (5x)..." -ForegroundColor Yellow
$times = @()
for ($i = 1; $i -le 5; $i++) {
    $result = Measure-Command { & $moonc -r $test_file 2>&1 | Out-Null }
    $times += $result.TotalSeconds
    Write-Host "  Execução $i : $($result.TotalSeconds) segundos"
}
$avg = ($times | Measure-Object -Average).Average
Write-Host "Média: $avg segundos" -ForegroundColor Green
```

**Linux/macOS (`benchmark.sh`):**
```bash
#!/bin/bash
# Benchmark MoonLight 100% Independente

MOONC="./build/moonc"
TEST_FILE="test_vector_add.gpu"

echo "=== MoonLight Performance Test ==="
echo ""

# Teste 1: Apenas gerar PTX
echo "Teste 1: Geração de PTX..."
time $MOONC $TEST_FILE -S -o test.ptx

# Teste 2: Compilar e executar
echo ""
echo "Teste 2: Compilação + Execução..."
time $MOONC -r $TEST_FILE

# Teste 3: Múltiplas execuções
echo ""
echo "Teste 3: Múltiplas execuções (5x)..."
TIMES=()
for i in {1..5}; do
    START=$(date +%s.%N)
    $MOONC -r $TEST_FILE > /dev/null 2>&1
    END=$(date +%s.%N)
    ELAPSED=$(echo "$END - $START" | bc)
    TIMES+=($ELAPSED)
    echo "  Execução $i: ${ELAPSED} segundos"
done

# Calcular média
SUM=0
for t in "${TIMES[@]}"; do
    SUM=$(echo "$SUM + $t" | bc)
done
AVG=$(echo "scale=3; $SUM / ${#TIMES[@]}" | bc)
echo "Média: ${AVG} segundos"
```

---

## 📊 Comparação de Performance

### Comparar com Python (opcional)

Se quiser comparar com a versão Python:

```bash
# Versão Python (antiga)
time python moonc.py -r test_vector_add.gpu

# Versão C++ (nova - 100% independente)
time ./build/moonc -r test_vector_add.gpu
```

**Expectativa:**
- Compilação C++: **10-100x mais rápida** que Python
- Geração PTX: **Instantânea** (sem nvcc)
- Execução: Similar (mesma GPU)

---

## 🔍 Testes Adicionais

### Teste 2: Matrix Multiplication

Crie `test_matmul.gpu`:
```moonlight
cuda kernel def matmul(A, B, C, N) {
    row = blockIdx_y * blockDim_y + threadIdx_y
    col = blockIdx_x * blockDim_x + threadIdx_x
    
    if (row < N && col < N) {
        sum = 0.0
        for (k = 0; k < N; k = k + 1) {
            sum = sum + A[row * N + k] * B[k * N + col]
        }
        C[row * N + col] = sum
    }
}

def main() {
    N = 512
    size = N * N
    
    # ... (similar ao vector_add)
}

main()
```

### Teste 3: Verificar PTX gerado

```bash
# Gerar PTX
./moonc test_vector_add.gpu -S -o test.ptx

# Verificar conteúdo
cat test.ptx
```

**PTX esperado:**
```ptx
.version 7.0
.target sm_75
.address_size 64

.entry add_vectors(.param .u64 a, .param .u64 b, .param .u64 c, .param .u32 n) {
    .reg .u32 %tid, %ctaid, %ntid;
    ...
}
```

---

## 📈 Métricas de Performance

### O que medir:

1. **Tempo de Compilação**
   - Parsing: < 100ms (para 1K linhas)
   - PTX Generation: < 50ms
   - Total: < 200ms

2. **Tempo de Execução**
   - PTX Loading: < 10ms
   - Kernel Launch: < 1ms
   - Memory Transfers: depende do tamanho

3. **Throughput**
   - Elementos processados por segundo
   - Comparar com CUDA C++ nativo

---

## 🐛 Troubleshooting

### Erro: "CUDA not found"
```bash
# Verificar CUDA
nvcc --version

# Definir variáveis de ambiente (Windows)
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.8"

# Linux
export CUDA_PATH=/usr/local/cuda
```

### Erro: "Failed to initialize CUDA"
- Verificar se GPU NVIDIA está disponível
- Verificar driver CUDA instalado
- Testar: `nvidia-smi`

### Erro de compilação
- Verificar C++17 support: `g++ --version` ou `clang++ --version`
- Verificar CMake: `cmake --version`
- Limpar build: `rm -rf build` e tentar novamente

---

## ✅ Checklist de Teste

- [ ] Compilação bem-sucedida
- [ ] `--version` funciona
- [ ] `-c` (check syntax) funciona
- [ ] `-S` (generate PTX) funciona
- [ ] `-r` (run) executa programa
- [ ] Kernel executa na GPU
- [ ] Resultados corretos
- [ ] Performance aceitável

---

## 🎯 Resultado Esperado

Ao executar `./moonc -r test_vector_add.gpu`:

```
Compiling test_vector_add.gpu...
Lexing completed: XXX tokens
Parsing completed: X statements
Generating PTX...
PTX generated (XXX bytes)
Loading PTX on GPU...
[SUCCESS] PTX loaded on GPU successfully
Executing program...
Teste concluído!
h_c[0] = 0.0
h_c[999999] = 2999997.0
[SUCCESS] Program executed successfully
```

**Tempo total esperado:** < 1 segundo (incluindo compilação + execução)

---

## 📝 Próximos Passos

1. Testar com diferentes tamanhos de dados
2. Comparar com versão Python
3. Medir throughput (GFLOPS)
4. Testar outros exemplos (matrix mult, etc)
5. Otimizar se necessário

