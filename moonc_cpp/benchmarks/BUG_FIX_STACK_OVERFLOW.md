# Correção do Bug Crítico de Stack Overflow

## Data
2025-01-XX

## Problema Identificado

O parser estava causando stack overflow (exit code `0xC00000FD`) em **todos** os programas MoonLight, mesmo os mais simples como `x = 1`.

### Sintomas
- Stack overflow em qualquer arquivo `.gpu`
- Ocorria durante a fase de parsing
- Acontecia mesmo com arquivos mínimos (apenas um statement)

### Causa Raiz

O problema estava em `parseStatement()` e `parseProgram()`:

1. **Recursão Infinita em `parseStatement()`**: Quando o parser chegava ao token EOF, `parseStatement()` não tratava esse caso corretamente. Ele tentava chamar `parseExpressionStatement()`, que por sua vez chamava `parseExpression()`, criando uma cadeia recursiva infinita.

2. **Loop Infinito em `parseProgram()`**: O loop `while (!isAtEnd())` calculava `isAtEnd()` apenas uma vez antes do loop, não a cada iteração. Quando `parseStatement()` retornava `nullptr` (indicando EOF), o loop continuava indefinidamente porque `at_end` não era recalculado.

## Solução Implementada

### 1. Correção em `parseStatement()`

Adicionada verificação para EOF antes de tentar parsear uma expressão:

```cpp
// If we're at EOF, return nullptr to signal end of parsing
if (isAtEnd() || currentToken().type == TokenType::EOF_TOKEN) {
    exitRecursion();
    logDebug("END (EOF)", "parseStatement");
    return nullptr;
}
```

### 2. Correção em `parseProgram()`

Modificado o loop para:
- Verificar `isAtEnd()` a cada iteração
- Parar quando `parseStatement()` retorna `nullptr`

```cpp
while (!isAtEnd()) {
    // ...
    auto stmt = parseStatement();
    if (stmt) {
        program->statements.push_back(stmt);
        statement_count++;
    } else {
        // parseStatement() returned nullptr, which means we're at EOF
        logDebug("parseStatement() returned nullptr (EOF), breaking loop", "parseProgram");
        break;
    }
}
```

### 3. Melhorias Adicionais

- **Logs de Debug**: Adicionados logs extensivos para identificar problemas futuros
- **Limites de Segurança**: Implementados limites de recursão (1000) e loops (10000) para prevenir stack overflow
- **Validação em `isAtEnd()` e `currentToken()`**: Adicionadas verificações de bounds para evitar acesso inválido a `tokens_`

## Arquivos Modificados

- `moonc_cpp/src/parser/parser.cpp`
  - `parseProgram()`: Corrigido loop para verificar `isAtEnd()` a cada iteração
  - `parseStatement()`: Adicionada verificação de EOF antes de chamar `parseExpressionStatement()`
  - `isAtEnd()`: Melhorada validação de bounds
  - `currentToken()`: Adicionada proteção contra acesso inválido
  - Adicionados métodos de debug e limites de segurança

- `moonc_cpp/include/moonlight/parser.h`
  - Adicionados membros para debug e limites de segurança
  - Adicionados métodos: `logDebug()`, `checkRecursionLimit()`, `checkLoopLimit()`, `enterRecursion()`, `exitRecursion()`

- `moonc_cpp/src/main.cpp`
  - Modificado para passar flag `verbose` ao construtor do `Parser`

## Testes Realizados

### Testes Mínimos
- ✅ `test0.gpu` (`x = 1`)
- ✅ `test1.gpu` (`print("teste")`)
- ✅ `test2.gpu` (`def main()`)
- ✅ `test3.gpu` (array assignment)

### Testes de Execução
- ✅ `test0.gpu` executa sem stack overflow
- ✅ Compilação e execução funcionam corretamente

### Benchmarks Originais
- ✅ `saxpy.gpu` - parseado com sucesso
- ✅ `reduction.gpu` - parseado com sucesso
- ✅ `gemm.gpu` - parseado com sucesso

## Resultado

✅ **Bug corrigido com sucesso!** O parser agora funciona corretamente para todos os programas testados, sem stack overflow.

## Prevenção Futura

1. **Limites de Segurança**: Os limites de recursão e loops previnem stack overflow mesmo se houver bugs futuros
2. **Logs de Debug**: O flag `-v` permite identificar problemas rapidamente
3. **Validação de Bounds**: Todas as funções que acessam `tokens_` agora verificam bounds antes de acessar

## Notas

- Os logs de debug podem ser mantidos para facilitar debugging futuro
- Os limites de segurança devem ser mantidos como proteção contra bugs futuros
- A verificação de EOF em `parseStatement()` é crítica e não deve ser removida

