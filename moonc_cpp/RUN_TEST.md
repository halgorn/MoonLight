# 🚀 Como Rodar Teste 100% Independente

## Compilação Rápida

### Windows
```powershell
cd moonc_cpp\build
cmake .. -G "Visual Studio 16 2019" -A x64
cmake --build . --config Release
```

### Linux/macOS
```bash
cd moonc_cpp/build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

---

## Teste Básico

```bash
# Windows
.\build\Release\moonc.exe -r test_vector_add.gpu -v

# Linux/macOS
./build/moonc -r test_vector_add.gpu -v
```

---

## Benchmark Automático

### Windows
```powershell
cd moonc_cpp
.\benchmark.ps1
```

### Linux/macOS
```bash
cd moonc_cpp
chmod +x benchmark.sh && ./benchmark.sh
```

---

## O que Esperar

✅ **Compilação:** < 200ms  
✅ **Execução:** < 1 segundo  
✅ **Resultado:** h_c[0] = 0.0, h_c[999999] = 2999997.0

---

## Arquivos Criados

- `test_vector_add.gpu` - Programa de teste
- `benchmark.ps1` - Script Windows
- `benchmark.sh` - Script Linux/macOS
- `TEST_100_PERCENT_INDEPENDENT.md` - Guia completo
- `COMO_TESTAR.md` - Instruções detalhadas

---

**Pronto para testar! 🎯**

