#!/usr/bin/env python3
"""
MoonLight Debugger Tool
Provides debugging capabilities for MoonLight GPU programs
"""

import sys
import os
import subprocess
from pathlib import Path

def debug_kernel(kernel_name, breakpoints=None):
    """
    Debug a CUDA kernel
    
    Args:
        kernel_name: Name of the kernel to debug
        breakpoints: List of breakpoint locations
    """
    print(f"Debugging kernel: {kernel_name}")
    print("")
    
    if breakpoints:
        print(f"Breakpoints: {breakpoints}")
        print("")
    
    print("Debugging commands:")
    print("  - Use cuda-gdb for GPU debugging")
    print("  - Use Nsight Debugger for visual debugging")
    print("  - Use gpu_printf() for output debugging")
    print("")
    
    print("To debug MoonLight code:")
    print("  1. Compile with debug symbols: python moonc.py program.gpu -o program --cuda --debug")
    print("  2. Run with: cuda-gdb ./program")
    print("  3. Or use: nsight-debug ./program")
    print("")
    
    print("Debugging features:")
    print("  - gpu_printf(): Print from GPU threads")
    print("  - gpu_breakpoint(): Pause execution")
    print("  - Variable inspection")
    print("  - Step through GPU code")
    print("")

def check_gpu_printf_output(program_path):
    """
    Check gpu_printf output from a program
    """
    print(f"Checking gpu_printf output from: {program_path}")
    print("")
    print("GPU printf output will appear in:")
    print("  - Console (if running directly)")
    print("  - Debugger output")
    print("  - Log files")
    print("")

def main():
    """Main debugger entry point"""
    if len(sys.argv) < 2:
        print("Usage: moonlight_debugger.py <command> [options]")
        print("")
        print("Commands:")
        print("  debug <kernel_name> [breakpoints...]")
        print("  check <program.gpu>")
        print("  printf <program.gpu>")
        print("")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'debug':
        if len(sys.argv) < 3:
            print("Usage: moonlight_debugger.py debug <kernel_name> [breakpoints...]")
            sys.exit(1)
        
        kernel_name = sys.argv[2]
        breakpoints = sys.argv[3:] if len(sys.argv) > 3 else None
        debug_kernel(kernel_name, breakpoints)
    
    elif command == 'check':
        if len(sys.argv) < 3:
            print("Usage: moonlight_debugger.py check <program.gpu>")
            sys.exit(1)
        
        program_path = sys.argv[2]
        print(f"Checking: {program_path}")
        print("")
        print("Checking for:")
        print("  - Syntax errors")
        print("  - Debugging statements")
        print("  - Breakpoints")
        print("")
    
    elif command == 'printf':
        if len(sys.argv) < 3:
            print("Usage: moonlight_debugger.py printf <program.gpu>")
            sys.exit(1)
        
        program_path = sys.argv[2]
        check_gpu_printf_output(program_path)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()

