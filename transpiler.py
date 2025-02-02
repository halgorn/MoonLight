import os
import sys
from parser import parser

def traduzir_ast(node, indent=1):
    """Traduz um nó da AST para código C++"""
    ind = "    " * indent
    if isinstance(node, list):
        codigo = ""
        for n in node:
            codigo += traduzir_ast(n, indent) + "\n"
        return codigo
    elif isinstance(node, tuple):
        op = node[0]
        if op == 'assign':
            return f"{ind}int {node[1]} = {traduzir_ast(node[2], 0)};"
        elif op in ['+', '-', '*', '/']:
            return f"({traduzir_ast(node[1], 0)} {op} {traduzir_ast(node[2], 0)})"
        elif op in ['>', '<', '==', '!=']:
            return f"({traduzir_ast(node[1], 0)} {op} {traduzir_ast(node[2], 0)})"
        elif op == 'if':
            cond = traduzir_ast(node[1], 0)
            bloco = traduzir_ast(node[2], indent+1)
            return f"{ind}if {cond} {{\n{bloco}{ind}}}"
        elif op == 'if-else':
            cond = traduzir_ast(node[1], 0)
            bloco_if = traduzir_ast(node[2], indent+1)
            bloco_else = traduzir_ast(node[3], indent+1)
            return f"{ind}if {cond} {{\n{bloco_if}{ind}}} else {{\n{bloco_else}{ind}}}"
        elif op == 'while':
            cond = traduzir_ast(node[1], 0)
            bloco = traduzir_ast(node[2], indent+1)
            return f"{ind}while {cond} {{\n{bloco}{ind}}}"
        elif op == 'for':
            init = traduzir_ast(node[1], 0)
            cond = traduzir_ast(node[2], 0)
            update = traduzir_ast(node[3], 0)
            bloco = traduzir_ast(node[4], indent+1)
            return f"{ind}for ({init} {cond}; {update}) {{\n{bloco}{ind}}}"
        elif op == 'print':
            expr = traduzir_ast(node[1], 0)
            return f'{ind}printf("%d\\n", {expr});'
        elif op == 'var':
            return node[1]
        else:
            return f"{ind}// Operação desconhecida: {op}"
    else:
        return str(node)

def gerar_codigo_cpp(ast):
    """Gera código C++ a partir da AST."""
    codigo = """#include <iostream>
using namespace std;

int main() {
"""
    codigo += traduzir_ast(ast, indent=1)
    codigo += "\n    return 0;\n}"
    return codigo

def compilar_codigo(codigo, output_file="output.cpp"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(codigo)
    print(f"Código C++ gerado salvo em {output_file}")

def main():
    if len(sys.argv) != 2:
        print("Uso: python transpiler.py <arquivo.gpu>")
        sys.exit(1)

    arquivo = sys.argv[1]
    
    if not os.path.exists(arquivo):
        print(f"Erro: Arquivo {arquivo} não encontrado.")
        sys.exit(1)

    with open(arquivo, "r", encoding="utf-8") as f:
        codigo_moonlight = f.read()

    ast = parser.parse(codigo_moonlight)
    codigo_cpp = gerar_codigo_cpp(ast)
    compilar_codigo(codigo_cpp)

if __name__ == "__main__":
    main()
