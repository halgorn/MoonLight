# MoonLight - Capacidades e Limitações Atuais

## ✅ O que MoonLight PODE fazer

### 1. **Menus e Lógica de Controle** ✅
**SIM, você pode criar menus!**

```moonlight
def mostrar_menu() {
    print("1. Opcao A")
    print("2. Opcao B")
    print("3. Sair")
}

opcao = 1

if (opcao == 1) {
    print("Executando A")
} else if (opcao == 2) {
    print("Executando B")
} else {
    print("Saindo")
}
```

**Limitação**: Sem `input()` nativo ainda. Você precisa pré-definir as escolhas ou integrá-las via Python.

---

### 2. **Loops Complexos** ✅
**SIM, loops funcionam perfeitamente!**

```moonlight
# While loop
i = 0
while (i < 10) {
    print("Iteracao:", i)
    i = i + 1
}

# For loop
for (j = 0; j < 5; j = j + 1) {
    print("Loop for:", j)
}

# Loops aninhados
x = 0
while (x < 3) {
    y = 0
    while (y < 3) {
        print("(", x, ",", y, ")")
        y = y + 1
    }
    x = x + 1
}
```

---

### 3. **Estruturas de Dados Complexas** ✅
**SIM, você pode usar listas, dicts, sets!**

```moonlight
# Listas
tarefas = ["Estudar", "Trabalhar", "Descansar"]
print(tarefas[0])

# Dicionários
config = {"nome": "MoonLight", "versao": 1.0}
print(config["nome"])

# Sets
numeros = {1, 2, 3, 4, 5}
```

---

### 4. **Funções e Recursão** ✅
**SIM, totalmente funcional!**

```moonlight
# Função simples
def soma(a, b) {
    return a + b
}

# Recursão
def fatorial(n) {
    if (n <= 1) {
        return 1
    }
    return n * fatorial(n - 1)
}

print(fatorial(5))  # 120
```

---

### 5. **Classes e POO Básica** ⚠️
**PARCIALMENTE - POO básica funciona**

```moonlight
class Pessoa {
    def __init__(nome, idade) {
        self.nome = nome
        self.idade = idade
    }
    
    def saudar() {
        print("Oi, sou", self.nome)
    }
}

p = Pessoa("Bruno", 30)
p.saudar()
```

**Limitação**: Herança e métodos avançados têm limitações.

---

### 6. **Operações Matemáticas Avançadas** ✅
**SIM, totalmente!**

```moonlight
# Aritméticas
resultado = (10 + 5) * 2 - 3 / 2

# Bitwise
x = 10 & 5
y = 10 | 5
z = 10 ^ 5

# Potência
potencia = 2 ** 10  # 1024

# Módulo
resto = 17 % 5
```

---

### 7. **Módulos e Imports** ✅
**SIM, sistema de módulos funciona!**

```moonlight
from math import PI, sqrt, factorial

print("PI =", PI)
print("sqrt(16) =", sqrt(16))
print("5! =", factorial(5))
```

---

### 8. **CUDA e GPU Acceleration** ✅
**SIM, kernels CUDA funcionam!**

```moonlight
cuda kernel def add_vectors(a, b, c, n) {
    idx = threadIdx_x + blockIdx_x * blockDim_x
    if (idx < n) {
        c[idx] = a[idx] + b[idx]
    }
}

# Processar 1000 elementos em paralelo
gpu[10, 100] add_vectors(a, b, c, 1000)
```

---

### 9. **JIT Compilation** ✅
**SIM, otimização JIT funciona!**

```moonlight
from jit_decorator import jit

@jit
def soma_intensiva(n) {
    total = 0
    i = 0
    while (i < n) {
        total = total + i
        i = i + 1
    }
    return total
}

# Execução otimizada
resultado = soma_intensiva(1000000)
```

---

### 10. **Lambdas e Generators** ✅
**SIM, funcionam!**

```moonlight
# Lambda
quadrado = lambda(x) x * x
print(quadrado(5))  # 25

# Generator (básico)
def contador(n) {
    i = 0
    while (i < n) {
        yield i
        i = i + 1
    }
}
```

---

## ❌ O que MoonLight NÃO PODE fazer (ainda)

### 1. **Interfaces Gráficas (GUI)** ❌
**NÃO - MoonLight não tem suporte a GUI nativo**

**Porquê**: 
- MoonLight é focado em computação numérica e CUDA
- Não possui bindings para Tkinter, PyQt, wxPython, etc.

**Alternativas**:
- Integrar com Python para GUI:
  ```python
  # Em Python
  import tkinter as tk
  from executor_simple import interpretar
  from parser import parser
  
  # Executar código MoonLight dentro do Python
  codigo_moon = "x = 10; y = 20; z = x + y"
  ast = parser.parse(codigo_moon)
  interpretar(ast)
  ```

---

### 2. **Input Interativo Nativo** ⚠️
**LIMITADO - Sem `input()` built-in**

**Porquê**: 
- `input()` não está implementado como built-in

**Alternativas**:
- Use Python para input e passe para MoonLight
- Use REPL para interatividade
- Pré-defina valores no código

---

### 3. **Networking/HTTP** ❌
**NÃO - Sem suporte a rede**

- Sem `requests`, `socket`, `http`
- Focado em computação local/GPU

---

### 4. **File I/O Avançado** ⚠️
**LIMITADO - Sem `open()`, `read()`, `write()`**

**Alternativa**:
- Usar Python para I/O e processar dados com MoonLight

---

### 5. **Multithreading Python-style** ❌
**NÃO - Mas tem CUDA para paralelismo!**

