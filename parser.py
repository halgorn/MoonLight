import ply.yacc as yacc
from lexer import tokens

precedence = (
    ('right', 'QUESTION', 'COLON'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('left', 'IN', 'IS'),
    ('left', 'EQ', 'NEQ', 'GT', 'LT', 'GE', 'LE'),
    ('left', 'BITWISEOR'),
    ('left', 'BITWISEXOR'), 
    ('left', 'BITWISEAND'),
    ('left', 'LEFTSHIFT', 'RIGHTSHIFT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE', 'MODULO'),
    ('right', 'POWER', 'DOUBLESTAR'),
    ('right', 'PLUSPLUS', 'MINUSMINUS', 'BITWISENOT'),
    ('left', 'DOT'),
    ('left', 'LBRACKET'),
    ('left', 'LPAREN'),  # Function calls have higher precedence
    ('left', 'AT'),
)

def p_program_multiple(p):
    '''program : program statement'''
    p[0] = p[1] + [p[2]]

def p_program_single(p):
    '''program : statement'''
    p[0] = [p[1]]

def p_program_empty(p):
    '''program : empty'''
    p[0] = []

def p_statement_assign(p):
    '''statement : IDENTIFIER ASSIGN expression
                 | identifier_list ASSIGN expression
                 | IDENTIFIER ASSIGN IDENTIFIER ASSIGN expression
                 | IDENTIFIER ASSIGN IDENTIFIER ASSIGN IDENTIFIER ASSIGN expression'''
    if len(p) == 4:
        # Verifica se é unpacking
        if isinstance(p[1], list):
            p[0] = ('unpack', p[1], p[3])
        else:
            p[0] = ('assign', p[1], p[3])
    elif len(p) == 6:
        # Multiple assignment: x = y = z
        p[0] = ('multi_assign', [p[1], p[3]], p[5])
    else:
        # Multiple assignment: i = j = k = expr (3 variables)
        p[0] = ('multi_assign', [p[1], p[3], p[5]], p[7])

def p_identifier_list(p):
    '''identifier_list : IDENTIFIER COMMA IDENTIFIER
                       | identifier_list COMMA IDENTIFIER'''
    if len(p) == 4:
        if isinstance(p[1], list):
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1], p[3]]

def p_statement_list_assign(p):
    '''statement : IDENTIFIER LBRACKET expression RBRACKET ASSIGN expression'''
    p[0] = ('list_assign', p[1], p[3], p[6])

def p_statement_attr_assign(p):
    '''statement : IDENTIFIER DOT IDENTIFIER ASSIGN expression
                 | SELF DOT IDENTIFIER ASSIGN expression'''
    # Allow self.attr = expr for class methods (SELF is reserved, parses as same structure)
    obj = 'self' if (getattr(p[1], 'type', None) == 'SELF' or p[1] in ('self', 'SELF')) else p[1]
    p[0] = ('attr_assign', obj, p[3], p[5])

def p_statement_compound_assign(p):
    '''statement : IDENTIFIER PLUSEQ expression
                 | IDENTIFIER MINUSEQ expression
                 | IDENTIFIER MULTEQ expression
                 | IDENTIFIER DIVEQ expression
                 | IDENTIFIER MODEQ expression
                 | IDENTIFIER POWEQ expression'''
    p[0] = ('compound_assign', p[1], p[2], p[3])

def p_statement_increment(p):
    '''statement : IDENTIFIER PLUSPLUS
                 | IDENTIFIER MINUSMINUS
                 | PLUSPLUS IDENTIFIER
                 | MINUSMINUS IDENTIFIER'''
    if p[2] in ['++', '--']:
        p[0] = ('post_increment', p[1], p[2])
    else:
        p[0] = ('pre_increment', p[2], p[1])

# DECORADORES SIMPLIFICADOS
def p_statement_decorated_func(p):
    '''statement : AT IDENTIFIER DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE'''
    p[0] = ('decorated_func_def', [('decorator', p[2], [])], p[4], p[6], p[9])

def p_statement_if(p):
    '''statement : IF LPAREN expression RPAREN LBRACE program RBRACE
                 | IF LPAREN expression RPAREN LBRACE program RBRACE ELSE LBRACE program RBRACE'''
    if len(p) == 8:
        p[0] = ('if', p[3], p[6])
    else:
        p[0] = ('if-else', p[3], p[6], p[10])

def p_statement_while(p):
    '''statement : WHILE LPAREN expression RPAREN LBRACE program RBRACE'''
    p[0] = ('while', p[3], p[6])

def p_statement_for(p):
    '''statement : FOR LPAREN statement SEMICOLON expression SEMICOLON statement RPAREN LBRACE program RBRACE'''
    p[0] = ('for', p[3], p[5], p[7], p[10])

def p_statement_print(p):
    '''statement : PRINT LPAREN argument_list RPAREN'''
    p[0] = ('print', p[3])

