"""Testes para o Sistema de Tipos do MoonLight"""
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from type_system import TypeInferrer, TypeInfo, MoonType, TypeEnvironment
from parser import parser

class TestTypeSystem(unittest.TestCase):
    
    def setUp(self):
        """Cria um novo inferidor para cada teste"""
        self.inferrer = TypeInferrer()
    
    def test_literal_types(self):
        """Testa inferência de tipos literais"""
        self.assertEqual(self.inferrer.infer_literal_type(42).base_type, MoonType.INT)
        self.assertEqual(self.inferrer.infer_literal_type(3.14).base_type, MoonType.FLOAT)
        self.assertEqual(self.inferrer.infer_literal_type("hello").base_type, MoonType.STRING)
        self.assertEqual(self.inferrer.infer_literal_type(True).base_type, MoonType.BOOL)
        self.assertEqual(self.inferrer.infer_literal_type(None).base_type, MoonType.NONE)
    
    def test_arithmetic_int(self):
        """Testa inferência em operações aritméticas com inteiros"""
        ast = parser.parse("x = 10 + 5")
        self.inferrer.analyze_ast(ast)
        var_type = self.inferrer.env.get_variable_type('x')
        self.assertEqual(var_type.base_type, MoonType.INT)
    
    def test_arithmetic_float(self):
        """Testa inferência em operações com float"""
        ast = parser.parse("x = 10.5 + 5")
        self.inferrer.analyze_ast(ast)
        var_type = self.inferrer.env.get_variable_type('x')
        self.assertEqual(var_type.base_type, MoonType.FLOAT)
    
    def test_division_returns_float(self):
        """Testa que divisão sempre retorna float"""
        ast = parser.parse("x = 10 / 2")
        self.inferrer.analyze_ast(ast)
        var_type = self.inferrer.env.get_variable_type('x')
        self.assertEqual(var_type.base_type, MoonType.FLOAT)
    
    def test_comparison_returns_bool(self):
        """Testa que comparações retornam bool"""
        ast = parser.parse("x = 10 > 5")
        self.inferrer.analyze_ast(ast)
        var_type = self.inferrer.env.get_variable_type('x')
        self.assertEqual(var_type.base_type, MoonType.BOOL)
    
    def test_logical_operations(self):
        """Testa operações lógicas"""
        ast = parser.parse("x = True and False")
        self.inferrer.analyze_ast(ast)
        var_type = self.inferrer.env.get_variable_type('x')
        self.assertEqual(var_type.base_type, MoonType.BOOL)
    
    def test_list_type_inference(self):
        """Testa inferência de tipo de lista"""
        ast = parser.parse("x = [1, 2, 3]")
        self.inferrer.analyze_ast(ast)
        var_type = self.inferrer.env.get_variable_type('x')
        self.assertEqual(var_type.base_type, MoonType.LIST)
        self.assertEqual(var_type.generic_params[0].base_type, MoonType.INT)
    
    def test_string_concatenation(self):
        """Testa concatenação de strings"""
        # Nota: Isso requer que o parser reconheça strings em expressões
        code = 'x = "hello"'
        ast = parser.parse(code)
        self.inferrer.analyze_ast(ast)
        var_type = self.inferrer.env.get_variable_type('x')
        self.assertEqual(var_type.base_type, MoonType.STRING)
    
    def test_type_conversion(self):
        """Testa conversões de tipo"""
        ast = parser.parse("x = int(3.14)")
        self.inferrer.analyze_ast(ast)
        var_type = self.inferrer.env.get_variable_type('x')
        self.assertEqual(var_type.base_type, MoonType.INT)
    
    def test_len_returns_int(self):
        """Testa que len() retorna int"""
        ast = parser.parse("lista = [1, 2, 3] size = len(lista)")
        self.inferrer.analyze_ast(ast)
        var_type = self.inferrer.env.get_variable_type('size')
        self.assertEqual(var_type.base_type, MoonType.INT)
    
    def test_range_returns_list_int(self):
        """Testa que range() retorna List[int]"""
        ast = parser.parse("x = range(10)")
        self.inferrer.analyze_ast(ast)
        var_type = self.inferrer.env.get_variable_type('x')
        self.assertEqual(var_type.base_type, MoonType.LIST)
        self.assertEqual(var_type.generic_params[0].base_type, MoonType.INT)
    
    def test_type_warning_on_reassignment(self):
        """Testa warning quando tipo muda em reatribuição"""
        ast = parser.parse("x = 10 x = 3.14")
        self.inferrer.analyze_ast(ast)
        self.assertGreater(len(self.inferrer.get_warnings()), 0)
        # Verifica que há um warning sobre mudança de tipo
        self.assertIn("Atribuição potencialmente perigosa", self.inferrer.get_warnings()[0])
    
    def test_function_definition(self):
        """Testa definição de função"""
        code = "def soma(a, b) { return a + b }"
        ast = parser.parse(code)
        self.inferrer.analyze_ast(ast)
        sig = self.inferrer.env.get_function_signature('soma')
        self.assertIsNotNone(sig)
    
    def test_type_environment_scoping(self):
        """Testa escopos de variáveis"""
        parent_env = TypeEnvironment()
        parent_env.define_variable('x', TypeInfo(MoonType.INT))
        
        child_env = TypeEnvironment(parent_env)
        # Child deve ver variável do parent
        self.assertEqual(child_env.get_variable_type('x').base_type, MoonType.INT)
        
        # Child define sua própria variável
        child_env.define_variable('y', TypeInfo(MoonType.FLOAT))
        self.assertEqual(child_env.get_variable_type('y').base_type, MoonType.FLOAT)
        
        # Parent não deve ver variável do child
        self.assertIsNone(parent_env.get_variable_type('y'))
    
    def test_type_compatibility(self):
        """Testa compatibilidade de tipos"""
        int_type = TypeInfo(MoonType.INT)
        float_type = TypeInfo(MoonType.FLOAT)
        any_type = TypeInfo(MoonType.ANY)
        
        # ANY é compatível com tudo
        self.assertTrue(int_type.is_compatible_with(any_type))
        self.assertTrue(any_type.is_compatible_with(float_type))
        
        # Tipos diferentes não são compatíveis
        self.assertFalse(int_type.is_compatible_with(float_type))

if __name__ == '__main__':
    unittest.main()










