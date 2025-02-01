# MoonLight

MoonLight é um compilador para uma linguagem de programação otimizada para GPUs via CUDA. Ele permite a execução de operações matemáticas aceleradas, aproveitando a capacidade computacional das placas de vídeo.

## 🚀 Funcionalidades
- **Execução de expressões matemáticas** com suporte a operações básicas (`+`, `-`, `*`, `/`).
- **Análise Léxica e Sintática** utilizando `PLY`.
- **Interpretação da AST** para execução do código.
- **Planejada:** Suporte a CUDA para aceleração computacional.

## 📌 Estrutura do Projeto
- `lexer.py` → Tokenização do código-fonte.
- `parser.py` → Análise sintática e geração da AST.
- `executor.py` → Interpretação e execução do código.
- `executor_main.py` → Interface para executar scripts `.gpu`.
- `testador.py` → Validação de código e geração de AST.

## 🎮 Como Usar
### **Instalação**
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-repo/moonlight.git
   cd moonlight
