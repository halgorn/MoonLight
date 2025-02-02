# Moonlight - Linguagem de Programação Otimizada para CUDA

Moonlight é uma linguagem de programação experimental projetada para rodar **cálculos numéricos otimizados usando núcleos CUDA**. Inspirada no **Python**, ela busca oferecer **facilidade de uso**, mas com **desempenho superior em GPUs**.

## 🚀 Recursos da Moonlight

- **Suporte a operações matemáticas básicas** (`+`, `-`, `*`, `/`)
- **Estruturas de controle**: `if`, `else`, `while`, `for`
- **Suporte a variáveis do Python**: inteiros, floats, booleanos e strings
- **Sistema de análise léxica e sintática** usando PLY (Python Lex-Yacc)
- **Execução direta de scripts `.gpu`**
- **Manipulação de listas e vetores** (adição de vetores com otimização CUDA)

## 📥 Instalação

```sh
git clone https://github.com/seu-repo/moonlight-lang.git
cd moonlight-lang
pip install -r requirements.txt
```

## 📝 Uso

Para executar um script `.gpu`, basta rodar:

```sh
python executor_main.py exemplo.gpu
```

Para testar a análise do código sem executá-lo:

```sh
python testador.py exemplo.gpu
```

## 🔥 Exemplo de Código

```moonlight
# Declaração de variáveis
x = 10
y = 5
z = 0

# Estruturas de controle
if (x > y) {
    z = x - y
} else {
    z = y - x
}

# Laços de repetição
while (x > 0) {
    x = x - 1
}

for (i = 0; i < 10; i = i + 1) {
    y = y + 1
}

# Manipulação de listas
lista = [1, 2, 3, 4, 5]
soma = soma(lista)  # Chama a função nativa de soma

# Funções personalizadas
def quadrado(n) {
    return n * n
}

resultado = quadrado(4)  # 16
```

## 🔧 Planejamento para Futuras Melhorias

- [ ] **Suporte total a CUDA:** tradução de código para kernels CUDA
- [ ] **Compilação Just-In-Time (JIT)** para otimizar execuções repetidas
- [ ] **Sistema de módulos e bibliotecas externas**
- [ ] **Integração com IA para otimização automática de código**
