# Exemplos no subset moonc_cpp

Estes exemplos usam **apenas** o subset suportado pelo compilador C++ (kernels, host, `device[n]`, control flow, `print`, variáveis, sem `class`, `import`, `gpu_resident`, pipeline declarativo).

| Exemplo | Descrição |
|---------|-----------|
| `examples/basic/hello_world.gpu` | Apenas `print` |
| `examples/basic/variables.gpu` | Variáveis e expressões |
| `examples/cuda/vector_add.gpu` | Kernel + host + `device[n]` + `gpu[blocks, threads] kernel(args)` |

Outros em `examples/` usam classes, imports, `gpu_resident`, pipeline, etc. e devem ser compilados com a toolchain Python: `python moonc.py arquivo.gpu -o app`.

## Como validar

Com o binário moonc (C++) construído em `build/`:

```bash
# Verificar sintaxe dos exemplos do subset
./build/moonc -c examples/basic/hello_world.gpu
./build/moonc -c examples/basic/variables.gpu
./build/moonc -c examples/cuda/vector_add.gpu
```

Ou use o script de smoke: `python run_subset_smoke.py` (procura o binário moonc em `build/` ou no PATH).
