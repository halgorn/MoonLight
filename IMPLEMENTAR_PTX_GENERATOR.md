# Implementação: Gerador PTX Direto

## Objetivo

Gerar **PTX (Parallel Thread Execution)** diretamente da AST MoonLight, sem passar por CUDA C++ ou nvcc.

---

## Por Que PTX?

1. ✅ **Formato texto** - fácil de gerar
2. ✅ **Carregamento direto** - via CUDA Runtime API
3. ✅ **Sem nvcc** - não precisa compilador externo
4. ✅ **Compilação instantânea** - PTX é carregado direto na GPU
5. ✅ **Portabilidade** - PTX é compilado pelo driver para qualquer GPU NVIDIA

---

## Estrutura PTX

### Exemplo Básico

```ptx
.version 7.0              // Versão PTX
.target sm_75              // Compute capability (RTX 20xx, 30xx)
.address_size 64          // 64-bit addresses

.entry add_vectors(        // Entry point (kernel)
    .param .u64 a,         // Parâmetros
    .param .u64 b,
    .param .u64 c,
    .param .u32 n
) {
    // Registradores
    .reg .u32 %tid;        // Thread ID
    .reg .u64 %ra, %rb, %rc;  // Endereços
    .reg .f32 %fa, %fb, %fc;  // Valores float
    
    // Código
    mov.u32 %tid, %tid.x;  // threadIdx.x
    ld.param.u64 %ra, [a]; // Carregar parâmetro
    ld.param.u64 %rb, [b];
    ld.param.u64 %rc, [c];
    
    // Calcular índice
    mul.wide.u32 %ra, %tid, 4;  // tid * sizeof(float)
    add.u64 %ra, %ra, %ra;      // a + offset
    add.u64 %rb, %rb, %ra;      // b + offset
    add.u64 %rc, %rc, %ra;      // c + offset
    
    // Operação
    ld.global.f32 %fa, [%ra];   // Carregar a[i]
    ld.global.f32 %fb, [%rb];   // Carregar b[i]
    add.f32 %fc, %fa, %fb;      // c[i] = a[i] + b[i]
    st.global.f32 [%rc], %fc;   // Salvar c[i]
    
    ret;                         // Retornar
}
```

---

## Implementação em C++

### 1. Classe PTXGenerator

```cpp
// moonc_cpp/src/codegen/ptx_generator.h
#pragma once

#include "../ast/ast_node.h"
#include <string>
#include <vector>
#include <map>

namespace moonlight {
namespace codegen {

class PTXGenerator {
private:
    int register_counter;
    int label_counter;
    std::map<std::string, std::string> variable_regs;
    
    // Target configuration
    std::string ptx_version = "7.0";
    std::string compute_capability = "sm_75";  // RTX 20xx, 30xx
    
public:
    PTXGenerator();
    
    // Main generation function
    std::string generatePTX(ASTProgram* program);
    
    // Kernel generation
    std::string generateKernel(ASTKernel* kernel);
    
    // Expression generation
    std::string generateExpression(ASTNode* expr);
    std::string generateStatement(ASTNode* stmt);
    
    // Register management
    std::string allocateRegister(const std::string& type);
    std::string allocateLabel();
    
    // Built-in variables
    std::string generateBuiltinVar(const std::string& name);
    
    // Memory operations
    std::string generateLoad(const std::string& addr, const std::string& type);
    std::string generateStore(const std::string& addr, const std::string& value, const std::string& type);
    
    // Arithmetic operations
    std::string generateAdd(const std::string& a, const std::string& b, const std::string& type);
    std::string generateSub(const std::string& a, const std::string& b, const std::string& type);
    std::string generateMul(const std::string& a, const std::string& b, const std::string& type);
    std::string generateDiv(const std::string& a, const std::string& b, const std::string& type);
    
    // Control flow
    std::string generateIf(ASTIf* if_node);
    std::string generateWhile(ASTWhile* while_node);
    std::string generateFor(ASTFor* for_node);
};

} // namespace codegen
} // namespace moonlight
```

### 2. Implementação Básica

