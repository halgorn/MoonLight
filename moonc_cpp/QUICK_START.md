# Quick Start - Teste 100% Independente

## 🚀 Compilação Rápida

### Windows
```powershell
cd moonc_cpp
mkdir build
cd build
cmake .. -G "Visual Studio 16 2019" -A x64
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

## ✅ Teste Básico

```bash
# Windows
.\build\Release\moonc.exe -r test_vector_add.gpu

# Linux/macOS  
./build/moonc -r test_vector_add.gpu
```

---

## ⚡ Benchmark Completo

### Windows
```powershell
.\benchmark.ps1
```

### Linux/macOS
```bash
chmod +x benchmark.sh
./benchmark.sh
```

---

## 📊 O que Esperar

**Tempo de compilação:** < 200ms  
**Tempo de execução:** < 1 segundo (total)  
**Performance GPU:** Similar a CUDA C++ nativo

---

## 🎯 Próximos Testes

1. Testar com diferentes tamanhos (1K, 1M, 10M elementos)
2. Comparar com versão Python (se disponível)
3. Testar outros kernels (matrix mult, etc)
4. Medir throughput (GFLOPS)

