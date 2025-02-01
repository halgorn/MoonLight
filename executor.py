from parser import parser

variaveis = {}  # Armazena nome -> valor

def interpretar(ast):
    """
    Interpreta um nó ou lista de nós da AST.
    """
    # Se for lista, percorre cada declaração
    if isinstance(ast, list):
        for node in ast:
            interpretar(node)
        return

    # Se for tupla, verifica o tipo de operação
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
        
        elif op == 'if':
            # Executa o bloco do IF se a condição for verdadeira
            condicao = interpretar(ast[1])
            if condicao:
                interpretar(ast[2])
        
        elif op == 'if-else':
            # Executa o bloco do IF ou do ELSE dependendo da condição
            condicao = interpretar(ast[1])
            if condicao:
                interpretar(ast[2])
            else:
                interpretar(ast[3])
        
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
    teste = """
x = 10
y = 5

if (x > y) {
    z = x - y
} else {
    z = y - x
}
"""
    executar_codigo(teste)
