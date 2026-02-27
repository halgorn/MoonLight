# MoonLight - Exemplos de Transpilação

Estes exemplos demonstram as capacidades do transpiler MoonLight → C++/CUDA.

## Exemplos

### bitwise_operations.gpu
Demonstra todas as operações bitwise:
- AND (&), OR (|), XOR (^)
- NOT (~)
- Left shift (<<), Right shift (>>)

### lambda_example.gpu
Demonstra expressões lambda:
- Lambda simples com um parâmetro
- Lambda com múltiplos parâmetros
- Lambda em atribuição

### power_example.gpu
Demonstra operador de potência (**):
- Potenciação simples
- Potenciação em expressões

## Como Transpilar e Executar

```bash
# Transpilar para C++
python transpiler.py examples/transpiler/power_example.gpu

# Verificar o código C++ gerado
cat output.cpp

# Compilar e executar (requer g++ ou nvcc)
python compiler_backend.py examples/transpiler/power_example.gpu
```

## Features Implementadas no Transpiler

✅ Operações bitwise completas
✅ Operador de potência (**)
✅ Expressões lambda
✅ List comprehensions
✅ Slice operations
✅ Operadores unários
✅ Funções auxiliares C++ (range, slice, comprehension)










