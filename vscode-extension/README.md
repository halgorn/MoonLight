# MoonLight Language Extension for VS Code

## Features

- **Syntax Highlighting**: Full syntax highlighting for `.gpu` files
- **Snippets**: Code snippets for common patterns
- **Run Command**: Execute MoonLight files directly (Ctrl+Shift+R)
- **Compile Command**: Compile to executable

## Keywords

- Control: `if`, `else`, `for`, `while`, `break`, `continue`
- Functions: `def`, `lambda`, `return`, `yield`
- Classes: `class`, `self`
- CUDA: `cuda`, `kernel`, `device`, `gpu`, `shared`, `syncthreads`
- JIT: `@jit`
- Built-ins: `print`, `len`, `sum`, `max`, `min`, `range`

## Installation

1. Copy this folder to `.vscode/extensions/`
2. Reload VS Code
3. Open any `.gpu` file

## Usage

### Run File
- Press `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
- Or: Right-click → "Run MoonLight File"

### Compile File
- Command Palette → "Compile MoonLight File"

## Snippets

- `def` → Function definition
- `class` → Class definition
- `for` → For loop
- `if` → If statement
- `cuda` → CUDA kernel definition

## Requirements

- MoonLight compiler installed
- Python 3.8+

## Release Notes

### 1.0.0
- Initial release
- Syntax highlighting
- Basic snippets
- Run command

## Contributing

Report issues at: https://github.com/moonlight-lang/moonlight









