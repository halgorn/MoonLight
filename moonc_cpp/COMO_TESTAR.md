# 🚀 Como Testar - MoonLight 100% Independente

## Passo 1: Compilar o Compilador

### Windows (PowerShell)
```powershell
cd moonc_cpp
mkdir build -ErrorAction SilentlyContinue
cd build
cmake .. -G "Visual Studio 16 2019" -A x64
cmake --build . --config Release
```

**Ou com MinGW:**
```powershell
cd moonc_cpp
mkdir build -ErrorAction SilentlyContinue
cd build
cmake .. -G "MinGW Makefiles"
cmake --build . --config Release
```

### Linux/macOS
```bash
cd moonc_cpp
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

---

## Passo 2: Verificar Compilação

```bash
# Windows
.\build\Release\moonc.exe --version

# Linux/macOS
./build/moonc --version
```

**Deve mostrar:**
```
MoonLight Compiler v2.0.0
CUDA support: enabled
```

---

## Passo 3: Teste Rápido

### Opção A: Teste Simples (Recomendado)

```bash
# Windows
.\build\Release\moonc.exe -r test_vector_add.gpu -v

# Linux/macOS
./build/moonc -r test_vector_add.gpu -v
```

### Opção B: Usar Exemplo Existente

```bash
# Windows
.\build\Release\moonc.exe -r ..\examples\cuda\vector_add.gpu -v

# Linux/macOS
./build/moonc -r ../examples/cuda/vector_add.gpu -v
```

---

## Passo 4: Benchmark de Performance

### Windows
```powershell
cd moonc_cpp
.\benchmark.ps1
```

### Linux/macOS
```bash
cd moonc_cpp
chmod +x benchmark.sh
./benchmark.sh
```

---

## 📊 O que Esperar

### Saída Esperada:
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

### Tempos Esperados:
- **Compilação (parsing + PTX):** < 200ms
- **PTX Loading:** < 10ms
- **Execução total:** < 1 segundo

---

## 🔍 Verificar PTX Gerado

```bash
# Gerar apenas PTX
.\build\Release\moonc.exe test_vector_add.gpu -S -o test.ptx

# Ver conteúdo
cat test.ptx  # Linux/macOS
type test.ptx  # Windows
```

---

## ⚠️ Troubleshooting

### Erro: "CUDA not found"
- Instale CUDA Toolkit
- Verifique: `nvcc --version`
- Windows: Defina `CUDA_PATH` environment variable

### Erro: "Failed to initialize CUDA"
- Verifique GPU NVIDIA: `nvidia-smi`
- Verifique driver CUDA instalado
- Teste: `nvidia-smi` deve mostrar GPU

### Erro de compilação
- Verifique C++17: `g++ --version` ou `clang++ --version`
- Limpe build: `rm -rf build` e tente novamente
- Windows: Use Visual Studio 2019+ ou MinGW-w64

---

## 📈 Comparação de Performance

### Comparar com Python (se disponível):
```bash
# Versão Python (antiga)
time python moonc.py -r test_vector_add.gpu

# Versão C++ (nova - 100% independente)
time ./build/moonc -r test_vector_add.gpu
```

**Expectativa:** C++ é **10-100x mais rápido** na compilação!

---

## ✅ Checklist

- [ ] Compilação bem-sucedida
- [ ] `--version` funciona
- [ ] `-c` (check syntax) funciona  
- [ ] `-S` (generate PTX) funciona
- [ ] `-r` (run) executa programa
- [ ] Kernel executa na GPU
- [ ] Resultados corretos
- [ ] Performance aceitável

---

## 🎯 Próximos Testes

1. **Teste com diferentes tamanhos:**
   - 1K elementos
   - 1M elementos (padrão)
   - 10M elementos

2. **Teste outros exemplos:**
   - `examples/cuda/matrix_mult.gpu`
   - `examples/cuda/parallel_reduction.gpu`

3. **Medir throughput:**
   - GFLOPS alcançados
   - Comparar com CUDA C++ nativo

---

## 💡 Dicas

- Use `-v` (verbose) para ver detalhes
- Use `-S` para inspecionar PTX gerado
- Compare tempos com múltiplas execuções
- Teste com diferentes compute capabilities

---

**Pronto para testar! 🚀**

