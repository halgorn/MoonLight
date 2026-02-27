#!/usr/bin/env python3
"""
MoonLight Compiler CLI (moonc)
Compila arquivos .gpu para executáveis standalone
"""

import sys
import os
import argparse
from pathlib import Path

# Import do MoonLight
from parser import parser
from transpiler import gerar_codigo_cpp

VERSION = "1.0.0"

def print_banner():
    """Imprime banner do compilador"""
    try:
        print("""
╔════════════════════════════════════════╗
║      🌙 MoonLight Compiler (moonc)     ║
║            Version 1.0.0               ║
╚════════════════════════════════════════╝
""")
    except:
        print("=" * 40)
        print("   MoonLight Compiler (moonc)")
        print("       Version 1.0.0")
        print("=" * 40)

def compile_file(input_file, output_file=None, optimize=True, verbose=False):
    """
    Compila arquivo .gpu para executável
    
    Args:
        input_file: Arquivo de entrada .gpu
        output_file: Nome do executável de saída
        optimize: Aplicar otimizações
        verbose: Modo verboso
    """
    if verbose:
        print(f"[INFO] Compilando {input_file}...")
    
    # Ler código fonte
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"[ERRO] Arquivo não encontrado: {input_file}")
        return 1
    except Exception as e:
        print(f"[ERRO] Erro ao ler arquivo: {e}")
        return 1
    
    # Parse
    if verbose:
        print("[INFO] Analisando sintaxe...")
    
    try:
        ast = parser.parse(codigo)
        if not ast:
            print("[ERRO] Erro ao fazer parsing do código")
            return 1
    except Exception as e:
        print(f"[ERRO] Erro de sintaxe: {e}")
        return 1
    
    # Transpile para C++
    if verbose:
        print("[INFO] Gerando código C++...")
    
    try:
        codigo_cpp = gerar_codigo_cpp(ast)
    except Exception as e:
        print(f"[ERRO] Erro ao transpilar: {e}")
        return 1
    
    # Determinar nome de saída
    if not output_file:
        output_file = Path(input_file).stem
        if sys.platform == 'win32':
            output_file += '.exe'
    
    # Escrever arquivo C++
    cpp_file = f"{Path(input_file).stem}.cpp"
    try:
        with open(cpp_file, 'w', encoding='utf-8') as f:
            f.write(codigo_cpp)
        if verbose:
            print(f"[INFO] Código C++ salvo em {cpp_file}")
    except Exception as e:
        print(f"[ERRO] Erro ao escrever C++: {e}")
        return 1
    
    # Compilar com g++/nvcc
    if verbose:
        print(f"[INFO] Compilando para {output_file}...")
    
    compile_cmd = f"g++ {cpp_file} -o {output_file} -std=c++17"
    if optimize:
        compile_cmd += " -O2"
    
    ret = os.system(compile_cmd)
    
    if ret != 0:
        print("[ERRO] Falha na compilação C++")
        return 1
    
    # Limpar arquivo intermediário
    if not verbose:
        try:
            os.remove(cpp_file)
        except:
            pass
    
    print(f"[SUCESSO] Executável gerado: {output_file}")
    return 0

