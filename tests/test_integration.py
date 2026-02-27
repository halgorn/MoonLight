"""Testes de integração para programas MoonLight completos"""
import unittest
import sys
import os
from io import StringIO
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from executor_simple import executar_codigo, variaveis, classes

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        """Limpa variáveis antes de cada teste"""
        variaveis.clear()
        classes.clear()
    
    def execute(self, code):
        """Helper para executar código e capturar output"""
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            executar_codigo(code)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        return output
    
    def test_fibonacci_recursive(self):
        """Testa implementação recursiva de Fibonacci"""
        code = """
def fibonacci(n) {
    if (n <= 1) {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}
result = fibonacci(8)
"""
        self.execute(code)
        self.assertEqual(variaveis['result'], 21)
    
    def test_factorial(self):
        """Testa cálculo de fatorial"""
        code = """
def factorial(n) {
    if (n <= 1) {
        return 1
    }
    return n * factorial(n - 1)
}
result = factorial(5)
"""
        self.execute(code)
        self.assertEqual(variaveis['result'], 120)
    
    def test_bubble_sort(self):
        """Testa implementação de bubble sort"""
        code = """
lista = [5, 2, 8, 1, 9]
n = len(lista)
for (i = 0; i < n; i = i + 1) {
    for (j = 0; j < n - 1; j = j + 1) {
        if (lista[j] > lista[j + 1]) {
            temp = lista[j]
            lista[j] = lista[j + 1]
            lista[j + 1] = temp
        }
    }
}
"""
        self.execute(code)
        self.assertEqual(variaveis['lista'], [1, 2, 5, 8, 9])
    
    def test_sum_of_even_numbers(self):
        """Testa soma de números pares"""
        code = """
sum = 0
for (i = 1; i <= 10; i = i + 1) {
    if (i % 2 == 0) {
        sum = sum + i
    }
}
"""
        self.execute(code)
        self.assertEqual(variaveis['sum'], 30)
    
    def test_class_with_methods(self):
        """Testa classe com múltiplos métodos"""
        code = """
class Calculator {
    def __init__() {
        self.result = 0
    }
    
    def add(value) {
        self.result = self.result + value
        return self.result
    }
    
    def multiply(value) {
        self.result = self.result * value
        return self.result
    }
}
calc = Calculator()
calc.result = 10
r1 = calc.add(5)
r2 = calc.multiply(2)
"""
        self.execute(code)
        # 10 + 5 = 15, 15 * 2 = 30
        self.assertEqual(variaveis['r2'], 30)
    
    def test_nested_loops(self):
        """Testa loops aninhados"""
        code = """
sum = 0
for (i = 1; i <= 3; i = i + 1) {
    for (j = 1; j <= 3; j = j + 1) {
        sum = sum + i * j
    }
}
"""
        self.execute(code)
        # (1*1 + 1*2 + 1*3) + (2*1 + 2*2 + 2*3) + (3*1 + 3*2 + 3*3)
        # = 6 + 12 + 18 = 36
        self.assertEqual(variaveis['sum'], 36)
    
    def test_prime_numbers(self):
        """Testa verificação de números primos"""
        code = """
def is_prime(n) {
    if (n <= 1) {
        return False
    }
    for (i = 2; i < n; i = i + 1) {
        if (n % i == 0) {
            return False
        }
    }
    return True
}
result1 = is_prime(7)
result2 = is_prime(10)
"""
        self.execute(code)
        self.assertEqual(variaveis['result1'], True)
        self.assertEqual(variaveis['result2'], False)
    
    def test_list_operations(self):
        """Testa operações com listas"""
        code = """
lista = [1, 2, 3]
tamanho = len(lista)
soma = sum(lista)
maximo = max(lista)
minimo = min(lista)
"""
        self.execute(code)
        self.assertEqual(variaveis['tamanho'], 3)
        self.assertEqual(variaveis['soma'], 6)
        self.assertEqual(variaveis['maximo'], 3)
        self.assertEqual(variaveis['minimo'], 1)
    
    def test_nested_functions(self):
        """Testa chamadas de funções aninhadas"""
        code = """
def double(x) {
    return x * 2
}
def triple(x) {
    return x * 3
}
def combine(x) {
    return double(x) + triple(x)
}
result = combine(5)
"""
        self.execute(code)
        # double(5) + triple(5) = 10 + 15 = 25
        self.assertEqual(variaveis['result'], 25)
    
    def test_complex_conditionals(self):
        """Testa condicionais complexas"""
        code = """
x = 15
y = 20
z = 10
if (x > z and y > z) {
    if (x > y) {
        result = x
    } else {
        result = y
    }
} else {
    result = z
}
"""
        self.execute(code)
        self.assertEqual(variaveis['result'], 20)

if __name__ == '__main__':
    unittest.main()










