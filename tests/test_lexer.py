"""Testes unitários para o Lexer do MoonLight"""
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lexer import lexer

class TestLexer(unittest.TestCase):
    
    def tokenize(self, code):
        """Helper para tokenizar código e retornar lista de tokens"""
        lexer.input(code)
        return [(tok.type, tok.value) for tok in lexer]
    
    def test_operators(self):
        """Testa operadores básicos"""
        tokens = self.tokenize("+ - * / % ** == != > < >= <=")
        expected_types = ['PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO', 
                         'DOUBLESTAR', 'EQ', 'NEQ', 'GT', 'LT', 'GE', 'LE']
        self.assertEqual([t[0] for t in tokens], expected_types)
    
    def test_parentheses_and_brackets(self):
        """Testa parênteses, colchetes e chaves"""
        tokens = self.tokenize("() [] {}")
        expected_types = ['LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'LBRACE', 'RBRACE']
        self.assertEqual([t[0] for t in tokens], expected_types)
    
    def test_numbers(self):
        """Testa reconhecimento de números"""
        tokens = self.tokenize("42 3.14 2.5e10 1.5e-3")
        self.assertEqual(tokens[0], ('NUMBER', 42))
        self.assertEqual(tokens[1], ('NUMBER', 3.14))
        self.assertAlmostEqual(tokens[2][1], 2.5e10)
        self.assertAlmostEqual(tokens[3][1], 1.5e-3)
    
    def test_strings(self):
        """Testa reconhecimento de strings"""
        tokens = self.tokenize('"hello" \'world\'')
        self.assertEqual(tokens[0], ('STRING', 'hello'))
        self.assertEqual(tokens[1], ('STRING', 'world'))
    
    def test_identifiers(self):
        """Testa identificadores"""
        tokens = self.tokenize("x variable_name _private")
        self.assertEqual(tokens[0], ('IDENTIFIER', 'x'))
        self.assertEqual(tokens[1], ('IDENTIFIER', 'variable_name'))
        self.assertEqual(tokens[2], ('IDENTIFIER', '_private'))
    
    def test_keywords(self):
        """Testa palavras reservadas"""
        tokens = self.tokenize("if else for while def class return")
        expected_types = ['IF', 'ELSE', 'FOR', 'WHILE', 'DEF', 'CLASS', 'RETURN']
        self.assertEqual([t[0] for t in tokens], expected_types)
    
    def test_compound_operators(self):
        """Testa operadores compostos"""
        tokens = self.tokenize("+= -= *= /= %= **= ++ --")
        expected_types = ['PLUSEQ', 'MINUSEQ', 'MULTEQ', 'DIVEQ', 'MODEQ', 'POWEQ', 'PLUSPLUS', 'MINUSMINUS']
        self.assertEqual([t[0] for t in tokens], expected_types)
    
    def test_bitwise_operators(self):
        """Testa operadores bitwise"""
        tokens = self.tokenize("& | ^ ~ << >>")
        expected_types = ['BITWISEAND', 'BITWISEOR', 'BITWISEXOR', 'BITWISENOT', 'LEFTSHIFT', 'RIGHTSHIFT']
        self.assertEqual([t[0] for t in tokens], expected_types)
    
    def test_comments(self):
        """Testa que comentários são ignorados"""
        tokens = self.tokenize("x = 10 # comentário")
        self.assertEqual(len(tokens), 3)  # x, =, 10
        self.assertEqual([t[0] for t in tokens], ['IDENTIFIER', 'ASSIGN', 'NUMBER'])
    
    def test_booleans(self):
        """Testa valores booleanos"""
        tokens = self.tokenize("True False")
        self.assertEqual(tokens[0], ('TRUE', 'True'))
        self.assertEqual(tokens[1], ('FALSE', 'False'))
    
    def test_none(self):
        """Testa None"""
        tokens = self.tokenize("None")
        self.assertEqual(tokens[0], ('NONE', 'None'))
    
    def test_builtin_functions(self):
        """Testa funções built-in (agora são identificadores normais)"""
        tokens = self.tokenize("len sum max min range")
        # Built-in functions são agora identificadores normais
        expected_types = ['IDENTIFIER', 'IDENTIFIER', 'IDENTIFIER', 'IDENTIFIER', 'IDENTIFIER']
        self.assertEqual([t[0] for t in tokens], expected_types)
        # Verifica os valores
        expected_values = ['len', 'sum', 'max', 'min', 'range']
        self.assertEqual([t[1] for t in tokens], expected_values)
    
    def test_cuda_keywords(self):
        """Testa keywords CUDA"""
        tokens = self.tokenize("cuda kernel gpu device shared")
        expected_types = ['CUDA', 'KERNEL', 'GPU', 'DEVICE', 'SHARED']
        self.assertEqual([t[0] for t in tokens], expected_types)

if __name__ == '__main__':
    unittest.main()

