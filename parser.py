import ply.yacc as yacc
from lexer import tokens

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
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
    '''statement : PRINT LPAREN expression RPAREN'''
    p[0] = ('print', p[3])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULTIPLY expression
                  | expression DIVIDE expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_comparison(p):
    '''expression : expression GT expression
                  | expression LT expression
                  | expression EQ expression
                  | expression NEQ expression'''
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

def p_expression_identifier(p):
    '''expression : IDENTIFIER'''
    p[0] = ('var', p[1])

def p_error(p):
    if p:
        print(f"Erro sintático na linha {p.lineno}, próximo ao token '{p.value}'")
    else:
        print("Erro sintático: Final inesperado do arquivo ou bloco mal fechado.")

parser = yacc.yacc()
