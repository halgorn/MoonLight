# Roadmap: Compilação Direta para Assembly

## 🎯 Objetivo

Eliminar **TODAS** as dependências externas:
- ❌ Python (parser, transpiler)
- ❌ C++ (g++, nvcc)
- ❌ LLVM (opcional, mas pode ser usado)

**Gerar diretamente:**
- ✅ Assembly nativo (x86-64, ARM, etc)
- ✅ Ou código objeto (.o)
- ✅ Ou executável direto

---

## 📊 Situação Atual

### Pipeline Atual (Depende de Python + C++)

```
MoonLight (.gpu)
    │
    ├─> Python (parser.py) ──> AST
    │                            │
    │                            ├─> Python (transpiler.py) ──> C++ (.cpp)
    │                            │                                    │
    │                            │                                    ├─> g++/nvcc ──> Executável
    │                            │                                    │
    │                            └─> Python (llvm_backend.py) ──> LLVM IR
    │                                                                    │
    │                                                                    └─> LLVM ──> Assembly/Objeto
    │
    └─> Python (executor_simple.py) ──> Interpretado (lento)
```

### Pipeline Desejado (100% Independente)

```
MoonLight (.gpu)
    │
    ├─> moonc (C++ standalone) ──> AST
    │                                │
    │                                ├─> Backend Assembly ──> .s (assembly)
    │                                │                          │
    │                                │                          └─> as (assembler) ──> .o ──> ld (linker) ──> Executável
    │                                │
    │                                └─> Backend LLVM ──> LLVM IR ──> LLVM ──> Assembly/Objeto
    │
    └─> moonc -r (modo interpretado em C++)
```

---

## 🔍 Opções para Gerar Assembly

### Opção 1: LLVM Backend (Recomendado) ⭐

**Status:** ✅ **Já parcialmente implementado!**

**Vantagens:**
- ✅ LLVM já gera assembly para múltiplas arquiteturas
- ✅ Otimizações automáticas
- ✅ Suporte a x86-64, ARM, RISC-V, etc
- ✅ Já temos `llvm_backend.py` funcionando

**O que falta:**
1. ✅ LLVM IR generation - **JÁ TEMOS** (llvm_backend.py)
2. ❌ LLVM → Assembly (gerar .s)
3. ❌ Assembly → Objeto (usar `llc` ou LLVM API)
4. ❌ Linking (usar `ld` ou LLVM lld)

**Implementação:**
```python
# llvm_backend.py já faz:
llvm_ir = generate_llvm_for_ast(ast)  # ✅ Funciona

# Falta adicionar:
assembly = llvm_compile_to_assembly(llvm_ir)  # ❌ Falta
object_file = llvm_compile_to_object(llvm_ir)  # ❌ Falta
executable = llvm_link(object_file)            # ❌ Falta
```

**Usando LLVM API:**
```python
from llvmlite import binding

# Gerar assembly
target_machine = binding.Target.from_default_triple().create_target_machine()
assembly = target_machine.emit_assembly(llvm_module)  # Gera .s

# Gerar objeto
object_code = target_machine.emit_object(llvm_module)  # Gera .o

# Escrever arquivo
with open('output.s', 'w') as f:
    f.write(assembly)
```

**Estimativa:** 1-2 semanas

---

### Opção 2: Backend Próprio (Mais Trabalho) 🔨

**Criar gerador de assembly do zero**

**Vantagens:**
- ✅ Zero dependências externas
- ✅ Controle total
- ✅ Pode otimizar especificamente para MoonLight

**Desvantagens:**
- ❌ Muito trabalho (6-12 meses)
- ❌ Precisa implementar para cada arquitetura
- ❌ Sem otimizações avançadas

**O que precisa:**
1. ❌ Gerador de assembly x86-64
2. ❌ Gerador de assembly ARM
3. ❌ Sistema de registradores
4. ❌ Calling conventions
5. ❌ Stack management
6. ❌ Otimizações básicas