def p_statement_func_call(p):
    '''statement : IDENTIFIER LPAREN argument_list RPAREN
                 | SYNC_STREAM LPAREN argument_list RPAREN
                 | CUDA_GRAPH_BEGIN LPAREN argument_list RPAREN
                 | CUDA_GRAPH_END LPAREN argument_list RPAREN
                 | CUDA_GRAPH_LAUNCH LPAREN argument_list RPAREN
                 | ENABLE_P2P LPAREN argument_list RPAREN
                 | P2P_COPY LPAREN argument_list RPAREN'''
    # Function call as statement (e.g., main(), sync_stream(stream))
    # Map token types to function names
    func_name_map = {
        'SYNC_STREAM': 'sync_stream',
        'CUDA_GRAPH_BEGIN': 'cuda_graph_begin',
        'CUDA_GRAPH_END': 'cuda_graph_end',
        'CUDA_GRAPH_LAUNCH': 'cuda_graph_launch',
        'ENABLE_P2P': 'enable_p2p',
        'P2P_COPY': 'p2p_copy',
    }
    
    if p[1] in func_name_map:
        func_name = func_name_map[p[1]]
    else:
        func_name = p[1]
    
    p[0] = ('func_call_stmt', func_name, p[3] if p[3] else [])

def p_statement_func_def(p):
    '''statement : DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                 | AT JIT DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                 | AT JIT LPAREN argument_list RPAREN DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                 | AT PROFILE DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE'''
    if len(p) == 9:
        # Regular function: DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
        # p[1]=DEF, p[2]=IDENTIFIER, p[3]=LPAREN, p[4]=parameter_list, p[5]=RPAREN, p[6]=LBRACE, p[7]=program, p[8]=RBRACE
        p[0] = ('func_def', p[2], p[4], p[7], [])
    elif len(p) == 11 and (getattr(p[2], 'type', p[2]) == 'JIT' or p[2] == 'JIT' or p[2] == 'jit'):
        # @jit def name(...) { ... }; len=11: p[1]=AT, p[2]=JIT, p[3]=DEF, p[4]=IDENTIFIER, p[5]=LPAREN, p[6]=parameter_list, p[7]=RPAREN, p[8]=LBRACE, p[9]=program, p[10]=RBRACE
        p[0] = ('func_def', p[4], p[6], p[9], [('decorator', 'jit', [])])
    elif len(p) == 11 and (getattr(p[2], 'type', p[2]) == 'PROFILE' or p[2] == 'PROFILE'):
        # @profile def name(...) { ... }
        p[0] = ('func_def', p[4], p[6], p[9], [('decorator', 'profile', [])])
    elif len(p) == 14 and (getattr(p[2], 'type', p[2]) == 'JIT' or p[2] == 'JIT' or p[2] == 'jit'):
        # @jit(...) def name(...) { ... }; len=14
        jit_args = p[4] if p[4] else []
        p[0] = ('func_def', p[7], p[9], p[12], [('decorator', 'jit', jit_args)])
    else:
        # Fallback
        p[0] = ('func_def', p[2] if len(p) > 2 else 'unknown', [], [], [])

def p_statement_yield(p):
    '''statement : YIELD expression
                 | YIELD'''
    if len(p) == 3:
        p[0] = ('yield', p[2])
    else:
        p[0] = ('yield', None)

def p_statement_class_def(p):
    '''statement : CLASS IDENTIFIER LBRACE class_body RBRACE
                 | CLASS IDENTIFIER LPAREN IDENTIFIER RPAREN LBRACE class_body RBRACE
                 | CLASS IDENTIFIER LPAREN inheritance_list RPAREN LBRACE class_body RBRACE'''
    if len(p) == 6:
        p[0] = ('class_def', p[2], None, p[4])
    elif len(p) == 9 and isinstance(p[4], str):
        p[0] = ('class_def', p[2], [p[4]], p[7])
    elif len(p) == 9:
        p[0] = ('class_def', p[2], p[4], p[7])

def p_inheritance_list(p):
    '''inheritance_list : IDENTIFIER
                        | inheritance_list COMMA IDENTIFIER'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_class_body(p):
    '''class_body : class_body class_statement
                  | class_statement
                  | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_class_statement(p):
    '''class_statement : DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                       | PROPERTY DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                       | STATICMETHOD DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                       | CLASSMETHOD DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                       | statement'''
    if len(p) == 9:
        p[0] = ('method_def', p[2], p[4], p[7])
    elif len(p) == 10:
        if p[1] == 'property':
            p[0] = ('property_def', p[3], p[5], p[8])
        elif p[1] == 'staticmethod':
            p[0] = ('staticmethod_def', p[3], p[5], p[8])
        elif p[1] == 'classmethod':
            p[0] = ('classmethod_def', p[3], p[5], p[8])
    else:
        p[0] = p[1]

def p_statement_method_call(p):
    '''statement : IDENTIFIER DOT IDENTIFIER LPAREN argument_list RPAREN'''
    p[0] = ('method_call', p[1], p[3], p[5])

def p_statement_break(p):
    '''statement : BREAK'''
    p[0] = ('break',)

def p_statement_continue(p):
    '''statement : CONTINUE'''
    p[0] = ('continue',)

def p_statement_async_def(p):
    '''statement : ASYNC DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE'''
    p[0] = ('async_func_def', p[3], p[5], p[8])

def p_statement_await(p):
    '''statement : AWAIT expression'''
    p[0] = ('await', p[2])

def p_statement_thread(p):
    '''statement : THREAD IDENTIFIER LPAREN argument_list RPAREN'''
    p[0] = ('thread', p[2], p[4])

def p_statement_with(p):
    '''statement : WITH expression AS IDENTIFIER LBRACE program RBRACE'''
    # with expr as var { block } - context manager: bind var = expr, run block, var removed from scope after
    p[0] = ('with', p[2], p[4], p[6])

