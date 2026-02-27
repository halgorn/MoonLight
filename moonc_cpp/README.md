# MoonLight C++ Compiler

Compilador standalone do MoonLight escrito em C++ para eliminar dependência do Python.

## Subconjunto da linguagem suportado (moonc_cpp)

O compilador C++ cobre um **subconjunto** da linguagem MoonLight, focado em programas GPU:

- **Suportado:** `cuda kernel def`, lançamentos `gpu[blocks, threads] kernel(args)`, alocação `device[n]`, transferências de memória, funções host, variáveis, `if`/`while`/`for`, `print`, chamadas de função, expressões e operadores usuais, lambdas, tipos básicos (int, float, etc.).
- **Não suportado neste compilador:** classes (`class`), imports (`import`/`from`), try/except, async/await, decoradores `@jit`/`@profile`, declarações `gpu_resident`, pipeline declarativo (`pipeline`/`stage`), e outros constructs do parser Python.

Para usar a linguagem **completa** (incluindo classes, módulos, JIT, etc.), use a toolchain Python: `python moonc.py arquivo.gpu -o app`. O executável gerado continua independente do Python.

Lista de exemplos que usam só o subset: [SUBSET_EXAMPLES.md](SUBSET_EXAMPLES.md). Para validar: `python run_subset_smoke.py` (requer moonc construído em `build/`).

## Estrutura

```
moonc_cpp/
├── src/
│   ├── lexer/          # Análise léxica
│   ├── parser/         # Análise sintática
│   ├── ast/            # Abstract Syntax Tree
│   ├── codegen/        # Geração de código
│   ├── runtime/        # Runtime support
│   └── main.cpp        # CLI principal
├── include/            # Headers públicos
├── tests/              # Testes unitários
└── CMakeLists.txt      # Build system
```

## Requisitos

- C++17 ou superior
- CMake 3.15+
- LLVM 14+ (para backend)
- CUDA Toolkit (opcional, para suporte GPU)

## Build

```bash
mkdir build
cd build
cmake ..
make -j8
```

## Uso

```bash
# Compilar programa
./moonc programa.gpu -o app

# Executar diretamente
./moonc -r programa.gpu

# Verificar sintaxe
./moonc -c programa.gpu
```

## Paridade de sintaxe (opcional / roadmap)

O subset atual **não** inclui:

- **Classes** (`class`, métodos, `self`, herança): para programas que usam apenas kernels + host + tipos básicos, o subset é suficiente. Suporte a classes pode ser adicionado depois ao parser C++ se desejado.
- **Imports** (`import foo`, `from foo import bar`): não suportados no moonc_cpp; use a toolchain Python para programas com módulos.

Paridade futura (opcional): estender o parser C++ para declarações `class` e um subset mínimo de imports (ex.: `import foo` sem ciclos) está no roadmap.

## Roadmap

- [x] Estrutura inicial
- [x] Lexer completo
- [x] Parser recursivo descendente (subset: kernels, host, control flow)
- [x] AST em C++
- [x] Geração PTX (codegen/ptx_generator)
- [x] Runtime (CUDALoader, Executor, MemoryManager)
- [ ] Paridade opcional com parser Python (classes, imports, etc.)
- [ ] LLVM backend (opcional)
- [ ] Otimizações







