"""Testes unitários para o Executor do MoonLight"""
import unittest
import sys
import os
from io import StringIO
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from executor_simple import executar_codigo, variaveis, classes

class TestExecutor(unittest.TestCase):
    
    def setUp(self):
        """Limpa variáveis antes de cada teste"""
        variaveis.clear()
        classes.clear()
    
    def execute(self, code):
        """Helper para executar código e capturar output"""
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            # Remove indentação de código multi-linha
            import textwrap
            code = textwrap.dedent(code).strip()
            executar_codigo(code)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        return output
    
    def test_simple_assignment(self):
        """Testa atribuição simples"""
        self.execute("x = 10")
        self.assertEqual(variaveis['x'], 10)
    
    def test_arithmetic_operations(self):
        """Testa operações aritméticas"""
        self.execute("result = 10 + 5 * 2")
        self.assertEqual(variaveis['result'], 20)
    
    def test_comparison_operators(self):
        """Testa operadores de comparação"""
        self.execute("result = 10 > 5")
        self.assertEqual(variaveis['result'], True)
    
    def test_logical_operators(self):
        """Testa operadores lógicos"""
        self.execute("result = (10 > 5) and (3 < 7)")
        self.assertEqual(variaveis['result'], True)
    
    def test_if_statement(self):
        """Testa estrutura if"""
        code = """
x = 10
if (x > 5) {
    y = 20
}
"""
        self.execute(code)
        self.assertEqual(variaveis['y'], 20)
    
    def test_if_else_statement(self):
        """Testa estrutura if-else"""
        code = """
x = 3
if (x > 5) {
    y = 20
} else {
    y = 10
}
"""
        self.execute(code)
        self.assertEqual(variaveis['y'], 10)
    
    def test_while_loop(self):
        """Testa loop while"""
        code = """
x = 5
sum = 0
while (x > 0) {
    sum = sum + x
    x = x - 1
}
"""
        self.execute(code)
        self.assertEqual(variaveis['sum'], 15)
        self.assertEqual(variaveis['x'], 0)
    
    def test_for_loop(self):
        """Testa loop for"""
        code = """
sum = 0
for (i = 1; i <= 5; i = i + 1) {
    sum = sum + i
}
"""
        self.execute(code)
        self.assertEqual(variaveis['sum'], 15)
    
    def test_function_definition_and_call(self):
        """Testa definição e chamada de função"""
        code = """
def soma(a, b) {
    return a + b
}
result = soma(5, 10)
"""
        self.execute(code)
        self.assertEqual(variaveis['result'], 15)
    
    def test_function_with_no_return(self):
        """Testa função sem return"""
        code = """
def set_value() {
    x = 100
}
result = set_value()
"""
        self.execute(code)
        self.assertIsNone(variaveis['result'])
    
    def test_list_creation(self):
        """Testa criação de lista"""
        code = "lista = [1, 2, 3, 4, 5]"
        self.execute(code)
        self.assertEqual(variaveis['lista'], [1, 2, 3, 4, 5])
    
    def test_list_indexing(self):
        """Testa indexação de lista"""
        code = """
lista = [10, 20, 30]
elemento = lista[1]
"""
        self.execute(code)
        self.assertEqual(variaveis['elemento'], 20)
    
    def test_list_assignment(self):
        """Testa atribuição em lista"""
        code = """
lista = [1, 2, 3]
lista[1] = 99
"""
        self.execute(code)
        self.assertEqual(variaveis['lista'][1], 99)
    
    def test_builtin_len(self):
        """Testa função len"""
        code = """
lista = [1, 2, 3, 4, 5]
size = len(lista)
"""
        self.execute(code)
        self.assertEqual(variaveis['size'], 5)
    
    def test_builtin_sum(self):
        """Testa função sum"""
        code = """
lista = [1, 2, 3, 4, 5]
total = sum(lista)
"""
        self.execute(code)
        self.assertEqual(variaveis['total'], 15)
    
    def test_builtin_max(self):
        """Testa função max"""
        code = """
lista = [1, 5, 3, 9, 2]
maximo = max(lista)
"""
        self.execute(code)
        self.assertEqual(variaveis['maximo'], 9)
    
    def test_builtin_min(self):
        """Testa função min"""
        code = """
lista = [5, 1, 3, 9, 2]
minimo = min(lista)
"""
        self.execute(code)
        self.assertEqual(variaveis['minimo'], 1)
    
    def test_builtin_range(self):
        """Testa função range"""
        code = "r = range(5)"
        self.execute(code)
        self.assertEqual(variaveis['r'], [0, 1, 2, 3, 4])
    
    def test_compound_assignment(self):
        """Testa atribuição composta"""
        code = """
x = 10
x += 5
"""
        self.execute(code)
        self.assertEqual(variaveis['x'], 15)
    
    def test_increment_operators(self):
        """Testa operadores de incremento"""
        code = """
x = 5
x++
"""
        self.execute(code)
        self.assertEqual(variaveis['x'], 6)
    
    def test_print_statement(self):
        """Testa comando print"""
        output = self.execute('print("Hello", "World")')
        self.assertIn("Hello World", output)
    
    def test_class_creation(self):
        """Testa criação de classe"""
        code = """
class Pessoa {
    def __init__(nome) {
        self.nome = nome
    }
}
"""
        self.execute(code)
        self.assertIn('Pessoa', classes)
    
    def test_class_instantiation(self):
        """Testa instanciação de classe"""
        code = """
class Pessoa {
    def __init__(nome) {
        self.nome = nome
    }
}
p = Pessoa("João")
"""
        self.execute(code)
        self.assertIsNotNone(variaveis.get('p'))
    
    def test_break_in_loop(self):
        """Testa break em loop"""
        code = """
i = 0
while (i < 10) {
    i = i + 1
    if (i == 5) {
        break
    }
}
"""
        self.execute(code)
        self.assertEqual(variaveis['i'], 5)
    
    def test_continue_in_loop(self):
        """Testa continue em loop"""
        code = """
sum = 0
for (i = 0; i < 5; i = i + 1) {
    if (i == 2) {
        continue
    }
    sum = sum + i
}
"""
        self.execute(code)
        # sum = 0 + 1 + 3 + 4 = 8 (pula o 2)
        self.assertEqual(variaveis['sum'], 8)

if __name__ == '__main__':
    unittest.main()