def p_statement_cuda_kernel(p):
    '''statement : CUDA KERNEL DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                 | AT IDENTIFIER CUDA KERNEL DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                 | AT PREDICT_TAKEN CUDA KERNEL DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                 | AT PROFILE CUDA KERNEL DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                 | AT OPTIMIZE LPAREN NUMBER RPAREN CUDA KERNEL DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                 | AT HINTS LPAREN RPAREN CUDA KERNEL DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE'''
    # PLY uses 1-based indexing, and p[0] is the result
    # For regular kernel: p[1]=CUDA, p[2]=KERNEL, p[3]=DEF, p[4]=IDENTIFIER, p[5]=LPAREN, p[6]=parameter_list, p[7]=RPAREN, p[8]=LBRACE, p[9]=program, p[10]=RBRACE
    # For decorated: p[1]=AT, p[2]=IDENTIFIER(decorator), p[3]=CUDA, p[4]=KERNEL, p[5]=DEF, p[6]=IDENTIFIER(name), p[7]=LPAREN, p[8]=parameter_list, p[9]=RPAREN, p[10]=LBRACE, p[11]=program, p[12]=RBRACE
    if len(p) == 11:  # Regular kernel: 10 tokens + p[0] = 11 total
        # Regular cuda kernel
        p[0] = ('cuda_kernel', p[4], p[6], p[9], False, [])  # False = not persistent, no decorators
    elif len(p) == 13:  # Decorated kernel with IDENTIFIER decorator
        # Decorated cuda kernel: @decorator cuda kernel def name(...) { ... }
        decorator_name = p[2]
        p[0] = ('cuda_kernel', p[6], p[8], p[11], False, [('decorator', decorator_name, [])])
    elif len(p) == 14 and p[2] == 'PREDICT_TAKEN':  # @predict_taken
        # @predict_taken cuda kernel def name(...) { ... }
        # p[1]=AT, p[2]=PREDICT_TAKEN, p[3]=CUDA, p[4]=KERNEL, p[5]=DEF, p[6]=IDENTIFIER(name), p[7]=LPAREN, p[8]=parameter_list, p[9]=RPAREN, p[10]=LBRACE, p[11]=program, p[12]=RBRACE
        p[0] = ('cuda_kernel', p[6], p[8], p[11], False, [('decorator', 'predict_taken', [])])
    elif len(p) == 14 and p[2] == 'PROFILE':  # @profile cuda kernel
        # @profile cuda kernel def name(...) { ... }
        # p[1]=AT, p[2]=PROFILE, p[3]=CUDA, p[4]=KERNEL, p[5]=DEF, p[6]=IDENTIFIER(name), p[7]=LPAREN, p[8]=parameter_list, p[9]=RPAREN, p[10]=LBRACE, p[11]=program, p[12]=RBRACE
        p[0] = ('cuda_kernel', p[6], p[8], p[11], False, [('decorator', 'profile', [])])
    elif len(p) == 11 and p[1] == 'AT' and p[2] == 'PROFILE':  # @profile def function
        # @profile def name(...) { ... }
        # p[1]=AT, p[2]=PROFILE, p[3]=DEF, p[4]=IDENTIFIER(name), p[5]=LPAREN, p[6]=parameter_list, p[7]=RPAREN, p[8]=LBRACE, p[9]=program, p[10]=RBRACE
        p[0] = ('func_def', p[4], p[6], p[9], [('decorator', 'profile', [])])
    elif len(p) == 16 and p[2] == 'OPTIMIZE':  # @optimize(level=N) cuda kernel
        # @optimize(level=N) cuda kernel def name(...) { ... }
        # p[1]=AT, p[2]=OPTIMIZE, p[3]=LPAREN, p[4]=NUMBER(level), p[5]=RPAREN, p[6]=CUDA, p[7]=KERNEL, p[8]=DEF, p[9]=IDENTIFIER(name), p[10]=LPAREN, p[11]=parameter_list, p[12]=RPAREN, p[13]=LBRACE, p[14]=program, p[15]=RBRACE
        level = p[4]
        p[0] = ('cuda_kernel', p[9], p[11], p[14], False, [('decorator', 'optimize', [level])])
    elif len(p) == 15 and p[2] == 'HINTS':  # @hints() cuda kernel
        # @hints() cuda kernel def name(...) { ... }
        # p[1]=AT, p[2]=HINTS, p[3]=LPAREN, p[4]=RPAREN, p[5]=CUDA, p[6]=KERNEL, p[7]=DEF, p[8]=IDENTIFIER(name), p[9]=LPAREN, p[10]=parameter_list, p[11]=RPAREN, p[12]=LBRACE, p[13]=program, p[14]=RBRACE
        p[0] = ('cuda_kernel', p[8], p[10], p[13], False, [('decorator', 'hints', [])])

def p_statement_cuda_persistent_kernel(p):
    '''statement : CUDA PERSISTENT KERNEL DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                 | AT IDENTIFIER CUDA PERSISTENT KERNEL DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE'''
    if len(p) == 11:
        # Regular persistent kernel: CUDA PERSISTENT KERNEL DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
        # p[1]=CUDA, p[2]=PERSISTENT, p[3]=KERNEL, p[4]=DEF, p[5]=IDENTIFIER, p[6]=LPAREN, p[7]=parameter_list, p[8]=RPAREN, p[9]=LBRACE, p[10]=program, p[11]=RBRACE
        p[0] = ('cuda_kernel', p[5], p[7], p[10], True, [])  # True = persistent, no decorators
    elif len(p) == 13:
        # Decorated persistent kernel: @decorator cuda persistent kernel def name(...) { ... }
        # p[1]=AT, p[2]=IDENTIFIER(decorator), p[3]=CUDA, p[4]=PERSISTENT, p[5]=KERNEL, p[6]=DEF, p[7]=IDENTIFIER(name), p[8]=LPAREN, p[9]=parameter_list, p[10]=RPAREN, p[11]=LBRACE, p[12]=program, p[13]=RBRACE
        decorator_name = p[2]
        p[0] = ('cuda_kernel', p[7], p[9], p[12], True, [('decorator', decorator_name, [])])
    else:
        # Fallback - should not happen
        p[0] = ('cuda_kernel', p[5] if len(p) > 5 else 'unknown', [], [], True, [])

