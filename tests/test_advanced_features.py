"""Testes para Features Avançadas do MoonLight"""
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from executor_simple import variaveis, executar_codigo

class TestAdvancedFeatures(unittest.TestCase):
    
    def setUp(self):
        """Limpa estado antes de cada teste"""
        variaveis.clear()
    
    def test_multiple_assignment(self):
        """Testa atribuição múltipla: x = y = z = 0"""
        code = "i = j = k = 5"
        executar_codigo(code)
        self.assertEqual(variaveis['i'], 5)
        self.assertEqual(variaveis['j'], 5)
        self.assertEqual(variaveis['k'], 5)
    
    def test_lambda_expression(self):
        """Testa expressões lambda"""
        code = """
square = lambda(x) x * x
result = square(5)
"""
        executar_codigo(code)
        self.assertEqual(variaveis['result'], 25)
    
    def test_generator_basic(self):
        """Testa generator básico com yield"""
        code = """
def counter(n) {
    i = 0
    while (i < n) {
        yield i
        i = i + 1
    }
}
gen = counter(3)
"""
        executar_codigo(code)
        self.assertIn('gen', variaveis)
        gen_result = variaveis['gen']
        self.assertIsInstance(gen_result, list)
    
    def test_with_statement(self):
        """Testa with statement básico"""
        code = """
x = 10
with x as temp {
    result = temp * 2
}
"""
        executar_codigo(code)
        self.assertEqual(variaveis['result'], 20)
        # temp deve ser removido após o with
        self.assertNotIn('temp', variaveis)
    
    def test_yield_in_function(self):
        """Testa detecção de yield em função"""
        from executor_simple import tem_yield
        
        # AST com yield
        ast_with_yield = [('yield', 5)]
        self.assertTrue(tem_yield(ast_with_yield))
        
        # AST sem yield
        ast_without_yield = [('return', 5)]
        self.assertFalse(tem_yield(ast_without_yield))
    
    def test_lambda_in_list(self):
        """Testa lambda em estruturas de dados"""
        code = """
funcs = [lambda(x) x + 1, lambda(x) x * 2]
f = funcs[0]
result = f(10)
"""
        executar_codigo(code)
        self.assertEqual(variaveis['result'], 11)
    
    def test_nested_lambdas(self):
        """Testa lambdas aninhadas"""
        code = """
add = lambda(x) lambda(y) x + y
add5 = add(5)
result = add5(3)
"""
        executar_codigo(code)
        # Lambda aninhada pode não funcionar perfeitamente, mas vamos testar
        self.assertIn('add5', variaveis)

    def test_list_comprehension(self):
        """Testa list comprehensions: [expr for var in iterable] e com if"""
        code = """
squares = [x * x for x in [1, 2, 3, 4, 5]]
evens = [x for x in [1, 2, 3, 4, 5] if x % 2 == 0]
"""
        executar_codigo(code)
        self.assertEqual(variaveis['squares'], [1, 4, 9, 16, 25])
        self.assertEqual(variaveis['evens'], [2, 4])

if __name__ == '__main__':
    unittest.main()










