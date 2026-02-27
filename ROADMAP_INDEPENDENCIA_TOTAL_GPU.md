# Roadmap: Independência Total - MoonLight 100% GPU

## 🎯 Objetivo Final

**MoonLight completamente independente:**
- ❌ **SEM Python** (compilador standalone)
- ❌ **SEM C++** (não gera C++, gera PTX direto)
- ❌ **SEM nvcc** (carrega PTX diretamente na GPU)
- ✅ **100% GPU** (código roda direto na placa de vídeo)

---

## 📊 Situação Atual vs Desejada

### ❌ Pipeline Atual (Depende de Python + C++ + nvcc)

```
MoonLight (.gpu)
    │
    ├─> Python (parser.py) ──> AST
    │                            │
    │                            └─> Python (cuda_codegen.py) ──> CUDA C++ (.cu)
    │                                                                    │
    │                                                                    └─> nvcc ──> PTX ──> GPU
    │
    └─> Python (executor_simple.py) ──> Interpretado (CPU)
```

**Problemas:**
- ❌ Precisa Python instalado
- ❌ Precisa nvcc (CUDA Toolkit)
- ❌ Gera C++ intermediário
- ❌ Compilação lenta (nvcc é pesado)

---

### ✅ Pipeline Desejado (100% Independente)

```
MoonLight (.gpu)
    │
    └─> moonc (binário standalone) ──> AST
                                          │
                                          └─> PTX Generator ──> PTX (.ptx)
                                                                  │
                                                                  └─> CUDA Runtime API ──> GPU (direto!)
```

**Vantagens:**
- ✅ Um binário único (`moonc`)
- ✅ Gera PTX diretamente (sem nvcc)
- ✅ Carrega PTX na GPU via CUDA Runtime
- ✅ Compilação instantânea
- ✅ Zero dependências externas

---

## 🚀 Fase 1: Compilador Standalone (4-6 semanas)

### 1.1 Completar moonc_cpp (Parser + AST)

**Status:** 50% completo

**O que falta:**
- [ ] Completar parser C++ (50% → 100%)
- [ ] Suportar todas features MoonLight
- [ ] Testes completos

**Arquivos:**
```
moonc_cpp/
├── src/
│   ├── parser/parser.cpp  # ❌ Completar
│   └── ast/ast_node.cpp   # ✅ Pronto
```

**Estimativa:** 2-3 semanas

---

### 1.2 PTX Generator (Novo!)

**Objetivo:** Gerar PTX assembly diretamente da AST

**PTX (Parallel Thread Execution)** é o assembly da NVIDIA:
- ✅ Formato texto legível
- ✅ Carregado diretamente na GPU
- ✅ Não precisa nvcc
- ✅ Compilação instantânea

**Exemplo PTX:**
```ptx
.version 7.0
.target sm_75
.address_size 64

.entry add_vectors(.param .u64 a, .param .u64 b, .param .u64 c, .param .u32 n) {
    .reg .u32 %tid;
    .reg .u64 %ra, %rb, %rc;
    .reg .f32 %fa, %fb, %fc;
    
    mov.u32 %tid, %tid.x;
    ld.param.u64 %ra, [a];
    ld.param.u64 %rb, [b];
    ld.param.u64 %rc, [c];
    
    mul.wide.u32 %ra, %tid, 4;
    add.u64 %ra, %ra, %ra;
    add.u64 %rb, %rb, %ra;
    add.u64 %rc, %rc, %ra;
    
    ld.global.f32 %fa, [%ra];
    ld.global.f32 %fb, [%rb];
    add.f32 %fc, %fa, %fb;
    st.global.f32 [%rc], %fc;
    
    ret;
}
```

**Implementação:**
```cpp
// moonc_cpp/src/codegen/ptx_generator.cpp
class PTXGenerator {
    std::string generatePTX(ASTNode* ast) {
        std::string ptx = ".version 7.0\n";
        ptx += ".target sm_75\n";
        ptx += ".address_size 64\n\n";
        
        // Gerar kernels
        for (auto kernel : ast->kernels) {
            ptx += generateKernelPTX(kernel);
        }
        
        return ptx;
    }
    
    std::string generateKernelPTX(KernelAST* kernel) {
        std::string ptx = ".entry " + kernel->name + "(";
        // ... gerar parâmetros
        ptx += ") {\n";
        
        // Gerar corpo
        ptx += translateBody(kernel->body);
        
        ptx += "    ret;\n";
        ptx += "}\n\n";
        return ptx;
    }
};
```

**Tarefas:**
- [ ] Criar `ptx_generator.cpp`
- [ ] Implementar geração de PTX básico
- [ ] Suportar operações aritméticas
- [ ] Suportar memória global/shared
- [ ] Suportar built-in variables (threadIdx, etc)
- [ ] Suportar sincronização (bar.sync)
- [ ] Testes com exemplos simples

**Estimativa:** 3-4 semanas

---

### 1.3 CUDA Runtime Integration

**Objetivo:** Carregar PTX diretamente na GPU (sem nvcc)

**CUDA Runtime API:**
```cpp
// moonc_cpp/src/runtime/cuda_loader.cpp
#include <cuda.h>
#include <cuda_runtime.h>

class CUDALoader {
public:
    CUmodule loadPTX(const std::string& ptx_code) {
        CUmodule module;
        CUresult result = cuModuleLoadData(&module, ptx_code.c_str());
        if (result != CUDA_SUCCESS) {
            // Error handling
        }
        return module;
    }
    
    CUfunction getFunction(CUmodule module, const std::string& name) {
        CUfunction func;
        cuModuleGetFunction(&func, module, name.c_str());
        return func;
    }
    
    void launchKernel(CUfunction func, 
                      int blocks, int threads,
                      void** args) {
        cuLaunchKernel(func,
                      blocks, 1, 1,    // grid
                      threads, 1, 1,   // block
                      0, NULL,         // shared mem, stream
                      args, NULL);
    }
};
```