def p_statement_gpu_launch_1d(p):
    '''statement : GPU LBRACKET expression COMMA expression RBRACKET IDENTIFIER LPAREN argument_list RPAREN
                 | GPU LBRACKET expression COMMA expression RBRACKET KERNEL LPAREN argument_list RPAREN
                 | GPU LBRACKET expression COMMA expression COMMA IDENTIFIER ASSIGN expression RBRACKET IDENTIFIER LPAREN argument_list RPAREN
                 | GPU LBRACKET expression COMMA expression COMMA IDENTIFIER ASSIGN expression RBRACKET KERNEL LPAREN argument_list RPAREN'''
    # Determine if it's a regular launch or with stream
    if len(p) == 10:
        # Regular launch: gpu[blocks, threads] kernel(args) or gpu[blocks, threads] identifier(args)
        kernel_name = p[6] if p[6] != 'kernel' else 'kernel'  # Handle KERNEL token
        p[0] = ('gpu_launch', p[3], p[5], kernel_name, p[8], '1d', None)
    elif len(p) == 15:
        # Launch with stream: gpu[blocks, threads, stream=stream_var] kernel(args)
        # p[1]=GPU, p[2]=LBRACKET, p[3]=expression(blocks), p[4]=COMMA, p[5]=expression(threads), p[6]=COMMA, p[7]=IDENTIFIER(stream), p[8]=ASSIGN, p[9]=expression(stream_var), p[10]=RBRACKET, p[11]=IDENTIFIER/KERNEL(kernel), p[12]=LPAREN, p[13]=argument_list, p[14]=RPAREN
        kernel_name = p[11] if p[11] != 'kernel' else 'kernel'  # Handle KERNEL token
        p[0] = ('gpu_launch', p[3], p[5], kernel_name, p[13], '1d', p[9])

def p_statement_gpu_launch_2d(p):
    '''statement : GPU LBRACKET LPAREN expression COMMA expression RPAREN COMMA LPAREN expression COMMA expression RPAREN RBRACKET IDENTIFIER LPAREN argument_list RPAREN
                 | GPU LBRACKET LPAREN expression COMMA expression RPAREN COMMA LPAREN expression COMMA expression RPAREN COMMA IDENTIFIER ASSIGN expression RBRACKET IDENTIFIER LPAREN argument_list RPAREN'''
    if len(p) == 19:
        # Regular 2D launch: gpu[(bx, by), (tx, ty)] kernel(args) — 18 RHS symbols
        p[0] = ('gpu_launch_2d', (p[4], p[6]), (p[10], p[12]), p[15], p[17], None)
    else:
        # 2D launch with stream: gpu[(bx, by), (tx, ty), stream=stream_var] kernel(args) — 22 RHS symbols
        # p[1]=GPU, p[2]=LBRACKET, ..., p[19]=IDENTIFIER(kernel), p[20]=LPAREN, p[21]=argument_list, p[22]=RPAREN
        p[0] = ('gpu_launch_2d', (p[4], p[6]), (p[10], p[12]), p[19], p[21], p[17])

def p_statement_gpu_launch_device_select(p):
    '''statement : GPU LBRACKET NUMBER RBRACKET LBRACKET expression COMMA expression RBRACKET IDENTIFIER LPAREN argument_list RPAREN'''
    # gpu[device_id][blocks, threads] kernel(args) for multi-GPU
    p[0] = ('gpu_launch_device', p[3], p[6], p[8], p[10], p[12])

def p_statement_jit_func(p):
    '''statement : JIT DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE
                 | COMPILE DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE'''
    p[0] = ('jit_func_def', p[3], p[5], p[8])

def p_statement_inline_func(p):
    '''statement : INLINE DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE'''
    p[0] = ('inline_func_def', p[3], p[5], p[8])

def p_statement_package(p):
    '''statement : PACKAGE IDENTIFIER LBRACE program RBRACE'''
    p[0] = ('package_def', p[2], p[4])

def p_statement_module(p):
    '''statement : MODULE IDENTIFIER LBRACE program RBRACE'''
    p[0] = ('module_def', p[2], p[4])

def p_statement_try(p):
    '''statement : TRY LBRACE program RBRACE except_clauses
                 | TRY LBRACE program RBRACE except_clauses FINALLY LBRACE program RBRACE'''
    if len(p) == 6:
        p[0] = ('try', p[3], p[5], None)
    else:
        p[0] = ('try', p[3], p[5], p[8])

