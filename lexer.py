import ply.lex as lex

# Palavras reservadas COMPLETAS
reserved = {
    'if': 'IF', 'else': 'ELSE', 'elif': 'ELIF',
    'for': 'FOR', 'while': 'WHILE', 'print': 'PRINT',
    'def': 'DEF', 'return': 'RETURN', 'lambda': 'LAMBDA',
    'map': 'MAP', 'filter': 'FILTER', 'reduce': 'REDUCE',
    'True': 'TRUE', 'False': 'FALSE', 'None': 'NONE',
    'and': 'AND', 'or': 'OR', 'not': 'NOT',
    'in': 'IN', 'is': 'IS',
    # FUNÇÕES BUILT-IN
    'len': 'LEN', 'range': 'RANGE', 'sum': 'SUM',
    'max': 'MAX', 'min': 'MIN', 'type': 'TYPE',
    'str': 'STR', 'int': 'INT', 'float': 'FLOAT',
    'list': 'LIST', 'dict': 'DICT', 'set': 'SET',
    'tuple': 'TUPLE', 'bool': 'BOOL',
    # CONTROLE DE LOOP
    'break': 'BREAK', 'continue': 'CONTINUE',
    # POO E METACLASSES
    'class': 'CLASS', 'self': 'SELF', 'super': 'SUPER',
    'metaclass': 'METACLASS', 'property': 'PROPERTY',
    'staticmethod': 'STATICMETHOD', 'classmethod': 'CLASSMETHOD',
    # EXCEÇÕES
    'try': 'TRY', 'except': 'EXCEPT', 'finally': 'FINALLY',
    'raise': 'RAISE', 'assert': 'ASSERT',
    # MÓDULOS E PACKAGES
    'import': 'IMPORT', 'from': 'FROM', 'as': 'AS',
    'package': 'PACKAGE', 'module': 'MODULE',
    # GERADORES E ASYNC
    'yield': 'YIELD', 'async': 'ASYNC', 'await': 'AWAIT',
    'generator': 'GENERATOR',
    # CONTEXT MANAGERS
    'with': 'WITH', 'enter': 'ENTER', 'exit': 'EXIT',
    # THREADING
    'thread': 'THREAD', 'lock': 'LOCK', 'sync': 'SYNC',
    # CUDA/GPU
    'cuda': 'CUDA', 'kernel': 'KERNEL', 'gpu': 'GPU',
    'device': 'DEVICE', 'global': 'GLOBAL', 'shared': 'SHARED',
    # JIT/PERFORMANCE
    'jit': 'JIT', 'numba': 'NUMBA', 'compile': 'COMPILE',
    'inline': 'INLINE', 'optimize': 'OPTIMIZE'
}

tokens = (
    'IDENTIFIER', 'NUMBER', 'STRING', 'ASSIGN',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO', 'POWER',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'GT', 'LT', 'EQ', 'NEQ', 'SEMICOLON', 'COMMA',
    'LBRACKET', 'RBRACKET', 'DOT', 'COLON',
    # OPERADORES AVANÇADOS
    'PLUSEQ', 'MINUSEQ', 'MULTEQ', 'DIVEQ', 'MODEQ', 'POWEQ',
    'PLUSPLUS', 'MINUSMINUS', 'LE', 'GE',
    'QUESTION', 'NEWLINE',
    # ESPECIAIS
    'AT', 'ARROW', 'DOUBLESTAR', 'ELLIPSIS',
    'BITWISEAND', 'BITWISEOR', 'BITWISEXOR', 'BITWISENOT',
    'LEFTSHIFT', 'RIGHTSHIFT'
) + tuple(reserved.values())

# OPERADORES COMPOSTOS PRIMEIRO (ordem importante para evitar conflitos)
def t_POWEQ(t):
    r'\*\*='
    return t

def t_DOUBLESTAR(t):
    r'\*\*'
    return t

def t_PLUSEQ(t):
    r'\+='
    return t

def t_MINUSEQ(t):
    r'-='
    return t

def t_MULTEQ(t):
    r'\*='
    return t

def t_DIVEQ(t):
    r'/='
    return t

def t_MODEQ(t):
    r'%='
    return t

def t_PLUSPLUS(t):
    r'\+\+'
    return t

def t_MINUSMINUS(t):
    r'--'
    return t

def t_LEFTSHIFT(t):
    r'<<'
    return t

def t_RIGHTSHIFT(t):
    r'>>'
    return t

def t_LE(t):
    r'<='
    return t

def t_GE(t):
    r'>='
    return t

def t_EQ(t):
    r'=='
    return t

def t_NEQ(t):
    r'!='
    return t

def t_ARROW(t):
    r'->'
    return t

def t_ELLIPSIS(t):
    r'\.\.\.'
    return t

# OPERADORES SIMPLES
t_ASSIGN = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_GT = r'>'
t_LT = r'<'
t_LPAREN = r'$'
t_RPAREN = r'$'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'$$'
t_RBRACKET = r'$$'
t_DOT = r'\.'
t_COMMA = r','
t_SEMICOLON = r';'
t_COLON = r':'
t_QUESTION = r'\?'
t_AT = r'@'

# Operadores bitwise
t_BITWISEAND = r'&'
t_BITWISEOR = r'\|'
t_BITWISEXOR = r'\^'
t_BITWISENOT = r'~'

t_ignore = ' \t'

def t_COMMENT(t):
    r'\#.*'
    pass

def t_STRING(t):
    r'\"([^\\\n"]|(\\.))*\"|\'([^\\\n\']|(\\.))*\'|\"\"\".*?\"\"\"|\'\'\'.*?\'\'\''
    # Remove aspas
    if t.value.startswith('"""') or t.value.startswith("'''"):
        t.value = t.value[3:-3]
    else:
        t.value = t.value[1:-1]
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?([eE][+-]?\d+)?[jJ]?'
    # Suporte a números complexos, científicos
    if 'j' in t.value or 'J' in t.value:
        # Para números complexos, vamos simplificar
        t.value = complex(t.value.replace('j', 'j').replace('J', 'j'))
    elif '.' in t.value or 'e' in t.value or 'E' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

def t_error(t):
    print(f"Erro léxico: Caractere inválido '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()