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
    ('left', 'AT'),
)

def p_program_multiple(p):
    '''program : program statement'''
    p[0] = p[1] + [p[2]]

def p_program_single(p):
    '''program : statement'''
    p[0] = [p[1]]

def p_statement_assign(p):
    '''statement : IDENTIFIER ASSIGN expression'''
    p[0] = ('assign', p[1], p[3])

def p_statement_list_assign(p):
    '''statement : IDENTIFIER LBRACKET expression RBRACKET ASSIGN expression'''
    p[0] = ('list_assign', p[1], p[3], p[6])

def p_statement_attr_assign(p):
    '''statement : IDENTIFIER DOT IDENTIFIER ASSIGN expression'''
    p[0] = ('attr_assign', p[1], p[3], p[5])

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

def p_statement_func_def(p):
    '''statement : DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE'''
    p[0] = ('func_def', p[2], p[4], p[7])

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

def p_statement_yield(p):
    '''statement : YIELD expression
                 | YIELD'''
    if len(p) == 3:
        p[0] = ('yield', p[2])
    else:
        p[0] = ('yield', None)

def p_statement_with(p):
    '''statement : WITH expression AS IDENTIFIER LBRACE program RBRACE
                 | WITH expression LBRACE program RBRACE'''
    if len(p) == 8:
        p[0] = ('with', p[2], p[4], p[6])
    else:
        p[0] = ('with', p[2], None, p[4])

def p_statement_async_def(p):
    '''statement : ASYNC DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE'''
    p[0] = ('async_func_def', p[3], p[5], p[8])

def p_statement_await(p):
    '''statement : AWAIT expression'''
    p[0] = ('await', p[2])

def p_statement_thread(p):
    '''statement : THREAD IDENTIFIER LPAREN argument_list RPAREN'''
    p[0] = ('thread', p[2], p[4])

def p_statement_cuda_kernel(p):
    '''statement : CUDA KERNEL DEF IDENTIFIER LPAREN parameter_list RPAREN LBRACE program RBRACE'''
    p[0] = ('cuda_kernel', p[4], p[6], p[9])

def p_statement_gpu_launch(p):
    '''statement : GPU LBRACKET expression COMMA expression RBRACKET IDENTIFIER LPAREN argument_list RPAREN'''
    p[0] = ('gpu_launch', p[3], p[5], p[7], p[9])

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
    '''expression : IDENTIFIER LPAREN argument_list RPAREN'''
    p[0] = ('func_call', p[1], p[3])

def p_expression_method_call(p):
    '''expression : IDENTIFIER DOT IDENTIFIER LPAREN argument_list RPAREN'''
    p[0] = ('method_call', p[1], p[3], p[5])

def p_expression_attr_access(p):
    '''expression : IDENTIFIER DOT IDENTIFIER'''
    p[0] = ('attr_access', p[1], p[3])

def p_expression_list_index(p):
    '''expression : IDENTIFIER LBRACKET expression RBRACKET'''
    p[0] = ('list_index', p[1], p[3])

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

def p_expression_ternary(p):
    '''expression : expression IF expression ELSE expression'''
    p[0] = ('ternary', p[3], p[1], p[5])

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

def p_expression_device_var(p):
    '''expression : DEVICE LBRACKET expression RBRACKET'''
    p[0] = ('device_var', p[3])

def p_expression_shared_var(p):
    '''expression : SHARED LBRACKET expression RBRACKET'''
    p[0] = ('shared_var', p[3])

def p_expression_await_expr(p):
    '''expression : AWAIT expression'''
    p[0] = ('await_expr', p[2])

def p_expression_yield_expr(p):
    '''expression : YIELD expression'''
    p[0] = ('yield_expr', p[2])

def p_expression_builtin_functions(p):
    '''expression : LEN LPAREN expression RPAREN
                  | SUM LPAREN expression RPAREN
                  | MAX LPAREN expression RPAREN
                  | MIN LPAREN expression RPAREN
                  | TYPE LPAREN expression RPAREN
                  | STR LPAREN expression RPAREN
                  | INT LPAREN expression RPAREN
                  | FLOAT LPAREN expression RPAREN
                  | BOOL LPAREN expression RPAREN
                  | LIST LPAREN expression RPAREN
                  | DICT LPAREN expression RPAREN
                  | SET LPAREN expression RPAREN
                  | TUPLE LPAREN expression RPAREN'''
    p[0] = (p[1].lower(), p[3])

def p_expression_range(p):
    '''expression : RANGE LPAREN expression RPAREN
                  | RANGE LPAREN expression COMMA expression RPAREN
                  | RANGE LPAREN expression COMMA expression COMMA expression RPAREN'''
    if len(p) == 5:
        p[0] = ('range', p[3])
    elif len(p) == 7:
        p[0] = ('range', p[3], p[5])
    else:
        p[0] = ('range', p[3], p[5], p[7])

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