**Exemplo:**
```python
class AssemblyGenerator:
    def generate_add(self, dest, src1, src2):
        return f"addq {src1}, {src2}  # {dest} = {src1} + {src2}"
    
    def generate_function(self, name, params, body):
        asm = f".globl {name}\n"
        asm += f"{name}:\n"
        asm += "  pushq %rbp\n"
        asm += "  movq %rsp, %rbp\n"
        # ... gerar body
        asm += "  popq %rbp\n"
        asm += "  ret\n"
        return asm
```

**Estimativa:** 6-12 meses

---

### Opção 3: Híbrido (Melhor Caminho) 🎯

**Usar LLVM para gerar assembly, mas sem depender de Python**

**Pipeline:**
```
MoonLight (.gpu)
    │
    └─> moonc_cpp (compilador C++ standalone)
            │
            ├─> Parser C++ ──> AST
            │
            └─> LLVM Backend (C++ API) ──> LLVM IR
                    │
                    └─> LLVM ──> Assembly (.s) ──> Objeto (.o) ──> Executável
```

**Vantagens:**
- ✅ Sem Python
- ✅ Usa LLVM (otimizações)
- ✅ Gera assembly nativo
- ✅ Compilador standalone

**O que falta:**
1. ✅ Parser C++ - **50% completo** (moonc_cpp)
2. ✅ AST C++ - **100% completo**
3. ❌ LLVM Backend em C++ - **0%**
4. ❌ Codegen C++ - **0%**

**Implementação em C++:**
```cpp
// moonc_cpp/src/codegen/llvm_codegen.cpp
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/Module.h>
#include <llvm/IR/LLVMContext.h>

class LLVMCodeGen {
    llvm::LLVMContext context;
    llvm::Module* module;
    llvm::IRBuilder<> builder;
    
public:
    std::string generateAssembly(ASTNode* ast) {
        // Gerar LLVM IR
        llvm::Function* func = generateFunction(ast);
        
        // Compilar para assembly
        std::string assembly;
        llvm::raw_string_ostream os(assembly);
        module->print(os, nullptr);
        
        // Usar llc para gerar assembly
        // ou usar LLVM API diretamente
        return assembly;
    }
};
```

**Estimativa:** 4-6 semanas

---

## 🚀 Plano de Implementação Recomendado

### Fase 1: Completar LLVM Backend Python (1-2 semanas)

**Objetivo:** Gerar assembly diretamente do Python (prova de conceito)

**Tarefas:**
- [ ] Adicionar `generate_assembly()` em `llvm_backend.py`
- [ ] Adicionar `generate_object()` em `llvm_backend.py`
- [ ] Adicionar `link_executable()` em `llvm_backend.py`
- [ ] Testar com exemplos simples
- [ ] Comparar performance com C++

**Código:**
```python
# llvm_backend.py
def generate_assembly(llvm_ir):
    """Gera assembly a partir de LLVM IR"""
    llvm_module = binding.parse_assembly(llvm_ir)
    target_machine = binding.Target.from_default_triple().create_target_machine()
    assembly = target_machine.emit_assembly(llvm_module)
    return assembly

def generate_object(llvm_ir, output_file):
    """Gera arquivo objeto (.o) a partir de LLVM IR"""
    llvm_module = binding.parse_assembly(llvm_ir)
    target_machine = binding.Target.from_default_triple().create_target_machine()
    object_code = target_machine.emit_object(llvm_module)
    with open(output_file, 'wb') as f:
        f.write(object_code)

def link_executable(object_files, output_file):
    """Linka arquivos objeto em executável"""
    # Usar lld ou ld
    import subprocess
    subprocess.run(['ld', '-o', output_file] + object_files)
```

---

### Fase 2: Portar para C++ (moonc_cpp) (4-6 semanas)

**Objetivo:** Compilador standalone em C++ que gera assembly

**Tarefas:**
- [ ] Completar parser C++ (50% → 100%)
- [ ] Implementar LLVM backend em C++
- [ ] Implementar geração de assembly
- [ ] Implementar linking
- [ ] Testes completos

**Arquivos:**
```
moonc_cpp/
├── src/
│   ├── codegen/
│   │   ├── llvm_codegen.cpp  # ❌ Criar
│   │   └── llvm_codegen.h    # ❌ Criar
│   └── ...
```

---

### Fase 3: Eliminar Dependências (1-2 semanas)

**Objetivo:** Compilador 100% standalone