```cpp
// moonc_cpp/src/codegen/ptx_generator.cpp
#include "ptx_generator.h"
#include "../ast/ast_node.h"
#include <sstream>
#include <iomanip>

namespace moonlight {
namespace codegen {

PTXGenerator::PTXGenerator() 
    : register_counter(0), label_counter(0) {
}

std::string PTXGenerator::generatePTX(ASTProgram* program) {
    std::ostringstream ptx;
    
    // Header
    ptx << ".version " << ptx_version << "\n";
    ptx << ".target " << compute_capability << "\n";
    ptx << ".address_size 64\n\n";
    
    // Generate kernels
    for (auto kernel : program->kernels) {
        ptx << generateKernel(kernel) << "\n";
    }
    
    return ptx.str();
}

std::string PTXGenerator::generateKernel(ASTKernel* kernel) {
    std::ostringstream ptx;
    register_counter = 0;
    variable_regs.clear();
    
    // Kernel signature
    ptx << ".entry " << kernel->name << "(";
    
    // Parameters
    std::vector<std::string> params;
    for (auto param : kernel->params) {
        std::string ptx_type = mapTypeToPTX(param.type);
        params.push_back(".param ." + ptx_type + " " + param.name);
    }
    ptx << join(params, ", ") << ") {\n";
    
    // Body
    ptx << "    // Kernel body\n";
    for (auto stmt : kernel->body) {
        ptx << "    " << generateStatement(stmt) << "\n";
    }
    
    ptx << "    ret;\n";
    ptx << "}\n";
    
    return ptx.str();
}

std::string PTXGenerator::generateStatement(ASTNode* stmt) {
    if (stmt->type == AST_ASSIGN) {
        return generateAssign(static_cast<ASTAssign*>(stmt));
    } else if (stmt->type == AST_IF) {
        return generateIf(static_cast<ASTIf*>(stmt));
    } else if (stmt->type == AST_WHILE) {
        return generateWhile(static_cast<ASTWhile*>(stmt));
    } else if (stmt->type == AST_FOR) {
        return generateFor(static_cast<ASTFor*>(stmt));
    }
    return "";
}

std::string PTXGenerator::generateExpression(ASTNode* expr) {
    if (expr->type == AST_BINARY_OP) {
        auto binop = static_cast<ASTBinaryOp*>(expr);
        std::string left = generateExpression(binop->left);
        std::string right = generateExpression(binop->right);
        std::string type = inferType(binop->left);
        
        if (binop->op == "+") {
            return generateAdd(left, right, type);
        } else if (binop->op == "-") {
            return generateSub(left, right, type);
        } else if (binop->op == "*") {
            return generateMul(left, right, type);
        } else if (binop->op == "/") {
            return generateDiv(left, right, type);
        }
    } else if (expr->type == AST_VAR) {
        auto var = static_cast<ASTVar*>(expr);
        return variable_regs[var->name];
    } else if (expr->type == AST_CONST) {
        auto const_val = static_cast<ASTConst*>(expr);
        return generateConstant(const_val);
    } else if (expr->type == AST_BUILTIN) {
        auto builtin = static_cast<ASTBuiltin*>(expr);
        return generateBuiltinVar(builtin->name);
    }
    
    return "";
}

std::string PTXGenerator::generateBuiltinVar(const std::string& name) {
    if (name == "threadIdx.x") {
        return "%tid.x";
    } else if (name == "threadIdx.y") {
        return "%tid.y";
    } else if (name == "blockIdx.x") {
        return "%ctaid.x";
    } else if (name == "blockDim.x") {
        return "%ntid.x";
    }
    // ... outros built-ins
    return "";
}

std::string PTXGenerator::generateAdd(const std::string& a, const std::string& b, const std::string& type) {
    std::string result = allocateRegister(type);
    std::ostringstream ptx;
    ptx << "add." << type << " " << result << ", " << a << ", " << b << ";";
    return result;  // Retorna registrador resultante
}

// ... outras operações

} // namespace codegen
} // namespace moonlight
```

---

## Exemplo: MoonLight → PTX

### Código MoonLight

```moonlight
cuda kernel def add_vectors(a, b, c, n) {
    i = threadIdx.x + blockIdx.x * blockDim.x
    if (i < n) {
        c[i] = a[i] + b[i]
    }
}
```

### PTX Gerado

```ptx
.version 7.0
.target sm_75
.address_size 64

.entry add_vectors(
    .param .u64 a,
    .param .u64 b,
    .param .u64 c,
    .param .u32 n
) {
    .reg .u32 %tid;
    .reg .u32 %bid;
    .reg .u32 %bdim;
    .reg .u32 %i;
    .reg .u64 %ra, %rb, %rc;
    .reg .f32 %fa, %fb, %fc;
    .reg .pred %p;
    
    // i = threadIdx.x + blockIdx.x * blockDim.x
    mov.u32 %tid, %tid.x;
    mov.u32 %bid, %ctaid.x;
    mov.u32 %bdim, %ntid.x;
    mul.u32 %i, %bid, %bdim;
    add.u32 %i, %tid, %i;
    
    // if (i < n)
    ld.param.u32 %n, [n];
    setp.lt.u32 %p, %i, %n;
    @%p bra L1;
    ret;
    
L1:
    // c[i] = a[i] + b[i]
    ld.param.u64 %ra, [a];
    ld.param.u64 %rb, [b];
    ld.param.u64 %rc, [c];
    
    mul.wide.u32 %ra, %i, 4;
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

---

## Carregar PTX na GPU

```cpp
// moonc_cpp/src/runtime/cuda_loader.cpp
#include <cuda.h>
#include <cuda_runtime.h>
#include <fstream>
#include <string>

CUmodule loadPTXFile(const std::string& filename) {
    // Ler arquivo PTX
    std::ifstream file(filename);
    std::string ptx((std::istreambuf_iterator<char>(file)),
                     std::istreambuf_iterator<char>());
    
    // Carregar PTX
    CUmodule module;
    CUresult result = cuModuleLoadData(&module, ptx.c_str());
    
    if (result != CUDA_SUCCESS) {
        const char* error_str;
        cuGetErrorString(result, &error_str);
        throw std::runtime_error("Failed to load PTX: " + std::string(error_str));
    }
    
    return module;
}

void launchKernel(CUmodule module, const std::string& kernel_name,
                  int blocks, int threads, void** args) {
    CUfunction func;
    cuModuleGetFunction(&func, module, kernel_name.c_str());
    
    cuLaunchKernel(func,
                  blocks, 1, 1,      // gridDim
                  threads, 1, 1,    // blockDim
                  0,                 // sharedMemBytes
                  NULL,              // stream
                  args,              // kernel params
                  NULL);             // extra options
}
```

---

## Próximos Passos

1. ✅ Criar estrutura `ptx_generator.h/cpp`
2. ✅ Implementar geração básica (aritmética)
3. ✅ Implementar memória (global, shared)
4. ✅ Implementar control flow (if, while, for)
5. ✅ Testar com kernel simples
6. ✅ Integrar CUDA Runtime loader

---

**Última atualização:** 2025-01-XX  
**Status:** Não iniciado - pronto para implementar





