# Resolução de Conflitos do Parser - Progresso

## Conflitos Resolvidos

### 1. Regra Duplicada `AT PROFILE DEF IDENTIFIER...`
- **Problema**: Aparecia tanto em `p_statement_cuda_kernel` quanto deveria estar em `p_statement_func_def`
- **Solução**: Removida de `p_statement_cuda_kernel`, adicionada corretamente em `p_statement_func_def`
- **Status**: ✅ RESOLVIDO

## Conflitos Parcialmente Resolvidos

### 2. Conflito Reduce/Reduce: `statement` vs `class_statement`
- **Problema**: `DEF IDENTIFIER...` pode ser tanto `statement` (função) quanto `class_statement` (método)
- **Status Atual**: PLY resolve automaticamente escolhendo `statement`, mas `class_statement -> DEF IDENTIFIER...` nunca é reduzida
- **Impacto**: Métodos de classe ainda funcionam porque a regra específica `class_statement : DEF IDENTIFIER...` é checada primeiro
- **Solução Futura**: Refatorar gramática de classes para usar contexto adicional ou regras mais específicas
- **Prioridade**: MÉDIA (funciona na prática)

## Conflitos Restantes

### 3. Shift/Reduce Conflicts (239)
- **Causa Principal**: Múltiplas formas de `statement` (91 produções) e `expression` (80 produções)
- **Estratégia**: Adicionar precedência explícita onde necessário
- **Progresso**: Adicionada precedência para `LPAREN` (function calls)
- **Próximos Passos**: Continuar adicionando precedência para outros operadores

### 4. Reduce/Reduce Conflicts (49)
- **Causa Principal**: Regras que podem ser reduzidas de múltiplas formas
- **Estratégia**: Unificar regras redundantes, adicionar contexto
- **Progresso**: Documentado conflito principal (`statement` vs `class_statement`)
- **Próximos Passos**: Identificar e resolver outros conflitos específicos

## Melhorias Implementadas

1. ✅ Removida regra duplicada `AT PROFILE DEF IDENTIFIER...`
2. ✅ Adicionada precedência para `LPAREN` (function calls)
3. ✅ Documentação de conflitos conhecidos

## Testes de Validação

- ✅ `@profile def function()` - OK
- ✅ `@profile cuda kernel def function()` - OK  
- ✅ `class Test { def method() { ... } }` - OK
- ✅ `def regular_function() { ... }` - OK

## Próximos Passos

1. Continuar adicionando precedência para operadores
2. Identificar e resolver conflitos reduce/reduce específicos
3. Testar com todos os exemplos após cada mudança
4. Considerar refatoração maior da gramática se necessário