**Tarefas:**
- [ ] Embed LLVM estático (ou usar lld)
- [ ] Testar em diferentes sistemas
- [ ] Documentação
- [ ] Release

---

## 📋 Checklist Completo

### Backend Assembly (LLVM)

- [ ] **Geração de Assembly**
  - [ ] `generate_assembly(llvm_ir)` → `.s`
  - [ ] Suporte x86-64
  - [ ] Suporte ARM (opcional)
  
- [ ] **Geração de Objeto**
  - [ ] `generate_object(llvm_ir)` → `.o`
  - [ ] Suporte ELF (Linux)
  - [ ] Suporte PE (Windows)
  - [ ] Suporte Mach-O (macOS)

- [ ] **Linking**
  - [ ] Link estático
  - [ ] Link dinâmico
  - [ ] Runtime linking

- [ ] **Otimizações**
  - [ ] -O0, -O1, -O2, -O3
  - [ ] Otimizações específicas MoonLight

### Compilador Standalone (moonc_cpp)

- [ ] **Parser Completo**
  - [ ] Todas expressões
  - [ ] Todos statements
  - [ ] Todas features

- [ ] **LLVM Backend C++**
  - [ ] Geração LLVM IR
  - [ ] Geração assembly
  - [ ] Geração objeto

- [ ] **CLI Completo**
  - [ ] `moonc file.gpu -o app` (compilar)
  - [ ] `moonc file.gpu -S` (gerar assembly)
  - [ ] `moonc file.gpu -c` (gerar objeto)
  - [ ] `moonc file.gpu -r` (executar)

---

## 🎯 Resultado Final

### Antes (Depende de Python + C++)

```bash
# Precisa Python
python moonc.py programa.gpu -o app

# Precisa g++
g++ output.cpp -o app
```

### Depois (100% Independente)

```bash
# Só precisa moonc (um binário)
./moonc programa.gpu -o app

# Ou gerar assembly diretamente
./moonc programa.gpu -S -o programa.s

# Ou gerar objeto
./moonc programa.gpu -c -o programa.o
```

**O executável `moonc`:**
- ✅ Não precisa Python
- ✅ Não precisa g++
- ✅ Gera assembly diretamente
- ✅ Linka automaticamente
- ✅ Um binário único

---

## ⏱️ Estimativas

| Fase | Tempo | Dependências |
|------|-------|--------------|
| Fase 1: LLVM Backend Python | 1-2 semanas | llvmlite |
| Fase 2: Portar para C++ | 4-6 semanas | LLVM C++ API |
| Fase 3: Standalone | 1-2 semanas | LLVM estático |
| **TOTAL** | **6-10 semanas** | LLVM (única dependência) |

---

## 🔄 Alternativa: Backend Próprio

Se quiser **ZERO dependências** (nem LLVM):

| Componente | Tempo | Complexidade |
|------------|-------|--------------|
| Gerador Assembly x86-64 | 2-3 meses | Alta |
| Gerador Assembly ARM | 1-2 meses | Média |
| Sistema de Registradores | 1 mês | Média |
| Calling Conventions | 2 semanas | Baixa |
| Stack Management | 2 semanas | Média |
| Otimizações Básicas | 1-2 meses | Alta |
| **TOTAL** | **6-12 meses** | **Muito Alta** |

**Recomendação:** Use LLVM. É muito mais rápido e confiável.

---

## 📚 Referências

- **LLVM Documentation**: https://llvm.org/docs/
- **LLVM IR Language Reference**: https://llvm.org/docs/LangRef.html
- **LLVM C++ API**: https://llvm.org/doxygen/
- **x86-64 Assembly**: https://en.wikibooks.org/wiki/X86_Assembly
- **System V ABI**: https://github.com/hjl-tools/x86-psABI

---

## ✅ Próximos Passos

1. **Imediato:** Implementar `generate_assembly()` em `llvm_backend.py`
2. **Curto prazo:** Completar parser C++ em `moonc_cpp`
3. **Médio prazo:** Portar LLVM backend para C++
4. **Longo prazo:** Compilador 100% standalone

---

**Última atualização:** 2025-01-XX  
**Status:** LLVM backend parcialmente implementado, falta geração de assembly/objeto





