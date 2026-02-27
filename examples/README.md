# MoonLight - Exemplos

Este diretório contém exemplos de programas MoonLight organizados por categoria.

## Estrutura

### basic/
Exemplos básicos para iniciantes:
- `hello_world.gpu` - Hello World clássico
- `variables.gpu` - Uso de variáveis e tipos
- `fibonacci.gpu` - Sequência de Fibonacci recursiva
- `factorial.gpu` - Cálculo de fatorial

### algorithms/
Algoritmos clássicos implementados em MoonLight:
- `bubble_sort.gpu` - Ordenação Bubble Sort
- `prime_numbers.gpu` - Verificação de números primos

### oop/
Exemplos de Programação Orientada a Objetos:
- `person_class.gpu` - Classe Pessoa simples
- `calculator.gpu` - Calculadora OOP

## Como Executar

### Modo Interpretado (Rápido)
```bash
python executor_main.py examples/basic/hello_world.gpu
```

### Modo Compilado (Otimizado - requer NVCC)
```bash
python compiler_backend.py examples/basic/hello_world.gpu
```

## Testando os Exemplos

Todos os exemplos foram testados e funcionam corretamente com o executor atual.

### Teste Rápido
```bash
# Testar todos os exemplos básicos
python executor_main.py examples/basic/hello_world.gpu
python executor_main.py examples/basic/variables.gpu
python executor_main.py examples/basic/fibonacci.gpu
python executor_main.py examples/basic/factorial.gpu

# Testar algoritmos
python executor_main.py examples/algorithms/bubble_sort.gpu
python executor_main.py examples/algorithms/prime_numbers.gpu

# Testar OOP
python executor_main.py examples/oop/person_class.gpu
python executor_main.py examples/oop/calculator.gpu
```

## Próximos Exemplos (Futuras Entregas)

- `cuda/` - Exemplos de programação CUDA (Entrega 6-7)
- `ai/` - Exemplos de IA e Machine Learning (Entrega 9)
- `advanced/` - Features avançadas (Entrega 5)










