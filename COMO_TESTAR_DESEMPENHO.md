# Como Testar Desempenho do Código MoonLight

Guia completo para testar e comparar performance do código MoonLight.

## ⚠️ IMPORTANTE: Por Que Ainda Usamos Python?

O MoonLight ainda usa Python para:
- **Compilar** código (moonc.py)
- **Parser/Lexer** (PLY)
- **Transpiler** (gerador C++)

**MAS:** O executável gerado é **100% independente** do Python!

```bash
# Compilar (precisa Python)
python moonc.py programa.gpu -o app

# Executar (NÃO precisa Python!)
./app
```

Veja `POR_QUE_AINDA_PYTHON.md` para mais detalhes.

---

## 🚀 Métodos de Teste

### 1. Script de Benchmark Simples (Recomendado)

Use o script `benchmark_performance.py` para testar qualquer código:

```bash
# Testar um arquivo .gpu
python benchmark_performance.py examples/basic/fibonacci.gpu 10

# Testar código inline (usa exemplo padrão)
python benchmark_performance.py
```

**O que ele faz:**
- ✅ Testa código em modo interpretado
- ✅ Testa código com JIT (se disponível)
- ✅ Testa código compilado (C++ executável)
- ✅ Compara performance entre todos os modos
- ✅ Mostra métricas detalhadas (tempo médio, mínimo, máximo)
- ✅ Calcula speedup (quanto mais rápido)

**Exemplo de saída:**
```
======================================================================
MOONLIGHT PERFORMANCE BENCHMARK
======================================================================

[1/2] Testando modo INTERPRETADO...
[2/2] Testando modo JIT...

======================================================================
RESULTADOS
======================================================================

[MODO INTERPRETADO]
  Tempo médio:     1250.345 ms
  Tempo mínimo:    1245.123 ms
  Tempo máximo:    1258.456 ms
  Tempo total:     12503.450 ms
  Iterações:       10

[MODO JIT]
  Tempo médio:     850.234 ms
  Tempo mínimo:    845.123 ms
  Tempo máximo:    860.456 ms
  Tempo total:     8502.340 ms
  Iterações:       10

[MODO COMPILADO]
  Tempo médio:     50.123 ms
  Tempo mínimo:    48.456 ms
  Tempo máximo:    52.789 ms
  Tempo total:     501.230 ms
  Tempo de transpile: 100.456 ms
  Tempo de compilação: 500.789 ms
  Iterações:       10

[COMPARACAO]
  JIT: 1.47x MAIS RAPIDO que interpretado
  COMPILADO: 24.94x MAIS RAPIDO que interpretado
  COMPILADO: 16.96x MAIS RAPIDO que JIT
```

---

### 2. Benchmarks Existentes

O projeto já tem vários benchmarks prontos:

#### Benchmarks Básicos

```bash
# Rodar todos os benchmarks básicos
python benchmarks/run_benchmarks.py

# Benchmark individual
python benchmarks/benchmark_fibonacci.py
python benchmarks/benchmark_loops.py
python benchmarks/benchmark_arrays.py
```

#### Benchmarks GPU

```bash
# Benchmarks de GPU/CUDA
python benchmarks/gpu/run_gpu_benchmarks.py
```

#### Benchmarks Persistent Kernels

```bash
# Benchmarks de persistent kernels
python benchmarks/persistent/run_persistent_benchmarks.py
```

---

### 3. Teste Manual Simples

Para testar código rapidamente:

```python
import time
from executor_simple import executar_codigo

code = """
def fibonacci(n) {
    if (n <= 1) { return n }
    return fibonacci(n-1) + fibonacci(n-2)
}

result = fibonacci(30)
"""

# Medir tempo
start = time.perf_counter()
executar_codigo(code)
end = time.perf_counter()

print(f"Tempo: {(end - start)*1000:.3f} ms")
```

---

### 4. Comparar com Python

Para comparar MoonLight com Python equivalente:

