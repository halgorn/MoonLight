#!/usr/bin/env python3
"""
MoonLight Debugger
Debugger with breakpoints and variable inspection
"""

import sys
from parser import parser
from executor_simple import variaveis

class MoonLightDebugger:
    """Interactive debugger for MoonLight"""
    
    def __init__(self):
        self.breakpoints = set()
        self.current_line = 0
        self.stepping = False
        self.running = True
    
    def set_breakpoint(self, line):
        """Set breakpoint at line"""
        self.breakpoints.add(line)
        print(f"Breakpoint set at line {line}")
    
    def remove_breakpoint(self, line):
        """Remove breakpoint"""
        if line in self.breakpoints:
            self.breakpoints.remove(line)
            print(f"Breakpoint removed from line {line}")
        else:
            print(f"No breakpoint at line {line}")
    
    def list_breakpoints(self):
        """List all breakpoints"""
        if not self.breakpoints:
            print("No breakpoints set")
        else:
            print("Breakpoints:")
            for bp in sorted(self.breakpoints):
                print(f"  Line {bp}")
    
    def inspect_variable(self, name):
        """Inspect variable value"""
        if name in variaveis:
            value = variaveis[name]
            print(f"{name} = {value}")
        else:
            print(f"Variable '{name}' not defined")
    
    def list_variables(self):
        """List all variables"""
        if not variaveis:
            print("No variables defined")
        else:
            print("Variables:")
            for name, value in variaveis.items():
                print(f"  {name} = {value}")
    
    def print_help(self):
        """Print debugger help"""
        help_text = """
MoonLight Debugger Commands:

  b <line>        Set breakpoint at line
  d <line>        Delete breakpoint at line
  l               List all breakpoints
  s               Step to next line
  c               Continue execution
  p <var>         Print variable value
  vars            List all variables
  q               Quit debugger
  h / help        Show this help
"""
        print(help_text)
    
    def debug_loop(self):
        """Main debugger loop"""
        print("MoonLight Debugger")
        print("Type 'h' for help\n")
        
        while True:
            try:
                cmd = input("(moon-db) ").strip()
                
                if not cmd:
                    continue
                
                parts = cmd.split()
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                if command in ['q', 'quit']:
                    print("Quitting debugger")
                    break
                
                elif command in ['h', 'help']:
                    self.print_help()
                
                elif command == 'b':
                    if args:
                        try:
                            line = int(args[0])
                            self.set_breakpoint(line)
                        except ValueError:
                            print("Invalid line number")
                    else:
                        print("Usage: b <line>")
                
                elif command == 'd':
                    if args:
                        try:
                            line = int(args[0])
                            self.remove_breakpoint(line)
                        except ValueError:
                            print("Invalid line number")
                    else:
                        print("Usage: d <line>")
                
                elif command == 'l':
                    self.list_breakpoints()
                
                elif command == 's':
                    self.stepping = True
                    print("Stepping...")
                    # Aqui seria implementada a lógica de step
                
                elif command == 'c':
                    self.stepping = False
                    print("Continuing...")
                    # Aqui seria implementada a lógica de continue
                
                elif command == 'p':
                    if args:
                        self.inspect_variable(args[0])
                    else:
                        print("Usage: p <variable>")
                
                elif command == 'vars':
                    self.list_variables()
                
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'h' for help")
            
            except KeyboardInterrupt:
                print("\n(Use 'q' to quit)")
                continue
            
            except EOFError:
                print("\nQuitting")
                break

def main():
    """Main entry point"""
    debugger = MoonLightDebugger()
    debugger.debug_loop()

if __name__ == '__main__':
    main()









