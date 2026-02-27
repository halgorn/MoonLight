# MoonLight - Tratamento de Erros

## Tipos de Erros

### 1. Erros Léxicos
Ocorrem quando o lexer encontra caracteres inválidos.

**Exemplo:**
```moonlight
x = 10$  # $ é um caractere inválido
```

**Mensagem de Erro:**
```
Erro léxico: Caractere inválido '$' na linha 1
```

### 2. Erros Sintáticos
Ocorrem quando a estrutura do código não segue a gramática da linguagem.

**Exemplos:**
```moonlight
# Falta de parênteses no if
if x > 5 {
    print(x)
}

# Falta de chaves
if (x > 5)
    print(x)

# Falta de ponto e vírgula no for
for (i = 0 i < 10; i = i + 1) {
    print(i)
}
```

**Mensagens de Erro:**
```
Erro sintático na linha 2, próximo ao token 'x'
Erro sintático: Final inesperado do arquivo ou bloco mal fechado
```

### 3. Erros de Execução
Ocorrem durante a execução do código.

**Exemplos:**
```moonlight
# Divisão por zero
x = 10 / 0

# Acesso a índice inválido
lista = [1, 2, 3]
elemento = lista[10]

# Chamada de função inexistente
resultado = funcao_inexistente()
```

### 4. Erros de Tipo
Ocorrem quando operações são realizadas com tipos incompatíveis.

**Exemplos:**
```moonlight
# Soma de string com número
resultado = "10" + 5

# Operação matemática com None
x = None
y = x + 10
```

## Boas Práticas

### 1. Validação de Entrada
```moonlight
def divide(a, b) {
    if (b == 0) {
        print("Erro: divisão por zero")
        return None
    }
    return a / b
}
```

### 2. Verificação de Limites
```moonlight
def get_element(lista, indice) {
    if (indice < 0 or indice >= len(lista)) {
        print("Erro: índice fora dos limites")
        return None
    }
    return lista[indice]
}
```

### 3. Validação de Tipos
```moonlight
def soma_lista(lista) {
    if (len(lista) == 0) {
        print("Erro: lista vazia")
        return 0
    }
    return sum(lista)
}
```

## Try/Except (Planejado para Entrega 2)

```moonlight
try {
    x = 10 / 0
} except {
    print("Erro capturado!")
}
```

## Assert (Planejado para Entrega 2)

```moonlight
assert (x > 0, "x deve ser positivo")
```










