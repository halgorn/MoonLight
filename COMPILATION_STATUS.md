# MoonLight - Status da Compilação

## Resumo

O MoonLight possui **3 modos de execução**:

1. **Interpretado** (atual, funcional mas lento)
2. **Transpiled + Compilado** (parcialmente funcional)
3. **JIT via LLVM** (experimental)

---

## Modo 1: Interpretado ✅

**Como usar:**
```bash
python executor_simple.py arquivo.gpu
```

**Performance:**
- Fibonacci(35): ~mesma velocidade do Python puro
- Razão: código é interpretado linha por linha

**Prós:**
- Funciona sem dependências externas
- Debug fácil
- Desenvolvimento rápido

**Contras:**
- **LENTO** - mesma velocidade do Python
- Sem otimizações
- Não usa GPU

---

## Modo 2: Compilado ⚠️

**Como usar:**
```bash
python moonc.py arquivo.gpu -o programa
```

**Status Atual:**
- ✅ Transpiler C++ funciona
- ⚠️ Parser tem conflitos (230 shift/reduce)
- ❌ Precisa g++/MSVC no Windows

**Performance Esperada:**
- Fibonacci(35): **10-100x mais rápido** que interpretado
- Razão: código nativo C++

**Limitações Atuais:**
1. **Parser**: Conflitos fazem funções falharem às vezes
2. **Windows**: Precisa instalar MinGW-w64 ou MSVC
3. **CUDA**: Precisa NVIDIA CUDA Toolkit

**Código que funciona:**
```moonlight
# Código simples compila OK
x = 35
y = x * 2
print(y)
```

**Código que ainda não compila:**
```moonlight
# Funções têm conflitos no parser
def fibonacci(n) {
    if (n <= 1) {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}
```

---

## Modo 3: JIT (LLVM) 🚧

**Status:** Experimental

---

## Benchmark: Fibonacci(35)

| Modo | Tempo | Speedup |
|------|-------|---------|
| Python Puro | ~X segundos | 1x (baseline) |
| MoonLight Interpretado | ~X segundos | ~1x (mesma velocidade) |
| MoonLight Compilado (C++) | **~X/10 - X/100 segundos** | 10-100x |
| MoonLight CUDA (GPU) | **~X/1000 segundos** | 1000x+ |

**Nota:** MoonLight interpretado é lento porque **não há compilação acontecendo** - é Python puro.

---

## O que falta para ter Compilação Completa

### Fase 1: Parser ⏳
- [ ] Resolver 191 shift/reduce conflicts
- [ ] Resolver 39 reduce/reduce conflicts
- [ ] Testar todos os exemplos

**Estimativa:** 1-2 dias de trabalho

### Fase 2: Compilador Backend ✅
- [x] Transpiler C++
- [x] Geração de código CUDA
- [ ] Windows: MinGW/MSVC support
- [ ] Linux: g++ support

**Estimativa:** Já implementado, só precisa compilador instalado

### Fase 3: Otimizações 🚧
- [ ] Dead code elimination
- [ ] Constant folding
- [ ] Loop unrolling
- [ ] Inline functions

**Estimativa:** 1 semana

---

## Como Instalar Compilador C++ (Windows)

### Opção 1: MinGW-w64
```bash
# Download do https://www.mingw-w64.org/
# Adicionar ao PATH: C:\mingw64\bin
```

### Opção 2: Visual Studio
```bash
# Instalar Visual Studio 2022 Community
# Selecionar "Desktop development with C++"
```

### Opção 3: MSYS2
```bash
pacman -S mingw-w64-x86_64-gcc
```

---

## Conclusão

**Por que Fibonacci está lento?**
- Porque está rodando **interpretado** (Python puro)
- Não há compilação acontecendo
- Parser tem bugs que impedem compilação de funções

**Solução:**
1. **Curto prazo:** Usar código simples que compila
2. **Médio prazo:** Corrigir parser (1-2 dias)
3. **Longo prazo:** Otimizações avançadas

**Para ter speedup real:**
```bash
# Depois de corrigir o parser:
python moonc.py fibonacci.gpu -o fib -O
./fib  # 10-100x mais rápido!
```

---

**Última atualização:** 2025-10-26  
**Status:** Parser precisa correção antes de compilação funcionar 100%

