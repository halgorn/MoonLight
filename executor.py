from parser import parser

# Dicionário global para armazenar variáveis
variaveis = {}

def interpretar(ast):
    if isinstance(ast, list):
        # Lista de instruções: interpreta cada uma delas
        for node in ast:
            interpretar(node)
        return

    if isinstance(ast, tuple):
        op = ast[0]

        if op == 'assign':
            # Atribuição: o valor da expressão é avaliado e salvo na variável
            variaveis[ast[1]] = interpretar(ast[2])

        elif op in ['+', '-', '*', '/']:
            # Operações aritméticas
            val_esq = interpretar(ast[1])
            val_dir = interpretar(ast[2])
            # Usa a operação nativa do Python; cuidado com a segurança se expandir a linguagem
            return eval(f"{val_esq} {op} {val_dir}")

        elif op in ['>', '<', '==', '!=']:
            # Operações de comparação
            val_esq = interpretar(ast[1])
            val_dir = interpretar(ast[2])
            return eval(f"{val_esq} {op} {val_dir}")

        elif op == 'var':
            # Uso de variável
            return variaveis.get(ast[1], 0)

        elif op == 'if':
            if interpretar(ast[1]):
                interpretar(ast[2])

        elif op == 'if-else':
            if interpretar(ast[1]):
                interpretar(ast[2])
            else:
                interpretar(ast[3])

        elif op == 'while':
            while interpretar(ast[1]):
                interpretar(ast[2])

        elif op == 'for':
            # A tupla do for foi definida como: ('for', init, condition, update, body)
            interpretar(ast[1])  # inicialização
            while interpretar(ast[2]):
                interpretar(ast[4])  # corpo (lista de instruções)
                interpretar(ast[3])  # atualização

        else:
            print(f"Operação desconhecida: {op}")

    else:
        # Caso seja um valor simples (número, string, booleano) já avaliado
        return ast

def executar_codigo(codigo):
    ast = parser.parse(codigo)
    interpretar(ast)
    print("Estado final das variáveis:", variaveis)

if __name__ == "__main__":
    # Código de teste (pode ser removido)
    teste = """
x = 0
while (x < 5) {
    x = x + 1
}
"""
    executar_codigo(teste)