```python
import time

# Código MoonLight
moonlight_code = """
def sum_squares(n) {
    sum = 0
    for (i = 0; i < n; i = i + 1) {
        sum = sum + i * i
    }
    return sum
}
"""

# Código Python equivalente
def sum_squares_python(n):
    sum = 0
    for i in range(n):
        sum += i * i
    return sum

# Testar MoonLight
from executor_simple import executar_codigo
start = time.perf_counter()
executar_codigo(moonlight_code)
moonlight_time = time.perf_counter() - start

# Testar Python
start = time.perf_counter()
result = sum_squares_python(1000000)
python_time = time.perf_counter() - start

print(f"MoonLight: {moonlight_time*1000:.3f} ms")
print(f"Python:    {python_time*1000:.3f} ms")
print(f"Speedup:   {python_time/moonlight_time:.2f}x")
```

---

## 📊 Métricas Importantes

### Tempo de Execução
- **Tempo médio**: Média de várias execuções (mais confiável)
- **Tempo mínimo**: Melhor caso
- **Tempo máximo**: Pior caso
- **Tempo total**: Soma de todas as execuções

### Speedup
- **Speedup > 1.0**: Versão mais rápida é melhor
- **Speedup = 1.0**: Performance equivalente
- **Speedup < 1.0**: Versão mais lenta

### Overhead
- **Tempo de parse**: Quanto tempo leva para parsear o código
- **Tempo de compilação**: Quanto tempo leva para compilar (JIT)
- **Tempo de execução**: Quanto tempo leva para executar

---

## 🎯 Exemplos Práticos

### Exemplo 1: Testar Função Recursiva

```bash
# Criar arquivo test_fib.gpu
cat > test_fib.gpu << 'EOF'
def fibonacci(n) {
    if (n <= 1) { return n }
    return fibonacci(n-1) + fibonacci(n-2)
}

result = fibonacci(35)
print("Result:", result)
EOF

# Testar
python benchmark_performance.py test_fib.gpu 5
```

### Exemplo 2: Testar Loop Intensivo

```bash
# Criar arquivo test_loop.gpu
cat > test_loop.gpu << 'EOF'
def sum_squares(n) {
    sum = 0
    for (i = 0; i < n; i = i + 1) {
        sum = sum + i * i
    }
    return sum
}

result = sum_squares(1000000)
print("Sum of squares:", result)
EOF

# Testar
python benchmark_performance.py test_loop.gpu 10
```

### Exemplo 3: Testar com JIT

```bash
# Criar arquivo test_jit.gpu
cat > test_jit.gpu << 'EOF'
@jit
def compute(n) {
    result = 0
    for (i = 0; i < n; i = i + 1) {
        result = result + i * i * i
    }
    return result
}

result = compute(1000000)
print("Result:", result)
EOF

# Testar (JIT será usado automaticamente)
python benchmark_performance.py test_jit.gpu 10
```

---

## 🔍 Interpretando Resultados

### ✅ Bom Desempenho
- Tempo consistente (mínimo e máximo próximos)
- JIT mais rápido que interpretado (speedup > 1.0)
- Overhead de parse/compilação baixo (< 10% do tempo total)

### ⚠️ Desempenho Aceitável
- Variação moderada entre execuções
- JIT similar ou ligeiramente mais rápido
- Overhead moderado (10-30% do tempo total)

### ❌ Desempenho Ruim
- Grande variação entre execuções
- JIT mais lento que interpretado
- Overhead alto (> 30% do tempo total)

---

## 💡 Dicas

1. **Use múltiplas iterações**: Média de 10+ execuções é mais confiável
2. **Faça warmup**: Primeira execução pode ser mais lenta (cache, JIT compilation)
3. **Teste com diferentes tamanhos**: Performance pode variar com tamanho do input
4. **Compare com baseline**: Sempre compare com Python ou implementação de referência
5. **Monitore recursos**: Use `htop` ou `nvidia-smi` para ver uso de CPU/GPU

---

## 🛠️ Troubleshooting

### "JIT não disponível"
```bash
# Instalar llvmlite
pip install llvmlite
```

### "Erro ao parsear código"
- Verifique sintaxe do código
- Teste com código mais simples primeiro

### "Tempos muito variáveis"
- Aumente número de iterações
- Feche outros programas
- Use `time.perf_counter()` ao invés de `time.time()`

---

## 📚 Referências

- `benchmarks/README.md` - Documentação dos benchmarks
- `benchmarks/persistent/README.md` - Benchmarks de persistent kernels
- `benchmarks/gpu/README.md` - Benchmarks de GPU
- `docs/JIT_GUIDE.md` - Guia de JIT compilation