def run_file(input_file, args=None):
    """Executa arquivo .gpu diretamente"""
    print(f"Executando {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        ast = parser.parse(codigo)
        if not ast:
            print("[ERRO] Erro ao fazer parsing")
            return 1
        
        from executor_simple import interpretar
        interpretar(ast)
        return 0
    except Exception as e:
        print(f"[ERRO] Erro na execucao: {e}")
        return 1

def check_file(input_file):
    """Verifica sintaxe sem executar"""
    print(f"Verificando {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        ast = parser.parse(codigo)
        
        if ast:
            print("[OK] Sintaxe valida")
            return 0
        else:
            print("[ERRO] Erro de sintaxe")
            return 1
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        return 1

def emit_assembly(input_file, output_file=None, verbose=False):
    """Gera arquivo assembly (.s) via LLVM a partir do .gpu (apenas funções host)."""
    try:
        from llvm_backend import generate_llvm_for_program, generate_assembly_from_ir
    except ImportError:
        print("[ERRO] llvmlite não instalado. Use: pip install llvmlite")
        return 1
    with open(input_file, 'r', encoding='utf-8') as f:
        codigo = f.read()
    try:
        ast = parser.parse(codigo)
    except Exception as e:
        print(f"[ERRO] Erro de sintaxe: {e}")
        return 1
    if not ast:
        print("[ERRO] Erro ao fazer parsing")
        return 1
    ir_str = generate_llvm_for_program(ast)
    if not ir_str:
        print("[ERRO] Nenhuma função host para gerar IR LLVM (ou llvmlite indisponível)")
        return 1
    asm = generate_assembly_from_ir(ir_str)
    if not asm:
        print("[ERRO] Falha ao gerar assembly")
        return 1
    out = output_file or Path(input_file).stem + '.s'
    with open(out, 'w', encoding='utf-8') as f:
        f.write(asm)
    if verbose:
        print(f"[INFO] Assembly salvo em {out}")
    print(f"[SUCESSO] Assembly gerado: {out}")
    return 0

def emit_object(input_file, output_file=None, verbose=False):
    """Gera arquivo objeto (.o) via LLVM a partir do .gpu (apenas funções host)."""
    try:
        from llvm_backend import generate_llvm_for_program, generate_object_from_ir
    except ImportError:
        print("[ERRO] llvmlite não instalado. Use: pip install llvmlite")
        return 1
    with open(input_file, 'r', encoding='utf-8') as f:
        codigo = f.read()
    try:
        ast = parser.parse(codigo)
    except Exception as e:
        print(f"[ERRO] Erro de sintaxe: {e}")
        return 1
    if not ast:
        print("[ERRO] Erro ao fazer parsing")
        return 1
    ir_str = generate_llvm_for_program(ast)
    if not ir_str:
        print("[ERRO] Nenhuma função host para gerar IR LLVM (ou llvmlite indisponível)")
        return 1
    out = output_file or Path(input_file).stem + '.o'
    if not generate_object_from_ir(ir_str, out):
        print("[ERRO] Falha ao gerar objeto")
        return 1
    if verbose:
        print(f"[INFO] Objeto salvo em {out}")
    print(f"[SUCESSO] Objeto gerado: {out}")
    return 0

def main():
    """Main CLI"""
    parser_cli = argparse.ArgumentParser(
        description='MoonLight Compiler - Compile .gpu files',
        prog='moonc'
    )
    
    parser_cli.add_argument('input', help='Input .gpu file')
    parser_cli.add_argument('-o', '--output', help='Output executable name')
    parser_cli.add_argument('-O', '--optimize', action='store_true', 
                           help='Enable optimizations')
    parser_cli.add_argument('-v', '--verbose', action='store_true',
                           help='Verbose output')
    parser_cli.add_argument('-r', '--run', action='store_true',
                           help='Run directly without compiling')
    parser_cli.add_argument('-c', '--check', action='store_true',
                           help='Check syntax only')
    parser_cli.add_argument('-S', '--asm', action='store_true',
                           dest='emit_asm',
                           help='Emit assembly (.s) via LLVM (requires llvmlite)')
    parser_cli.add_argument('--emit-obj', action='store_true',
                           dest='emit_obj',
                           help='Emit object file (.o) via LLVM (requires llvmlite)')
    parser_cli.add_argument('--version', action='version',
                           version=f'moonc {VERSION}')
    
    args = parser_cli.parse_args()
    
    # Print banner
    if args.verbose:
        print_banner()
    
    # Verificar arquivo existe
    if not os.path.exists(args.input):
        print(f"[ERRO] Arquivo não encontrado: {args.input}")
        return 1
    
    # Executar ação
    if args.check:
        return check_file(args.input)
    elif getattr(args, 'emit_asm', False):
        return emit_assembly(args.input, args.output, args.verbose)
    elif getattr(args, 'emit_obj', False):
        return emit_object(args.input, args.output, args.verbose)
    elif args.run:
        return run_file(args.input)
    else:
        return compile_file(args.input, args.output, args.optimize, args.verbose)

if __name__ == '__main__':
    sys.exit(main())

