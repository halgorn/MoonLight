# MoonLight Benchmarks

Suite de testes de performance comparando MoonLight com Python.

## 📊 O que é testado

### 1. **Fibonacci Recursivo** (`benchmark_fibonacci`)
- Teste clássico de recursão intensiva
- Fibonacci(35) - ~9M chamadas recursivas
- Melhor caso para compilação

### 2. **Loops Intensivos** (`benchmark_loops`)
- Loops simples e nested loops
- Operações aritméticas intensivas
- Sum of squares (10.000 iterações)
- Nested loops (1.000 x 1.000)

### 3. **Manipulação de Arrays** (`benchmark_arrays`)
- Criação e manipulação de listas
- Bubble sort (pior caso)
- Operações de acesso e soma

## 🚀 Como executar

### Rodar todos os benchmarks
```bash
python benchmarks/run_benchmarks.py
```

### Rodar benchmark individual

**Python:**
```bash
python benchmarks/benchmark_fibonacci.py
```

**MoonLight (interpretado):**
```bash
python executor_main.py benchmarks/benchmark_fibonacci.gpu
```

**MoonLight (compilado):**
```bash
python moonc.py benchmarks/benchmark_fibonacci.gpu -o fib_test
./fib_test
```

## 📈 Resultados esperados

### MoonLight Compilado vs Python

| Benchmark | Speedup esperado | Observação |
|-----------|------------------|------------|
| Fibonacci | 5-10x | Recursão se beneficia muito de C++ |
| Loops | 3-7x | Loops são mais rápidos em C++ |
| Arrays | 1-3x | Depende de alocações dinâmicas |

### MoonLight Interpretado vs Python

| Benchmark | Resultado | Observação |
|-----------|-----------|------------|
| Todos | Similar ou mais lento | Overhead do interpretador |

## 🎯 Interpretação dos resultados

### ✅ **MoonLight Compilado deve ser mais rápido porque:**
1. Compila para C++ nativo
2. Otimizações do g++/clang++
3. Sem overhead de interpretador Python
4. Tipos estáticos (sem boxing/unboxing)

### ⚠️ **MoonLight Interpretado pode ser mais lento porque:**
1. Executado via interpretador Python
2. Overhead de parsing/AST walking
3. Sem otimizações JIT

### 🎯 **Casos onde Python pode ser competitivo:**
1. Operações built-in otimizadas (sum, list comprehensions)
2. Código que usa bibliotecas C (numpy)
3. I/O intensivo

## 📝 Adicionando novos benchmarks

1. Crie par de arquivos: `benchmark_nome.gpu` e `benchmark_nome.py`
2. Mantenha lógica idêntica nos dois
3. Adicione entrada em `run_benchmarks.py`
4. Documente resultados esperados

## 🔧 Requisitos

- Python 3.8+
- g++ ou clang++ (para compilação)
- MoonLight instalado (`pip install -r requirements.txt`)

## 💡 Dicas para benchmarks justos

1. **Mesma lógica**: Código MoonLight e Python devem ser equivalentes
2. **Aquecimento**: Ignore primeira execução (cache, etc)
3. **Múltiplas rodadas**: Média de várias execuções
4. **Isolar processos**: Um benchmark por vez
5. **Desabilitar otimizações Python**: `python -O` se necessário

## 🎓 O que aprender

- MoonLight compilado é significativamente mais rápido para:
  - Recursão
  - Loops intensivos
  - Operações matemáticas
  
- MoonLight ainda depende de Python para compilar
- Futuro: Compilador C++ standalone será ainda mais rápido

## 📊 Exemplo de saída

```
======================================================================
MoonLight vs Python - Suite de Benchmarks
======================================================================

======================================================================
Benchmark: Fibonacci (Recursão)
======================================================================
  Executando Python: benchmark_fibonacci.py
  Executando MoonLight (interpretado): benchmark_fibonacci.gpu
  Executando MoonLight (compilado): benchmark_fibonacci.gpu
    Compilando para benchmark_fibonacci_compiled...

  Resultados:
    Python:                 3.2450s
    MoonLight (interp):     5.8920s
    MoonLight (compilado):  0.4123s

  🚀 Speedup (compilado vs Python): 7.87x
     MoonLight é 7.87x MAIS RÁPIDO!

======================================================================
RESUMO GERAL DOS BENCHMARKS
======================================================================

Benchmark                      Python       Interp       Compilado    Speedup
-------------------------------------------------------------------------------------
Fibonacci (Recursão)           3.245s       5.892s       0.412s       7.87x
Loops Intensivos               2.103s       3.456s       0.389s       5.41x
Manipulação de Arrays          1.987s       2.234s       0.823s       2.41x

🏆 Speedup médio (MoonLight compilado vs Python): 5.23x
   MoonLight é em média 5.23x MAIS RÁPIDO que Python! 🚀
```

## 🚀 Próximos passos

- [ ] Adicionar mais benchmarks (primes, sorting, matrix)
- [ ] Suporte para benchmarks CUDA (GPU)
- [ ] Comparar com outras linguagens (Rust, Go, Julia)
- [ ] Gráficos de performance
- [ ] CI/CD para regressões de performance

