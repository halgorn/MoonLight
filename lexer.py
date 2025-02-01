import ply.lex as lex

# Definição dos tokens
tokens = (
    'IDENTIFIER',  # Identificadores como nomes de variáveis
    'NUMBER',      # Números inteiros ou floats
    'ASSIGN',      # Operador de atribuição '='
    'PLUS',        # Operador '+'
    'MINUS',       # Operador '-'
    'MULTIPLY',    # Operador '*'
    'DIVIDE',      # Operador '/'
    'LPAREN',      # Parêntese esquerdo '('
    'RPAREN',      # Parêntese direito ')'
)

# Regex para tokens
t_ASSIGN    = r'='
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_MULTIPLY  = r'\*'
t_DIVIDE    = r'/'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_ignore    = ' \t'  # Ignorar espaços e tabs

# Função para reconhecer números
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    try:
        t.value = float(t.value) if '.' in t.value else int(t.value)
    except ValueError:
        print(f"Erro léxico: valor inválido {t.value}")
        t.value = 0
    return t

# Função para reconhecer identificadores
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

# Ignorar quebras de linha e atualizar a contagem de linhas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Tratamento de erros léxicos
def t_error(t):
    print(f"Erro léxico: Caractere inválido '{t.value[0]}' na linha {t.lineno}, posição {t.lexpos}")
    t.lexer.skip(1)

# Construir o lexer
lexer = lex.lex()

# (Opcional) Teste rápido do lexer
if __name__ == "__main__":
    test_code = "x = 10 + 2 * (3 - 1)\ny = x / 2\nz = y + 5"
    lexer.input(test_code)
    print("Tokens:")
    for token in lexer:
        print(token)
