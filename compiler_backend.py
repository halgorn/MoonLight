import subprocess
import sys
import os

def check_cl_exe():
    """Verifica se o cl.exe está no PATH (somente no Windows)."""
    if os.name == 'nt':
        try:
            # O comando 'where' retorna o caminho para cl.exe se estiver presente
            subprocess.check_output("where cl.exe", shell=True)
        except subprocess.CalledProcessError:
            print("❌ Erro: 'cl.exe' não foi encontrado no PATH.")
            print("Por favor, certifique-se de que o Visual Studio e o compilador C++ estão instalados.")
            print("► Dicas:")
            print("   - Abra o 'Developer Command Prompt for Visual Studio'.")
            print("   - Ou, adicione o diretório que contém cl.exe (ex.:")
            print("     C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\<versão>\\bin\\Hostx64\\x64)")
            print("     ao PATH do sistema.")
            sys.exit(1)

def compilar_codigo(cpp_file="output.cpp", executable="moonlight_program"):
    """Compila o código C++/CUDA gerado para criar um executável."""
    # Verifica se cl.exe está disponível (somente no Windows)
    check_cl_exe()
    
    comando = ["nvcc", cpp_file, "-o", executable]

    try:
        subprocess.check_call(comando)
        print("✅ Compilação realizada com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante a compilação: {e}")
        sys.exit(1)

    return executable

def executar_programa(executable):
    """Executa o programa compilado."""
    try:
        if os.name == "nt":  # Windows
            subprocess.check_call([f".\\{executable}.exe"])
        else:  # Linux/Mac
            subprocess.check_call([f"./{executable}"])
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar o programa: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Uso: python compiler_backend.py <arquivo.gpu>")
        sys.exit(1)

    cpp_file = "output.cpp"
    executable = "moonlight_program"

    print("🚀 Transpilando código Moonlight para C++/CUDA...")
    transpiler_cmd = ["python", "transpiler.py", sys.argv[1]]
    subprocess.check_call(transpiler_cmd)

    print("⚙️  Compilando código gerado...")
    compilar_codigo(cpp_file, executable)

    print("🎯 Executando o programa compilado...")
    executar_programa(executable)

if __name__ == "__main__":
    main()