- Sem `threading` ou `multiprocessing`
- Use CUDA para paralelismo massivo na GPU

---

### 6. **Bibliotecas Python Externas** ⚠️
**LIMITADO - Apenas stdlib MoonLight**

- Sem `numpy`, `pandas`, `matplotlib` diretamente
- Biblioteca AI própria em desenvolvimento

---

## 🎯 Use Cases Ideais para MoonLight

### ✅ **Perfeitamente Adequado:**

1. **Computação Numérica**
   ```moonlight
   # Cálculos intensivos
   def monte_carlo_pi(n) {
       dentro = 0
       i = 0
       while (i < n) {
           # Simulação Monte Carlo
           i = i + 1
       }
       return dentro
   }
   ```

2. **Processamento Paralelo em GPU**
   ```moonlight
   cuda kernel def processar_imagem(input, output, n) {
       idx = threadIdx_x + blockIdx_x * blockDim_x
       if (idx < n) {
           output[idx] = input[idx] * 2.0
       }
   }
   ```

3. **Algoritmos e Estruturas de Dados**
   ```moonlight
   def quicksort(arr) {
       # Implementação de quicksort
       # Totalmente viável!
   }
   ```

4. **Simulações Científicas**
   ```moonlight
   def simular_particulas(n_particulas, tempo) {
       # Física de partículas
       # Ideal para GPU!
   }
   ```

5. **Machine Learning (com AI library)**
   ```moonlight
   from ai.nn import Linear, relu
   from ai.optim import SGD
   
   model = Linear(10, 5)
   optimizer = SGD(0.01)
   ```

---

### ❌ **NÃO Recomendado:**

1. **Aplicações Desktop com GUI**
   - Use Python + PyQt/Tkinter
   - MoonLight para backend de cálculos

2. **Web Servers**
   - Use Python + Flask/Django
   - MoonLight para processamento pesado

3. **Aplicações com I/O intensivo**
   - Use Python para I/O
   - MoonLight para processamento

4. **Mobile Apps**
   - Não é o foco de MoonLight

---

## 💡 Como Fazer um Menu Interativo REAL

### Opção 1: REPL Interativo
```bash
python repl.py
```
```moonlight
moon> def menu() { print("1. A 2. B 3. C") }
moon> menu()
moon> opcao = 1
moon> if (opcao == 1) { print("A") }
```

### Opção 2: Integração com Python
```python
# menu_app.py
from parser import parser
from executor_simple import interpretar

while True:
    print("1. Calcular")
    print("2. Sair")
    escolha = input("Escolha: ")
    
    if escolha == "1":
        codigo = "x = 10; y = 20; print(x + y)"
        ast = parser.parse(codigo)
        interpretar(ast)
    elif escolha == "2":
        break
```

### Opção 3: Menu Pré-programado
```moonlight
# Simula menu com lista de opções
opcoes = [1, 2, 3, 0]

i = 0
while (i < len(opcoes)) {
    opcao = opcoes[i]
    
    if (opcao == 1) {
        print("Executando A")
    } else if (opcao == 2) {
        print("Executando B")
    } else if (opcao == 0) {
        print("Saindo")
    }
    
    i = i + 1
}
```

---

## 📊 Resumo de Capacidades

| Feature | Status | Limitações |
|---------|--------|-----------|
| Menus (lógica) | ✅ Sim | Sem input() nativo |
| Loops (while/for) | ✅ Sim | Nenhuma |
| Recursão | ✅ Sim | Nenhuma |
| Funções | ✅ Sim | Nenhuma |
| Classes | ⚠️ Básico | Herança limitada |
| Listas/Dicts | ✅ Sim | Nenhuma |
| Operações Math | ✅ Sim | Nenhuma |
| CUDA/GPU | ✅ Sim | Requer nvcc |
| JIT | ✅ Sim | Requer llvmlite |
| GUI | ❌ Não | Não suportado |
| Input interativo | ⚠️ Limitado | Sem built-in |
| Networking | ❌ Não | Não suportado |
| File I/O | ⚠️ Limitado | Sem built-ins |

---

## 🚀 Próximos Passos para GUIs

Se você REALMENTE precisa de GUI, considere:

1. **Hybrid Approach**:
   ```python
   # Python para GUI
   import tkinter as tk
   from moonlight import executar
   
   def calcular():
       resultado = executar("x = 10; y = 20; x + y")
       label.config(text=resultado)
   
   root = tk.Tk()
   button = tk.Button(root, text="Calcular", command=calcular)
   ```

2. **Web Interface**:
   - Flask/Django para frontend
   - MoonLight para backend de cálculos
   - REST API entre eles

3. **Terminal UI** (TUI):
   - Use `curses` em Python
   - Chame MoonLight para lógica

---

## 🎯 Conclusão

**Você PODE fazer:**
- ✅ Menus (lógica de controle)
- ✅ Loops complexos
- ✅ Algoritmos avançados
- ✅ Computação paralela (CUDA)
- ✅ Machine Learning (AI library)
- ✅ Cálculos numéricos intensivos

**Você NÃO PODE fazer (nativamente):**
- ❌ Interfaces gráficas (GUI)
- ❌ Input interativo em tempo real
- ❌ Networking/HTTP
- ❌ File I/O avançado

**MoonLight é IDEAL para:**
- Computação numérica
- GPU acceleration
- Algoritmos científicos
- Machine Learning
- Simulações

**MoonLight NÃO é ideal para:**
- Aplicações desktop com GUI
- Web servers
- Apps mobile

---

**Para GUI**: Use Python + Tkinter/PyQt e chame MoonLight para processamento pesado! 🚀









