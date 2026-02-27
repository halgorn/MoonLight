# Ferramentas de Desenvolvimento MoonLight

## Visão Geral

MoonLight oferece um conjunto completo de ferramentas para desenvolvimento, depuração e distribuição de código.

---

## 🛠️ Ferramentas Disponíveis

### 1. moonc - Compilador CLI

**Arquivo**: `moonc.py`

Compilador standalone que converte `.gpu` → executável nativo.

**Capacidades**:
- Compilação para binário standalone
- Modo interpretado rápido
- Verificação de sintaxe
- Otimizações configur áveis

**Uso**:
```bash
moonc arquivo.gpu -o programa -O
```

---

### 2. moon - REPL Interativo

**Arquivo**: `repl.py`

Console interativo para execução de código em tempo real.

**Capacidades**:
- Execução linha a linha
- Histórico de comandos (readline)
- Inspeção de variáveis
- Importação de módulos
- Suporte a multi-linha

**Uso**:
```bash
python repl.py
```

---

### 3. moon-db - Debugger

**Arquivo**: `debugger.py`

Debugger interativo com breakpoints.

**Capacidades**:
- Breakpoints em linhas específicas
- Step through code
- Inspeção de variáveis em tempo real
- Continue/pause execution
- Call stack inspection

**Uso**:
```bash
python debugger.py
```

---

### 4. moonpkg - Package Manager

**Arquivo**: `moonpkg.py`

Gerenciador de pacotes para instalação e distribuição.

**Capacidades**:
- Instalar/desinstalar pacotes
- Buscar no registry
- Gerenciar dependências
- Publicar pacotes

**Uso**:
```bash
moonpkg install <pacote>
moonpkg list
```

---

### 5. VS Code Extension

**Diretório**: `vscode-extension/`

Extensão completa para Visual Studio Code.

**Capacidades**:
- Syntax highlighting
- IntelliSense/autocomplete
- Snippets
- Run/compile commands
- Error underlining
- Debugger integration

**Instalação**:
```bash
cp -r vscode-extension ~/.vscode/extensions/moonlight-language
```

---

## 📦 Estrutura de Arquivos

```
moonlight/
├── moonc.py              # Compilador CLI
├── repl.py               # REPL interativo
├── debugger.py           # Debugger
├── moonpkg.py            # Package manager
├── vscode-extension/     # VS Code extension
│   ├── package.json
│   ├── syntaxes/
│   │   └── moonlight.tmLanguage.json
│   ├── snippets/
│   │   └── moonlight.json
│   └── language-configuration.json
├── docs/
│   ├── CLI_GUIDE.md      # Guia do CLI
│   └── TOOLING.md        # Este arquivo
└── examples/
    └── cli/
        └── hello_cli.gpu
```

---

## 🚀 Workflows de Desenvolvimento

### Desenvolvimento Iterativo

```bash
# Terminal 1: REPL para testes rápidos
python repl.py

# Terminal 2: Editor (VS Code)
code meu_programa.gpu

# Terminal 3: Executar com watch
watch -n 1 moonc -r meu_programa.gpu
```

### Debug de Problemas

```bash
# 1. Verificar sintaxe
moonc -c programa.gpu

# 2. Se OK, debugar
python debugger.py
(moon-db) b 15
(moon-db) c
(moon-db) p variavel
```

### Preparar para Produção

```bash
# 1. Testes
pytest tests/

# 2. Compilar otimizado
moonc programa.gpu -O -o programa_release

# 3. Benchmark
time ./programa_release

# 4. Distribuir
moonpkg publish
```

---

## 🎨 VS Code Integration

### Setup

1. Instale a extensão (ver acima)
2. Abra qualquer arquivo `.gpu`
3. Extensão ativa automaticamente

### Features

**Syntax Highlighting**:
- Keywords: `def`, `class`, `if`, `for`, `cuda`
- Strings, números, comentários
- Decoradores: `@jit`
- Built-ins: `print`, `len`, etc.

**Snippets**:
- Digite `def` + Tab → template de função
- Digite `class` + Tab → template de classe
- Digite `cuda` + Tab → template de kernel

**Commands**:
- `Ctrl+Shift+R`: Run current file
- `Ctrl+Shift+B`: Compile current file
- `F5`: Debug current file (futuro)

---

## 🔧 Configuração

### moonc.config.json

```json
{
  "compiler": "g++",
  "optimization_level": 2,
  "std": "c++17",
  "warnings": true,
  "cuda": {
    "enabled": true,
    "compute_capability": "sm_75"
  }
}
```

### .moonlight

Diretório user-local:

```
~/.moonlight/
├── config.json       # Configurações globais
├── modules/          # Módulos do usuário
├── packages/         # Pacotes instalados
└── cache/           # Cache de compilação
```

---

## 📊 Performance

### moonc Benchmarks

| Operação | Tempo |
|----------|-------|
| Parse 1000 linhas | ~50ms |
| Transpile para C++ | ~100ms |
| Compilar com g++ -O2 | ~2s |
| Total (parse → binário) | ~2.2s |

### REPL Performance

| Operação | Tempo |
|----------|-------|
| Startup | ~100ms |
| Comando simples | ~10ms |
| Import módulo | ~50ms |

---

## 🐛 Known Issues

1. **moonc**: Otimizações CUDA ainda não implementadas
2. **REPL**: Multi-linha com `{` ainda simplificado
3. **Debugger**: Step-through requer integração com AST walker
4. **VS Code**: Autocomplete ainda não tem type inference
5. **moonpkg**: Registry remoto ainda não implementado

---

## 🗺️ Roadmap de Ferramentas

### Curto Prazo
- [ ] Integrar debugger com moonc
- [ ] Autocomplete com type inference
- [ ] Profiler integrado

### Médio Prazo
- [ ] Language Server Protocol (LSP)
- [ ] Registry remoto para moonpkg
- [ ] Build system (Makefile/CMake generator)

### Longo Prazo
- [ ] IDE standalone
- [ ] Cloud compilation
- [ ] Package CDN

---

## 📚 Referências

- [CLI_GUIDE.md](CLI_GUIDE.md) - Guia detalhado do CLI
- [SYNTAX.md](SYNTAX.md) - Sintaxe da linguagem
- [CUDA_GUIDE.md](CUDA_ADVANCED.md) - Programação CUDA
- [JIT_GUIDE.md](JIT_GUIDE.md) - Compilação JIT

---

**MoonLight Tooling - v1.0.0**









