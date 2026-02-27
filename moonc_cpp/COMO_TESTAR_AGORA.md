# 🚀 Como Testar - Guia Rápido

## Teste Básico (Verificar Sintaxe)

```powershell
cd moonc_cpp
.\build\Release\moonc.exe -c test_vector_add.gpu -v
```

**O que faz:** Apenas verifica se a sintaxe está correta, sem executar.

---

## Teste Completo (Compilar + Executar)

```powershell
cd moonc_cpp
.\build\Release\moonc.exe -r test_vector_add.gpu -v
```

**O que faz:**
1. Compila o código MoonLight
2. Gera PTX
3. Carrega na GPU
4. Executa o programa completo

---

## Teste Apenas PTX (Gerar Assembly)

```powershell
cd moonc_cpp
.\build\Release\moonc.exe test_vector_add.gpu -S -o test.ptx -v
```

**O que faz:** Gera apenas o arquivo PTX (assembly CUDA) sem executar.

**Para ver o PTX gerado:**
```powershell
type test.ptx
```

---

## Teste com Script Automático

```powershell
cd moonc_cpp
.\EXECUTAR_TESTE.ps1
```

**O que faz:** Executa todos os testes automaticamente e mostra tempos.

---

## Teste de Performance (Benchmark)

```powershell
cd moonc_cpp
.\benchmark.ps1
```

**O que faz:** Executa múltiplas vezes e mostra estatísticas de performance.

---

## Teste com Outros Exemplos

```powershell
# Vector Add (já testado)
.\build\Release\moonc.exe -r test_vector_add.gpu -v

# Exemplo do repositório (se existir)
.\build\Release\moonc.exe -r ..\examples\cuda\vector_add.gpu -v
```

---

## 🔍 Verificar se Está Funcionando

### 1. Verificar Versão
```powershell
.\build\Release\moonc.exe --version
```

**Deve mostrar:**
```
MoonLight Compiler v2.0.0
CUDA support: enabled
```

### 2. Verificar Sintaxe
```powershell
.\build\Release\moonc.exe -c test_vector_add.gpu
```

**Se funcionar:** Nenhum erro = sintaxe OK ✅

### 3. Verificar PTX
```powershell
.\build\Release\moonc.exe test_vector_add.gpu -S -o test.ptx
type test.ptx
```

**Deve mostrar:** Código PTX assembly

---

## ⚠️ Troubleshooting

### Se travar no "Parsing..."
- Pode estar processando (normal para arquivos grandes)
- Aguarde alguns segundos
- Se demorar muito (>30s), pode haver erro no parser

### Se der erro de CUDA
- Verifique: `nvidia-smi` (deve mostrar GPU)
- Verifique driver CUDA instalado

### Se não encontrar arquivo
- Certifique-se de estar em `moonc_cpp/`
- Verifique se `test_vector_add.gpu` existe

---

## 📊 O que Esperar

### Saída Esperada (Sucesso):
```
Reading file: test_vector_add.gpu
Compiling test_vector_add.gpu...
Lexing completed: 215 tokens
Parsing completed: X statements
Generating PTX...
PTX generated (XXX bytes)
Loading PTX on GPU...
[SUCCESS] PTX loaded on GPU successfully
Executing program...
Teste concluído!
h_c[0] = 0.0
h_c[999999] = 2999997.0
[SUCCESS] Program executed successfully
```

---

## 🎯 Teste Mais Simples

Crie um arquivo `test_simple.gpu`:
```moonlight
def main() {
    print("Hello, MoonLight!")
    x = 10
    y = 20
    print("x + y =", x + y)
}

main()
```

Teste:
```powershell
.\build\Release\moonc.exe -r test_simple.gpu -v
```

---

**Pronto para testar! 🚀**