def p_except_clauses(p):
    '''except_clauses : except_clauses except_clause
                      | except_clause'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_except_clause(p):
    '''except_clause : EXCEPT LBRACE program RBRACE
                     | EXCEPT IDENTIFIER LBRACE program RBRACE'''
    if len(p) == 5:
        p[0] = ('except', None, p[3])
    else:
        p[0] = ('except', p[2], p[4])

def p_statement_raise(p):
    '''statement : RAISE expression
                 | RAISE'''
    if len(p) == 3:
        p[0] = ('raise', p[2])
    else:
        p[0] = ('raise', None)

def p_statement_assert(p):
    '''statement : ASSERT expression
                 | ASSERT expression COMMA expression'''
    if len(p) == 3:
        p[0] = ('assert', p[2], None)
    else:
        p[0] = ('assert', p[2], p[4])

def p_statement_import(p):
    '''statement : IMPORT IDENTIFIER
                 | IMPORT IDENTIFIER AS IDENTIFIER
                 | FROM IDENTIFIER IMPORT IDENTIFIER
                 | FROM IDENTIFIER IMPORT IDENTIFIER AS IDENTIFIER
                 | FROM IDENTIFIER IMPORT MULTIPLY'''
    if len(p) == 3:
        p[0] = ('import', p[2], None)
    elif len(p) == 5 and p[1] == 'import':
        p[0] = ('import', p[2], p[4])
    elif len(p) == 5:
        if p[4] == '*':
            p[0] = ('from_import_all', p[2])
        else:
            p[0] = ('from_import', p[2], p[4], None)
    else:
        p[0] = ('from_import', p[2], p[4], p[6])

def p_parameter_list(p):
    '''parameter_list : IDENTIFIER
                      | parameter_list COMMA IDENTIFIER
                      | empty'''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_statement_return(p):
    '''statement : RETURN expression
                 | RETURN'''
    if len(p) == 3:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', None)

# EXPRESSIONS
def p_expression_lambda(p):
    '''expression : LAMBDA LPAREN parameter_list RPAREN expression'''
    p[0] = ('lambda', p[3], p[5])

def p_expression_func_call(p):
    '''expression : IDENTIFIER LPAREN argument_list RPAREN
                  | CUDA_STREAM LPAREN argument_list RPAREN
                  | SYNC_STREAM LPAREN argument_list RPAREN
                  | CUDA_GRAPH_BEGIN LPAREN argument_list RPAREN
                  | CUDA_GRAPH_END LPAREN argument_list RPAREN
                  | CUDA_GRAPH_LAUNCH LPAREN argument_list RPAREN
                  | ENABLE_P2P LPAREN argument_list RPAREN
                  | P2P_COPY LPAREN argument_list RPAREN'''
    # Map token types to function names
    func_name_map = {
        'CUDA_STREAM': 'cuda_stream',
        'SYNC_STREAM': 'sync_stream',
        'CUDA_GRAPH_BEGIN': 'cuda_graph_begin',
        'CUDA_GRAPH_END': 'cuda_graph_end',
        'CUDA_GRAPH_LAUNCH': 'cuda_graph_launch',
        'ENABLE_P2P': 'enable_p2p',
        'P2P_COPY': 'p2p_copy',
    }
    
    # Get function name (either from IDENTIFIER or mapped from token)
    if p[1] in func_name_map:
        func_name = func_name_map[p[1]]
    else:
        func_name = p[1]
    
    # Reconhece funções built-in
    builtin_funcs = ['len', 'sum', 'max', 'min', 'type', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'range',
                     'warp_reduce_sum', 'warp_reduce_max', 'warp_reduce_min', 'warp_shuffle',
                     'cuda_stream', 'sync_stream', 'cuda_graph_begin', 'cuda_graph_end', 'cuda_graph_launch',
                     'enable_p2p', 'p2p_copy', 'gpu_printf', 'gpu_breakpoint']
    if func_name in builtin_funcs and (p[3] is None or len(p[3]) == 0):
        # Functions with no arguments
        if func_name in ['cuda_stream', 'cuda_graph_begin', 'cuda_graph_end']:
            p[0] = (func_name,)
        else:
            p[0] = (func_name,)
    elif func_name in builtin_funcs and p[3] and len(p[3]) == 1:
        p[0] = (func_name, p[3][0])
    elif func_name == 'warp_shuffle' and p[3] and len(p[3]) == 2:
        # warp_shuffle(value, src_lane)
        p[0] = ('warp_shuffle', p[3][0], p[3][1])
    elif func_name in ['warp_reduce_sum', 'warp_reduce_max', 'warp_reduce_min'] and p[3] and len(p[3]) == 1:
        # warp_reduce_sum(value), warp_reduce_max(value), warp_reduce_min(value)
        p[0] = (func_name, p[3][0])
    elif func_name == 'sync_stream' and p[3] and len(p[3]) == 1:
        # sync_stream(stream)
        p[0] = ('sync_stream', p[3][0])
    elif func_name == 'cuda_graph_launch' and p[3] and len(p[3]) == 1:
        # cuda_graph_launch(graph_exec)
        p[0] = ('cuda_graph_launch', p[3][0])
    elif func_name == 'enable_p2p' and p[3] and len(p[3]) == 2:
        # enable_p2p(gpu0, gpu1)
        p[0] = ('enable_p2p', p[3][0], p[3][1])
    elif func_name == 'p2p_copy' and p[3] and len(p[3]) == 3:
        # p2p_copy(dest, src, size)
        p[0] = ('p2p_copy', p[3][0], p[3][1], p[3][2])
    elif func_name == 'enable_p2p' and p[3] and len(p[3]) == 2:
        # enable_p2p(gpu0, gpu1)
        p[0] = ('enable_p2p', p[3][0], p[3][1])
    elif func_name == 'range':
        if len(p[3]) == 1:
            p[0] = ('range', p[3][0])
        elif len(p[3]) == 2:
            p[0] = ('range', p[3][0], p[3][1])
        elif len(p[3]) == 3:
            p[0] = ('range', p[3][0], p[3][1], p[3][2])
        else:
            p[0] = ('range', p[3][0], p[3][1], p[3][2], p[3][3])
    else:
        # Regular function call
        p[0] = ('func_call', func_name, p[3])

def p_expression_method_call(p):
    '''expression : IDENTIFIER DOT IDENTIFIER LPAREN argument_list RPAREN'''
    p[0] = ('method_call', p[1], p[3], p[5])

def p_expression_attr_access(p):
    '''expression : IDENTIFIER DOT IDENTIFIER
                  | SELF DOT IDENTIFIER'''
    obj = 'self' if (getattr(p[1], 'type', None) == 'SELF' or p[1] in ('self', 'SELF')) else p[1]
    p[0] = ('attr_access', obj, p[3])

def p_expression_list_index(p):
    '''expression : IDENTIFIER LBRACKET expression RBRACKET'''
    p[0] = ('list_index', p[1], p[3])

# CUDA MEMORY OPERATIONS
def p_expression_device_alloc(p):
    '''expression : DEVICE LBRACKET expression RBRACKET'''
    # device[size] - allocate on GPU
    p[0] = ('device_alloc', p[3])

def p_expression_shared_alloc(p):
    '''expression : SHARED LBRACKET expression RBRACKET'''
    # shared[size] - shared memory in kernel
    p[0] = ('shared_alloc', p[3])

def p_statement_memory_transfer_to_device(p):
    '''statement : IDENTIFIER LARROW IDENTIFIER'''
    # d_array <- h_array (host to device)
    p[0] = ('mem_transfer_h2d', p[1], p[3])

# Removed: duplicate rule for IDENTIFIER LARROW IDENTIFIER
# Memory transfer direction is now handled by p_statement_memory_transfer_to_device

def p_statement_cuda_free(p):
    '''statement : FREE LPAREN IDENTIFIER RPAREN'''
    # free(d_array)
    p[0] = ('cuda_free', p[3])

def p_statement_gpu_resident_alloc(p):
    '''statement : GPU_RESIDENT IDENTIFIER ASSIGN DEVICE LBRACKET expression RBRACKET'''
    # gpu_resident d_array = device[size]
    # Allocates on GPU and persists across function calls
    p[0] = ('gpu_resident_alloc', p[2], p[6])

def p_statement_gpu_device_alloc(p):
    '''statement : GPU LBRACKET expression RBRACKET IDENTIFIER ASSIGN DEVICE LBRACKET expression RBRACKET'''
    # gpu[device_id] var = device[size] - allocate on specific GPU
    p[0] = ('gpu_device_alloc', p[3], p[5], p[9])

def p_expression_device_malloc(p):
    '''expression : DEVICE_MALLOC LPAREN expression RPAREN'''
    # device_malloc(size) - allocate memory on GPU from within kernel
    p[0] = ('device_malloc', p[3])

def p_statement_device_free(p):
    '''statement : DEVICE_FREE LPAREN expression RPAREN'''
    # device_free(ptr) - free memory allocated on GPU
    p[0] = ('device_free', p[3])

def p_statement_unified_memory(p):
    '''statement : IDENTIFIER ASSIGN UNIFIED MEMORY LBRACKET expression RBRACKET'''
    # unified_data = unified memory[size]
    # Unified memory accessible from both CPU and GPU
    p[0] = ('unified_memory_alloc', p[1], p[6])

def p_statement_pinned_memory(p):
    '''statement : IDENTIFIER ASSIGN PINNED MEMORY LBRACKET expression RBRACKET'''
    # pinned_data = pinned memory[size]
    # Pinned (page-locked) memory for fast transfers
    p[0] = ('pinned_memory_alloc', p[1], p[6])

def p_statement_syncthreads(p):
    '''statement : SYNCTHREADS LPAREN RPAREN'''
    p[0] = ('syncthreads',)

def p_statement_syncwarp(p):
    '''statement : SYNCWARP LPAREN RPAREN'''
    p[0] = ('syncwarp',)

def p_statement_gpu_printf(p):
    '''statement : GPU_PRINTF LPAREN argument_list RPAREN'''
    # gpu_printf(format, args...) - GPU-side printf
    p[0] = ('gpu_printf', p[3])

def p_statement_gpu_breakpoint(p):
    '''statement : GPU_BREAKPOINT LPAREN RPAREN'''
    # gpu_breakpoint() - GPU-side breakpoint
    p[0] = ('gpu_breakpoint',)

# Warp primitives as call expressions (lane_id(), warp_id(), warp_reduce_sum(x), warp_shuffle(x,y))
def p_expression_lane_id_call(p):
    '''expression : LANE_ID LPAREN RPAREN'''
    p[0] = ('cuda_builtin', '__laneid()')

def p_expression_warp_id_call(p):
    '''expression : WARP_ID LPAREN RPAREN'''
    p[0] = ('cuda_builtin', '(threadIdx.x / 32)')

def p_expression_warp_reduce_shuffle_call(p):
    '''expression : WARP_REDUCE_SUM LPAREN argument_list RPAREN
                  | WARP_REDUCE_MAX LPAREN argument_list RPAREN
                  | WARP_REDUCE_MIN LPAREN argument_list RPAREN
                  | WARP_SHUFFLE LPAREN argument_list RPAREN'''
    func_name = p[1]  # token value: 'warp_reduce_sum', 'warp_shuffle', etc.
    args = p[3] if p[3] is not None else []
    if func_name == 'warp_shuffle':
        if args is None or len(args) != 2:
            raise SyntaxError("warp_shuffle requires exactly 2 arguments")
        p[0] = ('warp_shuffle', args[0], args[1])
    else:
        if args is None or len(args) != 1:
            raise SyntaxError(f"{func_name} requires exactly 1 argument")
        p[0] = (func_name, args[0])

# CUDA Built-in Variables as expressions
def p_expression_cuda_builtin(p):
    '''expression : THREADIDX_X
                  | THREADIDX_Y
                  | THREADIDX_Z
                  | BLOCKIDX_X
                  | BLOCKIDX_Y
                  | BLOCKIDX_Z
                  | BLOCKDIM_X
                  | BLOCKDIM_Y
                  | BLOCKDIM_Z
                  | GRIDDIM_X
                  | GRIDDIM_Y
                  | GRIDDIM_Z
                  | LANE_ID
                  | WARP_ID'''
    # Map to CUDA built-in variables
    cuda_var_map = {
        'threadIdx_x': 'threadIdx.x',
        'threadIdx_y': 'threadIdx.y',
        'threadIdx_z': 'threadIdx.z',
        'blockIdx_x': 'blockIdx.x',
        'blockIdx_y': 'blockIdx.y',
        'blockIdx_z': 'blockIdx.z',
        'blockDim_x': 'blockDim.x',
        'blockDim_y': 'blockDim.y',
        'blockDim_z': 'blockDim.z',
        'gridDim_x': 'gridDim.x',
        'gridDim_y': 'gridDim.y',
        'gridDim_z': 'gridDim.z',
        'lane_id': '__laneid()',  # CUDA intrinsic
        'warp_id': '(threadIdx.x / 32)'  # Warp ID calculation
    }
    p[0] = ('cuda_builtin', cuda_var_map.get(p[1], p[1]))

# Atomic operations
def p_expression_atomic_add(p):
    '''expression : ATOMIC_ADD LPAREN expression COMMA expression RPAREN'''
    p[0] = ('atomic_add', p[3], p[5])

def p_expression_atomic_sub(p):
    '''expression : ATOMIC_SUB LPAREN expression COMMA expression RPAREN'''
    p[0] = ('atomic_sub', p[3], p[5])

def p_expression_atomic_min(p):
    '''expression : ATOMIC_MIN LPAREN expression COMMA expression RPAREN'''
    p[0] = ('atomic_min', p[3], p[5])

def p_expression_atomic_max(p):
    '''expression : ATOMIC_MAX LPAREN expression COMMA expression RPAREN'''
    p[0] = ('atomic_max', p[3], p[5])

def p_expression_atomic_cas(p):
    '''expression : ATOMIC_CAS LPAREN expression COMMA expression COMMA expression RPAREN'''
    p[0] = ('atomic_cas', p[3], p[5], p[7])

def p_expression_atomic_exch(p):
    '''expression : ATOMIC_EXCH LPAREN expression COMMA expression RPAREN'''
    p[0] = ('atomic_exch', p[3], p[5])

# Work Queue operations
def p_statement_queue_declaration(p):
    '''statement : IDENTIFIER ASSIGN GPU_QUEUE LBRACKET IDENTIFIER COMMA expression RBRACKET'''
    # queue_name = gpu_queue[Type, capacity]
    p[0] = ('gpu_queue_decl', p[1], p[5], p[7])

def p_statement_enqueue_host(p):
    '''statement : ENQUEUE_HOST LPAREN IDENTIFIER COMMA expression RPAREN'''
    p[0] = ('enqueue_host', p[3], p[5])

def p_statement_dequeue_host(p):
    '''statement : IDENTIFIER ASSIGN DEQUEUE_HOST LPAREN IDENTIFIER RPAREN'''
    p[0] = ('dequeue_host', p[1], p[5])

def p_expression_dequeue_wait(p):
    '''expression : DEQUEUE_WAIT LPAREN IDENTIFIER RPAREN'''
    p[0] = ('dequeue_wait', p[3])

def p_statement_enqueue(p):
    '''statement : ENQUEUE LPAREN IDENTIFIER COMMA argument_list RPAREN'''
    # enqueue(queue, arg1, arg2, ...)
    queue = p[3]
    if p[5] is None:
        args = []
    elif isinstance(p[5], list):
        args = p[5]
    else:
        args = [p[5]]
    p[0] = ('enqueue', queue, args)

# Pipeline operations
def p_statement_pipeline_def(p):
    '''statement : PIPELINE IDENTIFIER LBRACE pipeline_stages RBRACE'''
    # pipeline name { stages }
    p[0] = ('pipeline_def', p[2], p[4])

def p_pipeline_stages(p):
    '''pipeline_stages : pipeline_stages pipeline_stage
                       | pipeline_stage'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_pipeline_stage(p):
    '''pipeline_stage : STAGE IDENTIFIER COLON IDENTIFIER LPAREN stage_params RPAREN'''
    # stage name: kernel_func(params)
    p[0] = ('pipeline_stage', p[2], p[4], p[6])

