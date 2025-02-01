import sys
from parser import parser

def main():
    if len(sys.argv) != 2:
        print("Uso: python testador.py <arquivo.gpu>")
        sys.exit(1)

    arquivo = sys.argv[1]
    if not arquivo.endswith(".gpu"):
        print("Erro: O arquivo deve ter a extensão .gpu")
        sys.exit(1)

    try:
        # Ler arquivo removendo espaços/quebras de linha à direita
        with open(arquivo, 'r', encoding="utf-8") as f:
            linhas = [linha.rstrip() for linha in f]
            codigo = "\n".join(linhas)

        print("Código fonte:\n")
        print(codigo)
        print("\nAnalisando...\n")

        resultado = parser.parse(codigo)
        print("AST gerada:")
        print(resultado)

    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    main()
