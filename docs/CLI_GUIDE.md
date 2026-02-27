# Guia de Ferramentas CLI do MoonLight

Este guia cobre todas as ferramentas de linha de comando do MoonLight.

---

## 🔨 moonc - Compilador

O `moonc` é o compilador standalone que transforma arquivos `.gpu` em executáveis nativos.

### Uso Básico

```bash
# Compilar arquivo
moonc arquivo.gpu

# Especificar nome do executável
moonc arquivo.gpu -o meu_programa

# Compilar com otimizações
moonc arquivo.gpu -O

# Modo verboso
moonc arquivo.gpu -v
```

### Flags

- `-o, --output <name>`: Nome do executável de saída
- `-O, --optimize`: Habilita otimizações (O2)
- `-v, --verbose`: Saída detalhada
- `-r, --run`: Executa diretamente sem compilar
- `-c, --check`: Apenas verifica sintaxe
- `-S, --asm`: Gera assembly (`.s`) via LLVM (requer `llvmlite`; apenas funções host)
- `--emit-obj`: Gera arquivo objeto (`.o`) via LLVM (requer `llvmlite`; apenas funções host)
- `--version`: Mostra versão

### Exemplos

**Compilar e executar:**
```bash
moonc hello.gpu
./hello
```

**Verificar sintaxe sem compilar:**
```bash
moonc -c meu_codigo.gpu
```

**Executar diretamente (interpretado):**
```bash
moonc -r script.gpu
```

**Gerar assembly ou objeto via LLVM** (requer `pip install llvmlite`):
```bash
moonc -S arquivo.gpu -o saida.s    # gera saida.s
moonc --emit-obj arquivo.gpu -o saida.o  # gera saida.o
```

---

## 🖥️ moon - REPL Interativo

O REPL (Read-Eval-Print Loop) permite executar código MoonLight interativamente.

### Iniciando o REPL

```bash
python repl.py
```

### Comandos Especiais

- `help`: Mostra ajuda
- `exit` / `quit`: Sai do REPL
- `vars`: Mostra todas as variáveis definidas
- `clear`: Limpa todas as variáveis
- `reset`: Reseta o REPL
- `history`: Mostra histórico de comandos

### Exemplos de Uso

```moonlight
moon> x = 10
moon> y = 20
moon> print(x + y)
30

moon> def square(n) { return n * n }
moon> square(5)
25

moon> for i in range(3) {
...       print(i)
...   }
0
1
2

moon> from math import PI
moon> print(PI)
3.141592653589793

moon> vars
Defined variables:
  x = 10
  y = 20
  square: <function>
  PI = 3.141592653589793
```

### Atalhos de Teclado

- **Ctrl+D**: Sair do REPL
- **Ctrl+C**: Interromper comando atual
- **↑/↓**: Navegar no histórico

---

## 🐛 moon-db - Debugger

O debugger permite depurar programas MoonLight com breakpoints e inspeção de variáveis.

### Iniciando o Debugger

```bash
python debugger.py
```

### Comandos do Debugger

- `b <line>`: Define breakpoint na linha
- `d <line>`: Remove breakpoint da linha
- `l`: Lista todos os breakpoints
- `s`: Step (próxima linha)
- `c`: Continue (continua execução)
- `p <var>`: Imprime valor da variável
- `vars`: Lista todas as variáveis
- `q`: Sair do debugger
- `h` / `help`: Mostra ajuda

### Exemplo de Sessão de Debug

```
(moon-db) b 10
Breakpoint set at line 10

(moon-db) c
Continuing...
[Hit breakpoint at line 10]

(moon-db) p x
x = 42

(moon-db) vars
Variables:
  x = 42
  y = 100
  result = 142

(moon-db) s
Stepping...

(moon-db) q
Quitting debugger
```

---

## 📦 moonpkg - Gerenciador de Pacotes

O `moonpkg` gerencia instalação e distribuição de pacotes MoonLight.

### Comandos

**Instalar pacote:**
```bash
python moonpkg.py install <pacote>
```

**Desinstalar pacote:**
```bash
python moonpkg.py uninstall <pacote>
```

**Listar pacotes instalados:**
```bash
python moonpkg.py list
```

**Buscar pacotes:**
```bash
python moonpkg.py search <termo>
```

**Informações do pacote:**
```bash
python moonpkg.py info <pacote>
```

