"""Testes para o Sistema de Módulos do MoonLight"""
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from module_loader import ModuleLoader, Module
from executor_simple import variaveis, executar_codigo

class TestModuleSystem(unittest.TestCase):
    
    def setUp(self):
        """Limpa estado antes de cada teste"""
        variaveis.clear()
        self.loader = ModuleLoader()
        self.loader.clear_cache()
    
    def test_module_loader_creation(self):
        """Testa criação do module loader"""
        self.assertIsInstance(self.loader, ModuleLoader)
        self.assertGreater(len(self.loader.module_paths), 0)
    
    def test_find_stdlib_module(self):
        """Testa que encontra módulos da stdlib"""
        math_path = self.loader.find_module('math')
        self.assertIsNotNone(math_path)
        self.assertTrue(math_path.endswith('math.gpu'))
        self.assertTrue(os.path.exists(math_path))
    
    def test_load_math_module(self):
        """Testa carregamento do módulo math"""
        module = self.loader.load_module('math')
        self.assertIsInstance(module, Module)
        self.assertEqual(module.name, 'math')
        self.assertIn('PI', module.namespace)
        self.assertIn('sqrt', module.namespace)
    
    def test_module_caching(self):
        """Testa que módulos são cacheados"""
        module1 = self.loader.load_module('math')
        module2 = self.loader.load_module('math')
        self.assertIs(module1, module2)  # Mesma instância
    
    def test_import_from(self):
        """Testa import from específico"""
        imports = self.loader.import_from('math', ['PI', 'E'])
        self.assertIn('PI', imports)
        self.assertIn('E', imports)
        self.assertAlmostEqual(imports['PI'], 3.141592653589793)
        self.assertAlmostEqual(imports['E'], 2.718281828459045)
    
    def test_import_from_all(self):
        """Testa import from *"""
        imports = self.loader.import_from('math', ['*'])
        self.assertIn('PI', imports)
        self.assertIn('E', imports)
        self.assertIn('sqrt', imports)
        self.assertIn('abs', imports)
    
    def test_import_nonexistent_module(self):
        """Testa erro ao importar módulo inexistente"""
        with self.assertRaises(ImportError):
            self.loader.load_module('nonexistent_module')
    
    def test_import_nonexistent_function(self):
        """Testa erro ao importar função inexistente"""
        with self.assertRaises(ImportError):
            self.loader.import_from('math', ['nonexistent_function'])
    
    def test_circular_import_detection(self):
        """Testa detecção de imports circulares"""
        # Este teste requer módulos com imports circulares
        # Por enquanto, apenas verifica que a pilha funciona
        self.assertEqual(len(self.loader.loading_stack), 0)
    
    def test_execute_with_import(self):
        """Testa execução de código com import (sqrt usa abs internamente, então importar abs também)"""
        code = """
from math import PI
from math import sqrt
from math import abs
x = sqrt(16)
"""
        variaveis.clear()
        executar_codigo(code)
        self.assertIn('PI', variaveis)
        self.assertIn('x', variaveis)
        self.assertAlmostEqual(variaveis['x'], 4.0, places=1)
    
    def test_execute_math_functions(self):
        """Testa execução de funções matemáticas"""
        code = """
from math import factorial
from math import abs
result1 = factorial(5)
result2 = abs(-10)
"""
        variaveis.clear()
        executar_codigo(code)
        self.assertEqual(variaveis['result1'], 120)
        self.assertEqual(variaveis['result2'], 10)
    
    def test_array_module_functions(self):
        """Testa funções do módulo array"""
        code = """
from array import reverse
from array import sort
lista = [3, 1, 2]
rev = reverse(lista)
sorted_list = sort(lista)
"""
        variaveis.clear()
        executar_codigo(code)
        self.assertEqual(variaveis['rev'], [2, 1, 3])
        self.assertEqual(variaveis['sorted_list'], [1, 2, 3])
    
    def test_module_isolation(self):
        """Testa que módulos têm namespaces isolados"""
        # Carrega módulo math
        math_module = self.loader.load_module('math')
        
        # Variável não deve vazar para o namespace global
        self.assertNotIn('PI', variaveis)
        
        # Mas deve estar no namespace do módulo
        self.assertIn('PI', math_module.namespace)
    
    def test_reload_module(self):
        """Testa recarregamento de módulo"""
        module1 = self.loader.load_module('math')
        module2 = self.loader.reload_module('math')
        # Após reload, não devem ser a mesma instância
        self.assertIsNot(module1, module2)
        # Mas devem ter o mesmo conteúdo
        self.assertEqual(module1.name, module2.name)
    
    def test_list_loaded_modules(self):
        """Testa listagem de módulos carregados"""
        self.assertEqual(len(self.loader.list_loaded_modules()), 0)
        
        self.loader.load_module('math')
        self.assertEqual(len(self.loader.list_loaded_modules()), 1)
        self.assertIn('math', self.loader.list_loaded_modules())
        
        self.loader.load_module('array')
        self.assertEqual(len(self.loader.list_loaded_modules()), 2)

if __name__ == '__main__':
    unittest.main()










