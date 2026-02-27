# Análise de Conflitos do Parser MoonLight

## Resumo

- **Total de regras**: 105 funções de produção
- **Regras com múltiplas produções**:
  - `statement`: 91 produções (maior fonte de conflitos)
  - `expression`: 80 produções
  - `class_statement`: 5 produções
  - `tuple_elements`: 4 produções

## Conflitos Conhecidos

### Shift/Reduce Conflicts (203)
Causados principalmente por:
1. **Ambiguidade em `statement`**: Muitas formas diferentes de statements podem começar com os mesmos tokens
2. **Ambiguidade em `expression`**: Expressões podem ser interpretadas de múltiplas formas
3. **Falta de precedência explícita**: Alguns operadores não têm precedência definida

### Reduce/Reduce Conflicts (49)
Causados principalmente por:
1. **Regras duplicadas**: Algumas regras podem ser reduzidas de múltiplas formas
2. **Conflito entre `statement` e `expression`**: Alguns constructs podem ser ambos

## Regras Problemáticas Identificadas

### 1. `p_statement_func_def` vs `p_statement_cuda_kernel`
- **Problema**: Regra `AT PROFILE DEF IDENTIFIER...` aparece em ambos (linha 239 de `p_statement_cuda_kernel`)
- **Causa**: `@profile def function()` é uma função normal, não um kernel CUDA
- **Solução**: Remover de `p_statement_cuda_kernel`, manter apenas em `p_statement_func_def`

### 2. `p_expression_func_call` vs `p_statement_func_call`
- **Problema**: Mesmas produções em ambos (ex: `IDENTIFIER LPAREN argument_list RPAREN`)
- **Causa**: Chamadas de função podem ser statements ou expressions
- **Solução**: Usar precedência ou contexto adicional para desambiguar

### 3. `p_class_statement` inclui `statement`
- **Problema**: `class_statement : statement` (linha 197) permite qualquer statement dentro de classes
- **Causa**: Pode causar ambiguidade com `DEF IDENTIFIER...` (método vs função)
- **Solução**: Especificar regras de método explicitamente antes da regra genérica

### 4. Múltiplas formas de `statement`
- 91 produções diferentes
- Muitas começam com os mesmos tokens
- Precisa de precedência explícita

## Priorização

### Alta Prioridade
1. Resolver conflitos entre `func_def` e `cuda_kernel`
2. Resolver ambiguidade entre `statement` e `expression` para function calls
3. Adicionar precedência para operadores que faltam

### Média Prioridade
4. Unificar regras duplicadas em `statement`
5. Simplificar regras de `expression`
6. Adicionar contexto para desambiguar

### Baixa Prioridade
7. Otimizar regras menos usadas
8. Documentar decisões de parsing

## Próximos Passos

1. Revisar e refatorar regras de `statement`
2. Adicionar precedência explícita
3. Unificar regras redundantes
4. Testar com todos os exemplos após cada mudança

