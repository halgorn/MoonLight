# Implementação: Geração Direta de Assembly

## Status Atual

✅ **LLVM Backend existe** (`llvm_backend.py`)
- Gera LLVM IR
- Compila JIT
- ❌ **FALTA:** Gerar assembly/objeto estático

## Implementação Rápida

### 1. Adicionar Funções em `llvm_backend.py`

```python
def generate_assembly_from_ast(func_ast):
    """Gera assembly a partir de AST"""
    llvm_ir = generate_llvm_for_ast(func_ast)
    if not llvm_ir:
        return None
    
    return generate_assembly_from_ir(llvm_ir)

def generate_assembly_from_ir(llvm_ir):
    """Gera assembly a partir de LLVM IR"""
    if not LLVM_AVAILABLE:
        return None
    
    try:
        # Parse LLVM IR
        llvm_module = binding.parse_assembly(llvm_ir)
        llvm_module.verify()
        
        # Criar target machine
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine(opt=2)  # -O2
        
        # Gerar assembly
        assembly = target_machine.emit_assembly(llvm_module)
        return assembly
    except Exception as e:
        print(f"Erro ao gerar assembly: {e}")
        return None

def generate_object_from_ir(llvm_ir, output_file):
    """Gera arquivo objeto (.o) a partir de LLVM IR"""
    if not LLVM_AVAILABLE:
        return False
    
    try:
        # Parse LLVM IR
        llvm_module = binding.parse_assembly(llvm_ir)
        llvm_module.verify()
        
        # Criar target machine
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine(opt=2)
        
        # Gerar objeto
        object_code = target_machine.emit_object(llvm_module)
        
        # Escrever arquivo
        with open(output_file, 'wb') as f:
            f.write(bytes(object_code))
        
        return True
    except Exception as e:
        print(f"Erro ao gerar objeto: {e}")
        return False
```

### 2. Atualizar `moonc.py`

```python
def compile_to_assembly(input_file, output_file=None):
    """Compila para assembly"""
    # Parse
    ast = parser.parse(codigo)
    
    # Gerar LLVM IR
    from llvm_backend import generate_llvm_for_ast, generate_assembly_from_ir
    
    if isinstance(ast, list) and len(ast) > 0:
        func_ast = ast[0]
        llvm_ir = generate_llvm_for_ast(func_ast)
        assembly = generate_assembly_from_ir(llvm_ir)
        
        # Escrever assembly
        if not output_file:
            output_file = Path(input_file).stem + '.s'
        
        with open(output_file, 'w') as f:
            f.write(assembly)
        
        print(f"[SUCESSO] Assembly gerado: {output_file}")
        return 0
```

### 3. Usar

```bash
# Gerar assembly
python moonc.py programa.gpu -S -o programa.s

# Compilar assembly
as programa.s -o programa.o
ld programa.o -o programa

# Executar
./programa
```

## Próximos Passos

1. ✅ Implementar funções acima
2. ✅ Testar com exemplo simples
3. ✅ Adicionar suporte a múltiplas funções
4. ✅ Adicionar runtime linking
5. ✅ Portar para C++ (moonc_cpp)





