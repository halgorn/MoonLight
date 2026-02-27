#!/usr/bin/env python3
"""
MoonLight REPL - Interactive Console
"""

import sys
import readline  # For command history
from parser import parser
from executor_simple import interpretar, variaveis

VERSION = "1.0.0"
PROMPT = "moon> "
CONTINUE_PROMPT = "...   "

def print_welcome():
    """Print welcome message"""
    print("""
╔══════════════════════════════════════════╗
║   🌙 MoonLight Interactive Console       ║
║              Version 1.0.0               ║
║   Type 'help' for help, 'exit' to quit  ║
╚══════════════════════════════════════════╝
""")

def print_help():
    """Print help message"""
    help_text = """
MoonLight REPL Commands:

  help            Show this help message
  exit / quit     Exit the REPL
  vars            Show all variables
  clear           Clear all variables
  reset           Reset the REPL
  history         Show command history
  
Examples:
  moon> x = 10
  moon> y = x * 2
  moon> print(y)
  20
  
  moon> def square(n) { return n * n }
  moon> square(5)
  25
  
  moon> from math import PI
  moon> print(PI)
  3.14159...
"""
    print(help_text)

def show_variables():
    """Show all defined variables"""
    if not variaveis:
        print("No variables defined")
        return
    
    print("\nDefined variables:")
    print("-" * 40)
    for name, value in variaveis.items():
        if isinstance(value, tuple) and value[0] in ['function', 'class']:
            print(f"  {name}: <{value[0]}>")
        else:
            value_str = str(value)
            if len(value_str) > 50:
                value_str = value_str[:47] + "..."
            print(f"  {name} = {value_str}")
    print()

def clear_variables():
    """Clear all variables"""
    variaveis.clear()
    print("Variables cleared")

def execute_command(code):
    """Execute a command"""
    # Special commands
    if code.strip() in ['exit', 'quit']:
        return 'exit'
    elif code.strip() == 'help':
        print_help()
        return 'continue'
    elif code.strip() == 'vars':
        show_variables()
        return 'continue'
    elif code.strip() == 'clear':
        clear_variables()
        return 'continue'
    elif code.strip() == 'reset':
        clear_variables()
        print("REPL reset")
        return 'continue'
    elif code.strip() == '':
        return 'continue'
    
    # Parse and execute code
    try:
        ast = parser.parse(code)
        if not ast:
            print("Syntax error")
            return 'error'
        
        result = interpretar(ast)
        
        # Print result if it's not None and not a statement
        if result is not None and not isinstance(result, type(None)):
            print(result)
        
        return 'success'
        
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        return 'interrupt'
    except EOFError:
        return 'exit'
    except Exception as e:
        print(f"Error: {e}")
        return 'error'

def main():
    """Main REPL loop"""
    print_welcome()
    
    buffer = []
    
    while True:
        try:
            # Determine prompt
            if buffer:
                prompt = CONTINUE_PROMPT
            else:
                prompt = PROMPT
            
            # Read line
            line = input(prompt)
            
            # Add to buffer
            buffer.append(line)
            
            # Check if we should execute
            # Simple heuristic: if line ends with } or doesn't have {, execute
            if line.strip() and not line.strip().endswith('{'):
                code = '\n'.join(buffer)
                
                # Execute
                status = execute_command(code)
                
                if status == 'exit':
                    print("Goodbye!")
                    break
                
                # Clear buffer after execution
                buffer = []
        
        except KeyboardInterrupt:
            print("\n(To exit, type 'exit' or press Ctrl+D)")
            buffer = []
            continue
        
        except EOFError:
            print("\nGoodbye!")
            break
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            buffer = []
            continue

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)