def p_stage_params(p):
    '''stage_params : IDENTIFIER ASSIGN expression
                    | stage_params COMMA IDENTIFIER ASSIGN expression
                    | empty'''
    if len(p) == 2:
        p[0] = {}
    elif len(p) == 4:
        p[0] = {p[1]: p[3]}
    else:
        p[0] = p[1]
        p[0][p[3]] = p[5]

# Removed: duplicate rule for IDENTIFIER DOT IDENTIFIER LPAREN argument_list RPAREN
# Pipeline start/stop is now handled by p_statement_method_call (line 167)

def p_expression_slice(p):
    '''expression : IDENTIFIER LBRACKET expression COLON expression RBRACKET
                  | IDENTIFIER LBRACKET expression COLON expression COLON expression RBRACKET'''
    if len(p) == 7:
        p[0] = ('slice', p[1], p[3], p[5], None)
    else:
        p[0] = ('slice', p[1], p[3], p[5], p[7])

def p_expression_list(p):
    '''expression : LBRACKET list_elements RBRACKET'''
    p[0] = ('list', p[2])

def p_expression_dict(p):
    '''expression : LBRACE dict_elements RBRACE'''
    p[0] = ('dict', p[2])

def p_expression_tuple(p):
    '''expression : LPAREN tuple_elements RPAREN'''
    p[0] = ('tuple', p[2])

