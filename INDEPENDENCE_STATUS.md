# MoonLight - Status de Independência

## ❓ MoonLight é independente do Python?

### Resposta Curta: **NÃO (ainda)** ⚠️

MoonLight **ainda depende do Python** para:
- Parser (PLY - Python Lex-Yacc)
- Executor/Interpretador
- Transpiler
- Todas as ferramentas CLI

---

## 📊 Status Atual (v1.0.0)

### ✅ O que funciona HOJE:

1. **Modo Interpretado** (Depende do Python)
   ```bash
   python executor_main.py programa.gpu
   # OU
   python moonc.py programa.gpu -r
   ```
   - Roda diretamente usando o interpretador Python
   - Depende 100% do Python instalado

2. **Modo Compilado** (Depende do Python + g++/nvcc)
   ```bash
   python moonc.py programa.gpu -o app
   ./app  # Executável independente!
   ```
   - MoonLight → Python transpila para C++
   - C++ → g++/nvcc compila para binário
   - **O executável final é independente!** ✅

### ⚠️ O que ainda depende do Python:

- ✅ **Parser**: Usa PLY (Python)
- ✅ **Lexer**: Usa PLY (Python)
- ✅ **Executor**: Interpretador em Python
- ✅ **Transpiler**: Gerador C++ em Python
- ✅ **moonc**: CLI em Python
- ✅ **REPL**: Console em Python
- ✅ **Debugger**: Em Python

---

## 🎯 Como Usar MoonLight HOJE

### Opção 1: **Modo Interpretado** (Requer Python)
```bash
# Requisitos: Python 3.8+, PLY
python moonc.py test_simple.gpu -r
```
**Vantagens**: Rápido para desenvolvimento/testes  
**Desvantagens**: Precisa de Python instalado

### Opção 2: **Modo Compilado** (Executável Independente!)
```bash
# Passo 1: Compilar (requer Python + g++)
python moonc.py test_simple.gpu -o test_app

# Passo 2: Executar (SEM Python!)
./test_app
```
**Vantagens**: Executável independente, rápido  
**Desvantagens**: Precisa de Python para compilar

### Opção 3: **REPL** (Requer Python)
```bash
python repl.py
```
**Vantagens**: Interativo, ótimo para experimentar  
**Desvantagens**: Precisa de Python

---

## 🔍 Dependências Atuais

### Para DESENVOLVER em MoonLight:
```
Python 3.8+
├── ply (parser/lexer)
├── pytest (testes)
└── llvmlite (JIT - opcional)
```

### Para EXECUTAR programas MoonLight:

**Modo Interpretado**:
- Python 3.8+
- PLY

**Modo Compilado**:
- Python 3.8+ (apenas para compilar)
- g++ ou clang++ (C++ compiler)
- nvcc (para CUDA - opcional)

**Executáveis gerados**:
- ❌ Nenhuma dependência! (100% standalone)

---

## 🚀 Como Testar HOJE

### Teste 1: Modo Interpretado
```bash
# Criar arquivo de teste (já criado: test_simple.gpu)
python moonc.py test_simple.gpu -r
```

### Teste 2: Verificar Sintaxe
```bash
python moonc.py test_simple.gpu -c
```

### Teste 3: Compilar para Executável
```bash
# Compilar
python moonc.py test_simple.gpu -o meu_app

# Executar (independente!)
./meu_app
```

### Teste 4: REPL Interativo
```bash
python repl.py

moon> x = 10
moon> print(x * 2)
20
moon> exit
```

---

## 📈 Roadmap para Independência Total

### Fase 1: **Atual** (v1.0.0) ⚠️
- Depende do Python para tudo
- Executáveis compilados são independentes
- **STATUS: 50% independente**

### Fase 2: **Compilador em C++** (v2.0) 🚧
- Reescrever parser/lexer em C++
- Compilador standalone `moonc` em C++
- **STATUS: 0% independente do Python**