### Exemplos

```bash
# Instalar pacote de utilidades
moonpkg install moonlight-utils

# Listar instalados
moonpkg list

# Buscar pacotes de IA
moonpkg search ai

# Ver informações
moonpkg info moonlight-ai

# Desinstalar
moonpkg uninstall moonlight-utils
```

### Diretórios de Pacotes

Pacotes são instalados em:
- **Linux/Mac**: `~/.moonlight/packages/`
- **Windows**: `%USERPROFILE%\.moonlight\packages\`

---

## 🎨 VS Code Extension

A extensão para VS Code oferece suporte completo para desenvolvimento em MoonLight.

### Instalação

1. Copie a pasta `vscode-extension` para:
   - **Linux/Mac**: `~/.vscode/extensions/`
   - **Windows**: `%USERPROFILE%\.vscode\extensions\`

2. Recarregue o VS Code

### Recursos

- ✅ **Syntax Highlighting**: Destaque de sintaxe completo
- ✅ **Snippets**: Atalhos para código comum
- ✅ **Autocomplete**: Sugestões de código
- ✅ **Run Command**: Executar arquivo (Ctrl+Shift+R)
- ✅ **Compile Command**: Compilar para executável

### Atalhos de Teclado

- **Ctrl+Shift+R**: Executar arquivo MoonLight
- **Ctrl+Shift+B**: Compilar arquivo

### Snippets Disponíveis

- `def` → Definição de função
- `class` → Definição de classe
- `for` → Loop for
- `while` → Loop while
- `if` → Condicional if-else
- `cuda` → Kernel CUDA
- `jit` → Função JIT
- `lambda` → Expressão lambda
- `import` → Importar módulo

---

## 🚀 Exemplos Rápidos

### Workflow de Desenvolvimento Típico

```bash
# 1. Criar arquivo
nano meu_programa.gpu

# 2. Verificar sintaxe
moonc -c meu_programa.gpu

# 3. Executar interpretado (rápido para testes)
moonc -r meu_programa.gpu

# 4. Compilar otimizado (para produção)
moonc meu_programa.gpu -O -o meu_programa

# 5. Executar binário
./meu_programa
```

### Testando no REPL

```bash
python repl.py
```

```moonlight
moon> def fibonacci(n) {
...       if (n <= 1) { return n }
...       return fibonacci(n-1) + fibonacci(n-2)
...   }
moon> fibonacci(10)
55
```

### Debug de Problemas

```bash
python debugger.py
```

---

## 📊 Comparação de Modos de Execução

| Modo | Comando | Velocidade | Uso |
|------|---------|-----------|-----|
| **Interpretado** | `moonc -r` | Lento | Desenvolvimento rápido |
| **JIT** | `@jit` no código | Médio | Loops intensivos |
| **Compilado** | `moonc -O` | Rápido | Produção |
| **CUDA** | Kernels CUDA | Muito Rápido | Paralelismo GPU |

---

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

```bash
# Diretório de módulos customizado
export MOONLIGHT_MODULES_PATH=/meu/caminho

# Habilitar debug do compilador
export MOONLIGHT_DEBUG=1

# Nível de otimização padrão
export MOONLIGHT_OPT_LEVEL=2
```

### Arquivo de Configuração

Crie `~/.moonlight/config.json`:

```json
{
  "compiler": {
    "optimization_level": 2,
    "verbose": false
  },
  "repl": {
    "history_size": 1000,
    "multiline_mode": true
  },
  "debugger": {
    "auto_vars": true
  }
}
```

---

## 🆘 Troubleshooting

### moonc não encontrado
```bash
# Adicione ao PATH ou use caminho completo
export PATH=$PATH:/caminho/para/moonlight
```

### Erro de compilação C++
```bash
# Verifique se g++ está instalado
g++ --version

# Ou use clang++
moonc arquivo.gpu --compiler=clang++
```

### REPL não responde
- Pressione Ctrl+C para interromper
- Use `reset` para limpar estado

### Debugger não funciona
- Verifique se o arquivo tem números de linha
- Use `moonc -c` para validar sintaxe primeiro

---

## 📚 Recursos Adicionais

- **Documentação completa**: `docs/`
- **Exemplos**: `examples/`
- **Testes**: `tests/`
- **Stdlib**: `stdlib/`

---

**MoonLight - Compilador CLI v1.0.0**









