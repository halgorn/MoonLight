"""Testes unitários para o Parser do MoonLight"""
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parser import parser

class TestParser(unittest.TestCase):
    
    def parse(self, code):
        """Helper para parsear código"""
        return parser.parse(code)
    
    def test_simple_assignment(self):
        """Testa atribuição simples"""
        ast = self.parse("x = 10")
        self.assertEqual(ast[0][0], 'assign')
        self.assertEqual(ast[0][1], 'x')
        self.assertEqual(ast[0][2], 10)
    
    def test_arithmetic_operations(self):
        """Testa operações aritméticas"""
        ast = self.parse("result = 10 + 5 * 2")
        self.assertEqual(ast[0][0], 'assign')
        # Verifica que há uma expressão aritmética
        expr = ast[0][2]
        self.assertEqual(expr[0], '+')
    
    def test_if_statement(self):
        """Testa estrutura if"""
        code = """
if (x > 5) {
    y = 10
}
"""
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'if')
        self.assertEqual(ast[0][1][0], '>')
    
    def test_if_else_statement(self):
        """Testa estrutura if-else"""
        code = """
if (x > 5) {
    y = 10
} else {
    y = 0
}
"""
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'if-else')
    
    def test_while_loop(self):
        """Testa loop while"""
        code = """
while (x > 0) {
    x = x - 1
}
"""
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'while')
    
    def test_for_loop(self):
        """Testa loop for"""
        code = """
for (i = 0; i < 10; i = i + 1) {
    print(i)
}
"""
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'for')
    
    def test_function_definition(self):
        """Testa definição de função"""
        code = """
def soma(a, b) {
    return a + b
}
"""
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'func_def')
        self.assertEqual(ast[0][1], 'soma')
        self.assertEqual(ast[0][2], ['a', 'b'])
    
    def test_function_call(self):
        """Testa chamada de função"""
        code = "result = soma(5, 10)"
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'assign')
        self.assertEqual(ast[0][2][0], 'func_call')
        self.assertEqual(ast[0][2][1], 'soma')
    
    def test_list_creation(self):
        """Testa criação de lista"""
        code = "lista = [1, 2, 3, 4, 5]"
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'assign')
        self.assertEqual(ast[0][2][0], 'list')
        self.assertEqual(len(ast[0][2][1]), 5)
    
    def test_list_indexing(self):
        """Testa indexação de lista"""
        code = "elemento = lista[0]"
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'assign')
        self.assertEqual(ast[0][2][0], 'list_index')
    
    def test_class_definition(self):
        """Testa definição de classe"""
        code = "class Pessoa { }"
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'class_def')
        self.assertEqual(ast[0][1], 'Pessoa')
    
    def test_print_statement(self):
        """Testa comando print"""
        code = 'print("Hello", "World")'
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'print')
        self.assertEqual(len(ast[0][1]), 2)
    
    def test_comparison_operators(self):
        """Testa operadores de comparação"""
        code = "result = x > 5"
        ast = self.parse(code)
        self.assertEqual(ast[0][2][0], '>')
    
    def test_logical_operators(self):
        """Testa operadores lógicos"""
        code = "result = x > 5 and y < 10"
        ast = self.parse(code)
        self.assertEqual(ast[0][2][0], 'and')
    
    def test_builtin_functions(self):
        """Testa funções built-in"""
        code = "size = len(lista)"
        ast = self.parse(code)
        self.assertEqual(ast[0][2][0], 'len')
    
    def test_range_function(self):
        """Testa função range"""
        code = "r = range(10)"
        ast = self.parse(code)
        self.assertEqual(ast[0][2][0], 'range')
    
    def test_compound_assignment(self):
        """Testa atribuição composta"""
        code = "x += 5"
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'compound_assign')
        self.assertEqual(ast[0][2], '+=')
    
    def test_increment_operators(self):
        """Testa operadores de incremento"""
        code = "x++"
        ast = self.parse(code)
        self.assertEqual(ast[0][0], 'post_increment')

if __name__ == '__main__':
    unittest.main()

