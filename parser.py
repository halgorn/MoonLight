import ply.yacc as yacc
from lexer import tokens

# Regras de precedência
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE'),
)

# ---
# 1) PROGRAM: Aceita múltiplas statements
# ---
def p_program_multiple(p):
    '''program : program statement'''
    p[0] = p[1] + [p[2]]

def p_program_single(p):
    '''program : statement'''
    p[0] = [p[1]]

# ---
# 2) STATEMENT: Atribuição por enquanto
# ---
def p_statement_assign(p):
    '''statement : IDENTIFIER ASSIGN expression'''
    p[0] = ('assign', p[1], p[3])

# ---
# 3) EXPRESSIONS
# ---
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression MULTIPLY expression
                  | expression DIVIDE expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = p[1]

def p_expression_identifier(p):
    '''expression : IDENTIFIER'''
    # Se quiser, pode futuramente identificar variáveis no interpretador
    p[0] = ('var', p[1])

# ---
# 4) TRATAMENTO DE ERROS
# ---
def p_error(p):
    if p:
        print(f"Erro sintático na linha {p.lineno}, próximo ao token '{p.value}'")
    else:
        print("Erro sintático: Final inesperado do arquivo")

# ---
# 5) CONSTRUIR O PARSER
# ---
parser = yacc.yacc()

# (Opcional) Teste rápido do parser
if __name__ == "__main__":
    test_code = """x = 10 + 2 * (3 - 1)
y = x / 2
z = y + 5
"""
    result = parser.parse(test_code)
    print("AST:", result)
