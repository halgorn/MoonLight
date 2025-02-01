from parser import parser

variaveis = {}  # Armazena nome -> valor

def interpretar(ast):
    """
    Interpreta um nó ou lista de nós da AST.
    """
    # Se for lista, percorra cada declaração
    if isinstance(ast, list):
        for node in ast:
            interpretar(node)
        return

    # Se for tupla, verifique o tipo de operação
    if isinstance(ast, tuple):
        op = ast[0]
        
        if op == 'assign':
            # Ex: ('assign', 'x', expressão)
            variaveis[ast[1]] = interpretar(ast[2])
        elif op in ['+', '-', '*', '/']:
            # Ex: ('+', exp1, exp2)
            val_esq = interpretar(ast[1])
            val_dir = interpretar(ast[2])
            if op == '+':
                return val_esq + val_dir
            elif op == '-':
                return val_esq - val_dir
            elif op == '*':
                return val_esq * val_dir
            elif op == '/':
                return val_esq / val_dir
        elif op == 'var':
            # Retorna o valor da variável se existir
            nome_var = ast[1]
            return variaveis.get(nome_var, 0)  # Retorna 0 se não existir
        else:
            print(f"Operação desconhecida: {op}")
    else:
        # Se for um número (int ou float)
        return ast

def executar_codigo(codigo):
    """
    Executa todo o código, interpretando a AST resultante.
    """
    ast = parser.parse(codigo)
    interpretar(ast)
    print("Estado final das variáveis:")
    print(variaveis)

# (Opcional) Teste rápido do executor
if __name__ == "__main__":
    teste = """x = 10 + 2 * (3 - 1)
y = x / 2
z = y + 5
"""
    executar_codigo(teste)
