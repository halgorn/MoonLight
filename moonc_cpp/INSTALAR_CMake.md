# 📦 Como Instalar CMake no Windows

## Opção 1: Instalar CMake (Recomendado)

### Via Chocolatey (se tiver)
```powershell
choco install cmake
```

### Via Scoop (se tiver)
```powershell
scoop install cmake
```

### Download Manual
1. Acesse: https://cmake.org/download/
2. Baixe: **Windows x64 Installer**
3. Instale e marque: **"Add CMake to system PATH"**
4. Reinicie o PowerShell

### Verificar Instalação
```powershell
cmake --version
```

---

## Opção 2: Usar Visual Studio (se tiver)

Se você tem Visual Studio instalado, pode usar o CMake que vem com ele:

```powershell
# Encontrar CMake do Visual Studio
$vs_cmake = "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"

# Ou para Visual Studio 2019
$vs_cmake = "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"

# Testar
& $vs_cmake --version

# Se funcionar, adicionar ao PATH temporariamente
$env:PATH += ";C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin"
```

---

## Opção 3: Compilar Manualmente (Sem CMake)

Se não quiser instalar CMake, posso criar um script de compilação manual, mas é mais complexo.

---

## ⚡ Depois de Instalar CMake

Execute:
```powershell
cd moonc_cpp\build
cmake .. -G "MinGW Makefiles"
cmake --build . --config Release
```

Ou com Visual Studio:
```powershell
cd moonc_cpp\build
cmake .. -G "Visual Studio 16 2019" -A x64
cmake --build . --config Release
```

