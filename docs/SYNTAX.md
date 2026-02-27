# MoonLight - Guia de Sintaxe

## Índice
- [Variáveis e Tipos](#variáveis-e-tipos)
- [Operadores](#operadores)
- [Estruturas de Controle](#estruturas-de-controle)
- [Funções](#funções)
- [List comprehensions, with, multiple assignment](#features-completas-list-comprehensions-with-multiple-assignment)
- [Classes](#classes)
- [Estruturas de Dados](#estruturas-de-dados)
- [Funções Built-in](#funções-built-in)

## Variáveis e Tipos

### Declaração de Variáveis
```moonlight
# Números inteiros
x = 10
idade = 25

# Números decimais
pi = 3.14159
preco = 99.99

# Strings
nome = "João"
mensagem = 'Olá Mundo'

# Booleanos
ativo = True
concluido = False

# None
valor = None
```

## Operadores

### Operadores Aritméticos
```moonlight
soma = 10 + 5        # Adição
sub = 10 - 5         # Subtração
mult = 10 * 5        # Multiplicação
div = 10 / 5         # Divisão
mod = 10 % 3         # Módulo
pot = 2 ** 3         # Potência
```

### Operadores de Comparação
```moonlight
a = 10 > 5           # Maior que
b = 10 < 5           # Menor que
c = 10 == 10         # Igual a
d = 10 != 5          # Diferente de
e = 10 >= 10         # Maior ou igual
f = 10 <= 5          # Menor ou igual
```

### Operadores Lógicos
```moonlight
result = True and False     # E lógico
result = True or False      # OU lógico
result = not True           # NÃO lógico
```

### Operadores de Atribuição Composta
```moonlight
x = 10
x += 5      # x = x + 5
x -= 3      # x = x - 3
x *= 2      # x = x * 2
x /= 4      # x = x / 4
x %= 3      # x = x % 3
x **= 2     # x = x ** 2
```

### Operadores de Incremento/Decremento
```moonlight
x = 5
x++         # Pós-incremento
x--         # Pós-decremento
++x         # Pré-incremento
--x         # Pré-decremento
```

### Operadores Bitwise
```moonlight
a = 5 & 3      # AND bitwise
b = 5 | 3      # OR bitwise
c = 5 ^ 3      # XOR bitwise
d = ~5         # NOT bitwise
e = 5 << 2     # Left shift
f = 5 >> 2     # Right shift
```

## Estruturas de Controle

### if/else
```moonlight
x = 10

if (x > 5) {
    print("x é maior que 5")
}

if (x > 15) {
    print("x é maior que 15")
} else {
    print("x não é maior que 15")
}

# Nested if
if (x > 0) {
    if (x < 20) {
        print("x está entre 0 e 20")
    }
}
```

### while
```moonlight
contador = 0
while (contador < 5) {
    print(contador)
    contador = contador + 1
}
```

### for
```moonlight
# For tradicional
for (i = 0; i < 10; i = i + 1) {
    print(i)
}

# For com passo customizado
for (i = 0; i < 10; i = i + 2) {
    print(i)  # Imprime números pares
}
```

### break e continue
```moonlight
# Break
for (i = 0; i < 10; i = i + 1) {
    if (i == 5) {
        break
    }
    print(i)
}

# Continue
for (i = 0; i < 10; i = i + 1) {
    if (i == 5) {
        continue
    }
    print(i)
}
```

## Funções

### Definição de Funções
```moonlight
# Função simples
def saudacao() {
    print("Olá!")
}

# Função com parâmetros
def soma(a, b) {
    return a + b
}

# Função com múltiplos returns
def abs_value(x) {
    if (x < 0) {
        return -x
    }
    return x
}

# Chamando funções
saudacao()
resultado = soma(5, 10)
print(resultado)
```

### Recursão
```moonlight
def fibonacci(n) {
    if (n <= 1) {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

def factorial(n) {
    if (n <= 1) {
        return 1
    }
    return n * factorial(n - 1)
}
```

### Decoradores
```moonlight
# Decorador @jit para otimização
@jit
def calculo_pesado(n) {
    sum = 0
    for (i = 0; i < n; i = i + 1) {
        sum = sum + i * i
    }
    return sum
}
```

## Features completas: list comprehensions, with, multiple assignment

### List comprehensions
```moonlight
# [expr for var in iterable]
dobros = [x * 2 for x in lista]

# Com filtro: [expr for var in iterable if cond]
pares = [x for x in numeros if x % 2 == 0]
```

### With (context manager)
```moonlight
# with expr as var { block }
with recurso as r {
    r.usar()
}
```

### Multiple assignment
```moonlight
# x = y = z = valor
x = y = z = 0

# a = b = c = expr
i = j = k = 10
```

## Classes

### Definição de Classes
```moonlight
# Classe básica
class Pessoa {
    def __init__(nome, idade) {
        self.nome = nome
        self.idade = idade
    }
    
    def apresentar() {
        print("Meu nome é", self.nome)
        print("Tenho", self.idade, "anos")
    }
    
    def aniversario() {
        self.idade = self.idade + 1
    }
}

# Criando instância
p = Pessoa("João", 25)
p.apresentar()
p.aniversario()
```

### Herança
```moonlight
# Classe pai
class Animal {
    def __init__(nome) {
        self.nome = nome
    }
    
    def fazer_som() {
        print("Som genérico")
    }
}

# Classe filha
class Cachorro(Animal) {
    def fazer_som() {
        print("Au au!")
    }
}
```

## Estruturas de Dados

### Listas
```moonlight
# Criação
numeros = [1, 2, 3, 4, 5]
vazio = []

# Acesso
primeiro = numeros[0]
ultimo = numeros[4]

# Modificação
numeros[2] = 99

# Operações
tamanho = len(numeros)
soma = sum(numeros)
maximo = max(numeros)
minimo = min(numeros)
```

### Dicionários
```moonlight
# Criação
pessoa = {"nome": "João", "idade": 25}

# Acesso (quando implementado)
nome = pessoa["nome"]

# Modificação (quando implementado)
pessoa["idade"] = 26
```

### Tuplas
```moonlight
# Criação
coordenadas = (10, 20)
ponto = (1, 2, 3)
```

## Funções Built-in

### Funções de Agregação
```moonlight
lista = [1, 2, 3, 4, 5]

tamanho = len(lista)       # Retorna 5
total = sum(lista)         # Retorna 15
maior = max(lista)         # Retorna 5
menor = min(lista)         # Retorna 1
```

### Funções de Conversão
```moonlight
# Conversão de tipos
x = int(3.14)        # 3
y = float(10)        # 10.0
z = str(42)          # "42"
b = bool(1)          # True

# Verificar tipo
tipo = type(x)
```

### Função range
```moonlight
# range(fim)
r1 = range(5)           # [0, 1, 2, 3, 4]

# range(inicio, fim)
r2 = range(2, 7)        # [2, 3, 4, 5, 6]

# range(inicio, fim, passo)
r3 = range(0, 10, 2)    # [0, 2, 4, 6, 8]
```

### print
```moonlight
# Print simples
print("Olá Mundo")

# Print múltiplos argumentos
print("Valor:", 42)
print("x =", x, "y =", y)
```

## Exemplos Completos

### Exemplo 1: Cálculo de Fatorial
```moonlight
def factorial(n) {
    if (n <= 1) {
        return 1
    }
    return n * factorial(n - 1)
}

resultado = factorial(5)
print("5! =", resultado)
```

### Exemplo 2: Bubble Sort
```moonlight
def bubble_sort(lista) {
    n = len(lista)
    for (i = 0; i < n; i = i + 1) {
        for (j = 0; j < n - 1; j = j + 1) {
            if (lista[j] > lista[j + 1]) {
                temp = lista[j]
                lista[j] = lista[j + 1]
                lista[j + 1] = temp
            }
        }
    }
    return lista
}

numeros = [5, 2, 8, 1, 9]
ordenados = bubble_sort(numeros)
print(ordenados)
```

### Exemplo 3: Verificar Número Primo
```moonlight
def is_prime(n) {
    if (n <= 1) {
        return False
    }
    for (i = 2; i < n; i = i + 1) {
        if (n % i == 0) {
            return False
        }
    }
    return True
}

for (num = 2; num <= 20; num = num + 1) {
    if (is_prime(num)) {
        print(num, "é primo")
    }
}
```

### Exemplo 4: Classe Calculadora
```moonlight
class Calculator {
    def __init__() {
        self.result = 0
    }
    
    def add(value) {
        self.result = self.result + value
        return self.result
    }
    
    def subtract(value) {
        self.result = self.result - value
        return self.result
    }
    
    def multiply(value) {
        self.result = self.result * value
        return self.result
    }
    
    def divide(value) {
        self.result = self.result / value
        return self.result
    }
    
    def clear() {
        self.result = 0
    }
}

calc = Calculator()
calc.add(10)
calc.multiply(5)
calc.subtract(3)
print("Resultado:", calc.result)
```

## Notas Importantes

1. **Blocos de código** são delimitados por chaves `{ }`
2. **Condições** devem estar entre parênteses `( )`
3. **Indentação** não é obrigatória, mas recomendada para legibilidade
4. **Comentários** começam com `#`
5. **Arquivos** MoonLight têm extensão `.gpu`










