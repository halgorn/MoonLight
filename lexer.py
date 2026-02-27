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
    # CUDA/GPU
    'cuda': 'CUDA', 'kernel': 'KERNEL', 'device': 'DEVICE', 
    'gpu': 'GPU', 'host': 'HOST', 'shared': 'SHARED',
    'global': 'GLOBAL', 'free': 'FREE',
    'persistent': 'PERSISTENT', 'gpu_resident': 'GPU_RESIDENT',
    'syncthreads': 'SYNCTHREADS', 'syncwarp': 'SYNCWARP',
    # Warp primitives
    'warp_reduce_sum': 'WARP_REDUCE_SUM', 'warp_reduce_max': 'WARP_REDUCE_MAX',
    'warp_reduce_min': 'WARP_REDUCE_MIN', 'warp_shuffle': 'WARP_SHUFFLE',
    'lane_id': 'LANE_ID', 'warp_id': 'WARP_ID',
    # CUDA Built-in Variables
    'threadIdx_x': 'THREADIDX_X', 'threadIdx_y': 'THREADIDX_Y', 'threadIdx_z': 'THREADIDX_Z',
    'blockIdx_x': 'BLOCKIDX_X', 'blockIdx_y': 'BLOCKIDX_Y', 'blockIdx_z': 'BLOCKIDX_Z',
    'blockDim_x': 'BLOCKDIM_X', 'blockDim_y': 'BLOCKDIM_Y', 'blockDim_z': 'BLOCKDIM_Z',
    'gridDim_x': 'GRIDDIM_X', 'gridDim_y': 'GRIDDIM_Y', 'gridDim_z': 'GRIDDIM_Z',
    # Atomic operations
    'atomic_add': 'ATOMIC_ADD', 'atomic_sub': 'ATOMIC_SUB',
    'atomic_min': 'ATOMIC_MIN', 'atomic_max': 'ATOMIC_MAX',
    'atomic_cas': 'ATOMIC_CAS', 'atomic_exch': 'ATOMIC_EXCH',
    # Work Queue
    'gpu_queue': 'GPU_QUEUE', 'enqueue_host': 'ENQUEUE_HOST',
    'dequeue_host': 'DEQUEUE_HOST', 'dequeue_wait': 'DEQUEUE_WAIT',
    'enqueue': 'ENQUEUE',
    # Device-side allocation
    'device_malloc': 'DEVICE_MALLOC', 'device_free': 'DEVICE_FREE',
    # Unified and pinned memory
    'unified': 'UNIFIED', 'pinned': 'PINNED', 'memory': 'MEMORY',
    # Pipeline
    'pipeline': 'PIPELINE', 'stage': 'STAGE', 'connect': 'CONNECT',
    # CUDA Streams
    'cuda_stream': 'CUDA_STREAM', 'sync_stream': 'SYNC_STREAM',
    'cuda_graph_begin': 'CUDA_GRAPH_BEGIN', 'cuda_graph_end': 'CUDA_GRAPH_END',
    'cuda_graph_launch': 'CUDA_GRAPH_LAUNCH',
    # Multi-GPU
    'enable_p2p': 'ENABLE_P2P', 'p2p_copy': 'P2P_COPY',
    # Profiling & Debugging
    'gpu_printf': 'GPU_PRINTF', 'gpu_breakpoint': 'GPU_BREAKPOINT', 'profile': 'PROFILE',
    # Control Flow
    'predict_taken': 'PREDICT_TAKEN',
    # Optimization
    'optimize': 'OPTIMIZE', 'hints': 'HINTS',
    # JIT Compilation
    'jit': 'JIT',
    # THREADING
    'thread': 'THREAD', 'lock': 'LOCK', 'sync': 'SYNC',
    # JIT/PERFORMANCE
    'jit': 'JIT', 'compile': 'COMPILE',
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
    'QUESTION',
    # ESPECIAIS
    'AT', 'ARROW', 'DOUBLESTAR', 'ELLIPSIS',
    'BITWISEAND', 'BITWISEOR', 'BITWISEXOR', 'BITWISENOT',
    'LEFTSHIFT', 'RIGHTSHIFT',
    # CUDA ESPECÍFICOS
    'LARROW'  # <- for memory transfers
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

def t_LARROW(t):
    r'<-'
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
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
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

t_ignore = ' \t\n'

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

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    # Não retorna token, apenas atualiza número de linha

def t_error(t):
    print(f"Erro léxico: Caractere inválido '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()