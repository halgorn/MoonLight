# ⚡ Teste Rápido - Windows PowerShell

## Passo 1: Compilar (Primeira Vez)

```powershell
cd moonc_cpp
mkdir build
cd build
cmake .. -G "Visual Studio 16 2019" -A x64
cmake --build . --config Release
```

**Ou se não tiver Visual Studio, use MinGW:**
```powershell
cd moonc_cpp
mkdir build
cd build
cmake .. -G "MinGW Makefiles"
cmake --build . --config Release
```

---

## Passo 2: Teste Básico

```powershell
cd moonc_cpp
.\build\Release\moonc.exe -r test_vector_add.gpu -v
```

---

## Passo 3: Benchmark Completo

```powershell
cd moonc_cpp
.\benchmark.ps1
```

---

## ⚠️ Se der erro de compilação

1. **Verificar CMake:**
   ```powershell
   cmake --version
   ```

2. **Verificar CUDA (opcional):**
   ```powershell
   nvcc --version
   ```

3. **Compilar sem CUDA (para testar parser):**
   ```powershell
   cmake .. -DMOONLIGHT_WITH_CUDA=OFF
   cmake --build . --config Release
   ```

---

## ✅ Teste Rápido (Sem Compilar)

Se quiser apenas testar o parser (sem GPU):

```powershell
cd moonc_cpp
.\build\Release\moonc.exe -c test_vector_add.gpu -v
```

Isso só verifica a sintaxe, sem executar.

