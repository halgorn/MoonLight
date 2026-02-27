"""Demonstração do Sistema de Tipos do MoonLight"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from parser import parser
from type_system import TypeInferrer

def demo_type_inference(code: str, description: str):
    """Demonstra inferência de tipos para um código"""
    print(f"\n{'='*60}")
    print(f"DEMO: {description}")
    print(f"{'='*60}")
    print(f"Código:\n{code}\n")
    
    inferrer = TypeInferrer()
    ast = parser.parse(code)
    inferrer.analyze_ast(ast)
    
    print("Tipos Inferidos:")
    for var_name, var_type in inferrer.env.variables.items():
        print(f"  {var_name}: {var_type}")
    
    if inferrer.get_warnings():
        print(f"\nWARNINGS:")
        for warning in inferrer.get_warnings():
            print(f"  - {warning}")
    
    if inferrer.get_errors():
        print(f"\nERROS:")
        for error in inferrer.get_errors():
            print(f"  - {error}")
    
    if not inferrer.get_warnings() and not inferrer.get_errors():
        print("\n[OK] Sem problemas detectados")

# Demo 1: Tipos básicos
demo_type_inference(
    "x = 10\ny = 3.14\nname = \"João\"\nflag = True",
    "Inferência de Tipos Básicos"
)

# Demo 2: Operações aritméticas
demo_type_inference(
    "a = 10\nb = 20\nsum = a + b\navg = sum / 2",
    "Operações Aritméticas (int + int = int, divisão = float)"
)

# Demo 3: Listas com tipos genéricos
demo_type_inference(
    "numbers = [1, 2, 3, 4, 5]\nsize = len(numbers)",
    "Lista com Tipos Genéricos List[int]"
)

# Demo 4: Comparações
demo_type_inference(
    "x = 10\ny = 20\nis_greater = x > y",
    "Comparações Retornam bool"
)

# Demo 5: Warning em reatribuição com tipo diferente
demo_type_inference(
    "x = 10\nx = 3.14",
    "Warning: Mudança de Tipo em Reatribuição"
)

# Demo 6: Range retorna List[int]
demo_type_inference(
    "r = range(10)",
    "Range Retorna List[int]"
)

# Demo 7: Conversões de tipo
demo_type_inference(
    "x = 3.14\ny = int(x)",
    "Conversões de Tipo Explícitas"
)

# Demo 8: Função com inferência
demo_type_inference(
    "def soma(a, b) { return a + b }\nresult = soma(5, 10)",
    "Definição de Função (tipos de parâmetros desconhecidos inicialmente)"
)

print(f"\n{'='*60}")
print("Demonstração Completa!")
print(f"{'='*60}\n")
print("O sistema de tipos do MoonLight:")
print("[OK] Infere tipos automaticamente")
print("[OK] Detecta conversoes implicitas potencialmente perigosas")
print("[OK] Suporta tipos genericos (List[int], etc)")
print("[OK] Mantem escopo adequado de variaveis")
print("[OK] Ajuda a prevenir bugs em tempo de desenvolvimento")