### Fase 3: **Totalmente Standalone** (v3.0) 🎯
- Zero dependências Python
- `moonc` binário standalone
- Distribuição simples (apenas um executável)
- **STATUS: 100% independente**

---

## 💡 Como Distribuir Programas MoonLight HOJE

### Para Usuários COM Python:
```bash
# Dar o arquivo .gpu
python moonc.py programa.gpu -r
```

### Para Usuários SEM Python:
```bash
# 1. Você compila (precisa Python)
python moonc.py programa.gpu -o app

# 2. Distribui apenas o executável
# app.exe (Windows) ou ./app (Linux)
# O usuário NÃO precisa de Python!
```

---

## 🎯 Resumo

| Aspecto | Status | Requer Python? |
|---------|--------|----------------|
| **Desenvolvimento** | ✅ Completo | ✅ Sim |
| **Executar .gpu** | ✅ Funciona | ✅ Sim |
| **Compilar .gpu** | ✅ Funciona | ✅ Sim (para compilar) |
| **Executáveis gerados** | ✅ Independentes | ❌ Não! |
| **REPL** | ✅ Funciona | ✅ Sim |
| **Debugger** | ✅ Funciona | ✅ Sim |
| **VS Code Extension** | ✅ Funciona | ✅ Sim (indiretamente) |
| **Compilador Standalone** | ❌ Futuro | ✅ Sim (ainda) |

---

## 🔧 Instalação para Usar MoonLight

### Requisitos Mínimos:
```bash
# 1. Python 3.8+
python --version

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Testar
python moonc.py test_simple.gpu -r
```

### Para Compilar Executáveis:
```bash
# Além do acima:
# - g++ ou clang++ (C++ compiler)
# - nvcc (apenas para CUDA)

g++ --version
nvcc --version  # opcional
```

---

## 📝 Exemplos de Uso

### 1. Desenvolvimento Rápido (Interpretado)
```bash
# Editar código
nano meu_programa.gpu

# Testar imediatamente
python moonc.py meu_programa.gpu -r

# Repetir até funcionar
```

### 2. Produção (Compilado)
```bash
# Compilar com otimizações
python moonc.py meu_programa.gpu -O -o app_release

# Distribuir executável
# Usuário final NÃO precisa de Python!
./app_release
```

### 3. Interativo (REPL)
```bash
python repl.py

moon> def fib(n) {
...       if (n <= 1) { return n }
...       return fib(n-1) + fib(n-2)
...   }
moon> fib(10)
55
```

---

## ⚠️ Limitações Atuais

1. **Precisa de Python** para compilar (não para executar binários)
2. **Não há moonc standalone** (ainda é Python)
3. **Distribuição complexa** (requer Python + deps)
4. **REPL depende de Python**

---

## 🎯 Conclusão

### MoonLight HOJE (v1.0.0):

**Para DESENVOLVEDORES**:
- ✅ Funciona perfeitamente
- ⚠️ Requer Python instalado
- ✅ Todas as features funcionais

**Para USUÁRIOS FINAIS**:
- ✅ Executáveis compilados são 100% independentes
- ✅ Não precisam de Python para rodar o executável
- ⚠️ Você (dev) precisa de Python para compilar

**Analogia**:
- MoonLight hoje é como **TypeScript**:
  - TypeScript precisa de Node.js para compilar
  - Mas o JavaScript gerado roda em qualquer browser
- MoonLight precisa de Python para compilar
  - Mas o executável roda em qualquer sistema (sem Python)

---

## 🚀 Próximos Passos para Independência

### v2.0 (Futuro):
- Reescrever parser/lexer em C++
- `moonc` como binário standalone
- Bootstrapping (compilar MoonLight com MoonLight)

### v3.0 (Futuro Distante):
- Zero dependências externas
- Distribuição: um único executável
- Self-hosting completo

---

**RESUMO**: MoonLight v1.0.0 funciona perfeitamente, mas **ainda depende do Python para compilação**. Executáveis gerados são **100% independentes**! 🚀