**Tarefas:**
- [ ] Implementar `cuda_loader.cpp`
- [ ] Carregar PTX via `cuModuleLoadData`
- [ ] Obter funções via `cuModuleGetFunction`
- [ ] Lançar kernels via `cuLaunchKernel`
- [ ] Error handling completo
- [ ] Testes

**Estimativa:** 1-2 semanas

---

## 🚀 Fase 2: Compilador Completo (2-3 semanas)

### 2.1 CLI Completo

**Comandos:**
```bash
# Compilar para PTX
./moonc programa.gpu -S -o programa.ptx

# Compilar e executar (carrega PTX na GPU)
./moonc programa.gpu -o programa

# Executar PTX existente
./moonc -r programa.ptx
```

**Tarefas:**
- [ ] Flag `-S` (gerar PTX)
- [ ] Flag `-o` (compilar e executar)
- [ ] Flag `-r` (executar PTX)
- [ ] Flag `-O` (otimizações)

**Estimativa:** 1 semana

---

### 2.2 Otimizações PTX

**Otimizações básicas:**
- [ ] Register allocation
- [ ] Instruction scheduling
- [ ] Dead code elimination
- [ ] Constant folding
- [ ] Loop unrolling

**Estimativa:** 1-2 semanas

---

## 🚀 Fase 3: Runtime Standalone (1-2 semanas)

### 3.1 Embed CUDA Runtime

**Objetivo:** Binário único com CUDA Runtime embutido

**Opções:**
1. **Static linking** (recomendado)
   - Linkar libcudart estaticamente
   - Binário maior, mas standalone

2. **Dynamic loading**
   - Carregar libcudart.so/dll dinamicamente
   - Verificar se CUDA está instalado

**Tarefas:**
- [ ] Configurar CMake para static linking
- [ ] Testar em diferentes sistemas
- [ ] Documentação

**Estimativa:** 1 semana

---

## 📋 Checklist Completo

### Compilador Standalone
- [ ] **Parser C++ Completo**
  - [ ] Todas expressões
  - [ ] Todos statements
  - [ ] Todas features CUDA
  
- [ ] **PTX Generator**
  - [ ] Geração básica de PTX
  - [ ] Operações aritméticas
  - [ ] Memória (global, shared, local)
  - [ ] Built-in variables
  - [ ] Sincronização
  - [ ] Control flow (if, while, for)
  - [ ] Funções device
  
- [ ] **CUDA Runtime Integration**
  - [ ] Carregar PTX
  - [ ] Obter funções
  - [ ] Lançar kernels
  - [ ] Memory management
  - [ ] Error handling

### Otimizações
- [ ] Register allocation
- [ ] Instruction scheduling
- [ ] Dead code elimination
- [ ] Constant folding
- [ ] Loop optimizations

### Distribuição
- [ ] Binário único (moonc)
- [ ] Static linking CUDA Runtime
- [ ] Testes multiplataforma
- [ ] Documentação

---

## 🎯 Resultado Final

### Antes (Depende de Tudo)

```bash
# Precisa Python
python moonc.py programa.gpu -o app

# Precisa nvcc
nvcc programa.cu -o app

# Executar
./app
```

### Depois (100% Independente)

```bash
# Só precisa moonc (um binário)
./moonc programa.gpu -o app

# Ou gerar PTX diretamente
./moonc programa.gpu -S -o programa.ptx

# Executar (carrega PTX na GPU)
./app
```

**O binário `moonc`:**
- ✅ Não precisa Python
- ✅ Não precisa nvcc
- ✅ Não precisa g++
- ✅ Gera PTX diretamente
- ✅ Carrega na GPU via CUDA Runtime
- ✅ Um binário único

---

## ⏱️ Estimativas

| Fase | Tempo | Dependências |
|------|-------|--------------|
| Fase 1.1: Completar Parser C++ | 2-3 semanas | Nenhuma |
| Fase 1.2: PTX Generator | 3-4 semanas | Nenhuma |
| Fase 1.3: CUDA Runtime | 1-2 semanas | CUDA Runtime (libcudart) |
| Fase 2: Compilador Completo | 2-3 semanas | CUDA Runtime |
| Fase 3: Runtime Standalone | 1 semana | CUDA Runtime (static) |
| **TOTAL** | **9-13 semanas** | **Apenas CUDA Runtime** |

---

## 🔄 Alternativa: Backend Próprio (Mais Trabalho)

Se quiser **ZERO dependências** (nem CUDA Runtime):

**Opção:** Implementar driver NVIDIA diretamente
- ❌ Muito complexo (6-12 meses)
- ❌ Precisa reverse engineering
- ❌ Não recomendado

**Recomendação:** Use CUDA Runtime. É a única dependência e é necessária para GPU NVIDIA.

---

## 📚 Referências

- **PTX ISA**: https://docs.nvidia.com/cuda/parallel-thread-execution/
- **CUDA Runtime API**: https://docs.nvidia.com/cuda/cuda-runtime-api/
- **CUDA Driver API**: https://docs.nvidia.com/cuda/cuda-driver-api/
- **PTX Examples**: https://github.com/NVIDIA/cuda-samples

---

## ✅ Próximos Passos Imediatos

1. **Completar parser C++** (moonc_cpp)
2. **Criar PTX generator básico**
3. **Testar com kernel simples**
4. **Integrar CUDA Runtime**

---

**Última atualização:** 2025-01-XX  
**Status:** Parser 50% completo, PTX generator não iniciado