def p_list_elements(p):
    '''list_elements : expression
                     | list_elements COMMA expression
                     | empty'''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_dict_elements(p):
    '''dict_elements : dict_pair
                     | dict_elements COMMA dict_pair
                     | empty'''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_dict_pair(p):
    '''dict_pair : expression COLON expression'''
    p[0] = (p[1], p[3])

def p_tuple_elements(p):
    '''tuple_elements : expression COMMA
                      | expression COMMA expression
                      | tuple_elements COMMA expression
                      | empty'''
    if len(p) == 2:
        p[0] = []
    elif len(p) == 3:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = [p[1], p[3]]
    else:
        p[0] = p[1] + [p[3]]

def p_argument_list(p):
    '''argument_list : expression
                     | argument_list COMMA expression
                     | empty'''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_expression_logical_binary(p):
    '''expression : expression AND expression
                  | expression OR expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_logical_not(p):
    '''expression : NOT expression'''
    p[0] = ('not', p[2])

# Operador ternário temporariamente desabilitado devido a conflito com if/else statements
# TODO: Implementar ternário com sintaxe ? : ao invés de if/else
# def p_expression_ternary(p):
#     '''expression : expression IF expression ELSE expression'''
#     p[0] = ('ternary', p[3], p[1], p[5])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULTIPLY expression
                  | expression DIVIDE expression
                  | expression MODULO expression
                  | expression POWER expression
                  | expression DOUBLESTAR expression
                  | expression BITWISEAND expression
                  | expression BITWISEOR expression
                  | expression BITWISEXOR expression
                  | expression LEFTSHIFT expression
                  | expression RIGHTSHIFT expression'''
    op = p[2]
    if op == '**':
        op = 'power'
    p[0] = (op, p[1], p[3])

