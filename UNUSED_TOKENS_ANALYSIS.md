# Análise de Tokens Não Utilizados

## Tokens Identificados como Não Utilizados (24 tokens)

Baseado nos warnings do parser:

1. **ARROW** - `->` operator
2. **CONNECT** - Connection operator
3. **ELIF** - `elif` keyword
4. **ELLIPSIS** - `...` operator
5. **ENTER** - `enter` keyword (context manager)
6. **EXIT** - `exit` keyword (context manager)
7. **FILTER** - `filter` function
8. **GENERATOR** - `generator` keyword
9. **GLOBAL** - `global` keyword
10. **HOST** - `host` keyword (CUDA)
11. **LOCK** - `lock` keyword
12. **MAP** - `map` function
13. **METACLASS** - `metaclass` keyword
14. **NUMBA** - `numba` keyword
15. **QUESTION** - `?` operator
16. **REDUCE** - `reduce` function
17. **SELF** - `self` keyword
18. **SUPER** - `super` keyword
19. **SYNC** - `sync` keyword
20. **WARP_REDUCE_MAX** - Warp primitive
21. **WARP_REDUCE_MIN** - Warp primitive
22. **WARP_REDUCE_SUM** - Warp primitive
23. **WARP_SHUFFLE** - Warp primitive
24. **WITH** - `with` keyword

## Decisão por Token

### Tokens para Features Futuras (MANTER)
- **ELIF**: Pode ser usado no futuro para `elif` statements
- **WITH**: Context managers podem ser implementados
- **ENTER/EXIT**: Parte de context managers
- **GENERATOR**: Generators podem ser expandidos
- **METACLASS**: Metaclasses podem ser implementadas
- **SELF/SUPER**: POO pode ser expandida
- **WARP_REDUCE_***, **WARP_SHUFFLE**: Warp primitives podem ser implementadas
- **GLOBAL**: Pode ser usado para variáveis globais
- **HOST**: Pode ser usado em contexto CUDA

### Tokens Obsoletos/Incompletos (REMOVER ou IMPLEMENTAR)
- **ARROW**: `->` não é usado na sintaxe atual
- **CONNECT**: Não definido na especificação
- **ELLIPSIS**: `...` não é usado
- **FILTER/MAP/REDUCE**: Funções funcionais não implementadas
- **LOCK/SYNC**: Threading não totalmente implementado
- **NUMBA**: Compatibilidade com Numba não implementada
- **QUESTION**: `?` operator não usado

## Recomendação

### Fase 1: Remover Tokens Obviamente Não Usados
- ARROW, CONNECT, ELLIPSIS, QUESTION, NUMBA

### Fase 2: Documentar Tokens para Features Futuras
- ELIF, WITH, ENTER/EXIT, GENERATOR, METACLASS, SELF/SUPER
- WARP_REDUCE_*, WARP_SHUFFLE, GLOBAL, HOST

### Fase 3: Implementar ou Remover Tokens Parcialmente Implementados
- FILTER/MAP/REDUCE: Implementar ou remover
- LOCK/SYNC: Implementar threading ou remover

