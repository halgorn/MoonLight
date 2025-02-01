import sys
from executor import executar_codigo

def main():
    if len(sys.argv) != 2:
        print("Uso: python executor_main.py <arquivo.gpu>")
        sys.exit(1)

    arquivo = sys.argv[1]
    if not arquivo.endswith(".gpu"):
        print("Erro: O arquivo deve ter a extensão .gpu")
        sys.exit(1)

    try:
        # Ler o arquivo removendo espaços/quebras de linha indesejadas
        with open(arquivo, 'r', encoding="utf-8") as f:
            linhas = [linha.rstrip() for linha in f]
            codigo = "\n".join(linhas)

        print("Executando o código .gpu...\n")
        executar_codigo(codigo)

    except Exception as e:
        print(f"Erro ao executar o arquivo: {e}")

if __name__ == "__main__":
    main()