def p_expression_unary(p):
    '''expression : MINUS expression %prec MINUS
                  | PLUS expression %prec PLUS
                  | BITWISENOT expression'''
    p[0] = ('unary', p[1], p[2])

def p_expression_comparison(p):
    '''expression : expression GT expression
                  | expression LT expression
                  | expression EQ expression
                  | expression NEQ expression
                  | expression GE expression
                  | expression LE expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_membership(p):
    '''expression : expression IN expression
                  | expression IS expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = p[1]

def p_expression_string(p):
    '''expression : STRING'''
    p[0] = p[1]

def p_expression_bool(p):
    '''expression : TRUE
                  | FALSE'''
    p[0] = True if p[1] == "True" else False

def p_expression_none(p):
    '''expression : NONE'''
    p[0] = None

# Removed: duplicate rule for DEVICE LBRACKET expression RBRACKET
# Already defined in p_expression_device_alloc (line 345)

# Removed: duplicate rule for SHARED LBRACKET expression RBRACKET
# Already defined in p_expression_shared_alloc (line 350)

def p_expression_await_expr(p):
    '''expression : AWAIT expression'''
    p[0] = ('await_expr', p[2])

def p_expression_yield_expr(p):
    '''expression : YIELD expression'''
    p[0] = ('yield_expr', p[2])


def p_expression_list_comprehension(p):
    '''expression : LBRACKET expression FOR IDENTIFIER IN expression RBRACKET
                  | LBRACKET expression FOR IDENTIFIER IN expression IF expression RBRACKET'''
    if len(p) == 8:
        p[0] = ('list_comp', p[2], p[4], p[6], None)
    else:
        p[0] = ('list_comp', p[2], p[4], p[6], p[8])

def p_expression_dict_comprehension(p):
    '''expression : LBRACE expression COLON expression FOR IDENTIFIER IN expression RBRACE
                  | LBRACE expression COLON expression FOR IDENTIFIER IN expression IF expression RBRACE'''
    if len(p) == 10:
        p[0] = ('dict_comp', p[2], p[4], p[6], p[8], None)
    else:
        p[0] = ('dict_comp', p[2], p[4], p[6], p[8], p[10])

def p_expression_identifier(p):
    '''expression : IDENTIFIER'''
    if p[1] == "True":
        p[0] = True
    elif p[1] == "False":
        p[0] = False
    else:
        p[0] = ('var', p[1])

def p_empty(p):
    'empty :'
    p[0] = None

def p_error(p):
    if p:
        print(f"Erro sintático na linha {p.lineno}, próximo ao token '{p.value}'")
    else:
        print("Erro sintático: Final inesperado do arquivo ou bloco mal fechado.")

parser = yacc.yacc()