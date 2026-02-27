"""Sistema de Tipos do MoonLight com Inferência Automática"""

from enum import Enum
from typing import Dict, List, Optional, Set, Union

class MoonType(Enum):
    """Tipos básicos do MoonLight"""
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "str"
    NONE = "None"
    LIST = "list"
    DICT = "dict"
    TUPLE = "tuple"
    SET = "set"
    FUNCTION = "function"
    CLASS = "class"
    ANY = "any"
    UNKNOWN = "unknown"

class TypeInfo:
    """Informação de tipo com suporte a genéricos"""
    def __init__(self, base_type: MoonType, generic_params: Optional[List['TypeInfo']] = None):
        self.base_type = base_type
        self.generic_params = generic_params or []
    
    def __str__(self):
        if self.generic_params:
            params_str = ", ".join(str(p) for p in self.generic_params)
            return f"{self.base_type.value}[{params_str}]"
        return self.base_type.value
    
    def __eq__(self, other):
        if not isinstance(other, TypeInfo):
            return False
        return self.base_type == other.base_type and self.generic_params == other.generic_params
    
    def is_compatible_with(self, other: 'TypeInfo') -> bool:
        """Verifica se este tipo é compatível com outro"""
        if self.base_type == MoonType.ANY or other.base_type == MoonType.ANY:
            return True
        if self.base_type == MoonType.UNKNOWN or other.base_type == MoonType.UNKNOWN:
            return True
        return self == other

class TypeEnvironment:
    """Ambiente de tipos para análise semântica"""
    def __init__(self, parent: Optional['TypeEnvironment'] = None):
        self.parent = parent
        self.variables: Dict[str, TypeInfo] = {}
        self.functions: Dict[str, tuple] = {}  # nome -> (params, return_type)
    
    def define_variable(self, name: str, type_info: TypeInfo):
        """Define uma variável no escopo atual"""
        self.variables[name] = type_info
    
    def get_variable_type(self, name: str) -> Optional[TypeInfo]:
        """Obtém o tipo de uma variável"""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get_variable_type(name)
        return None
    
    def define_function(self, name: str, param_types: List[TypeInfo], return_type: TypeInfo):
        """Define uma função"""
        self.functions[name] = (param_types, return_type)
    
    def get_function_signature(self, name: str) -> Optional[tuple]:
        """Obtém a assinatura de uma função"""
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.get_function_signature(name)
        return None

class TypeInferrer:
    """Inferidor de tipos para MoonLight"""
    def __init__(self):
        self.env = TypeEnvironment()
        self.warnings: List[str] = []
        self.errors: List[str] = []
    
    def infer_literal_type(self, value) -> TypeInfo:
        """Infere o tipo de um literal"""
        # Bool deve ser verificado antes de int (bool é subclasse de int em Python)
        if isinstance(value, bool):
            return TypeInfo(MoonType.BOOL)
        elif isinstance(value, int):
            return TypeInfo(MoonType.INT)
        elif isinstance(value, float):
            return TypeInfo(MoonType.FLOAT)
        elif isinstance(value, str):
            return TypeInfo(MoonType.STRING)
        elif value is None:
            return TypeInfo(MoonType.NONE)
        elif isinstance(value, list):
            if value:
                # Infere tipo dos elementos
                elem_type = self.infer_literal_type(value[0])
                return TypeInfo(MoonType.LIST, [elem_type])
            return TypeInfo(MoonType.LIST, [TypeInfo(MoonType.ANY)])
        elif isinstance(value, dict):
            return TypeInfo(MoonType.DICT)
        elif isinstance(value, tuple):
            return TypeInfo(MoonType.TUPLE)
        elif isinstance(value, set):
            return TypeInfo(MoonType.SET)
        return TypeInfo(MoonType.UNKNOWN)
    
    def infer_expression_type(self, ast, env: Optional[TypeEnvironment] = None) -> TypeInfo:
        """Infere o tipo de uma expressão"""
        if env is None:
            env = self.env
        
        # Literal direto
        if not isinstance(ast, tuple):
            return self.infer_literal_type(ast)
        
        op = ast[0]
        
        # Operações aritméticas
        if op in ['+', '-', '*', '/', '%', 'power', '**']:
            left_type = self.infer_expression_type(ast[1], env)
            right_type = self.infer_expression_type(ast[2], env)
            
            # int + int = int
            if left_type.base_type == MoonType.INT and right_type.base_type == MoonType.INT:
                if op == '/':
                    # Divisão sempre retorna float
                    return TypeInfo(MoonType.FLOAT)
                return TypeInfo(MoonType.INT)
            
            # float em qualquer operando = float
            if left_type.base_type in [MoonType.FLOAT, MoonType.INT] and \
               right_type.base_type in [MoonType.FLOAT, MoonType.INT]:
                return TypeInfo(MoonType.FLOAT)
            
            # String + String = String
            if op == '+' and left_type.base_type == MoonType.STRING and right_type.base_type == MoonType.STRING:
                return TypeInfo(MoonType.STRING)
            
            self.warnings.append(f"Operação {op} entre tipos incompatíveis: {left_type} e {right_type}")
            return TypeInfo(MoonType.UNKNOWN)
        
        # Comparações
        elif op in ['>', '<', '==', '!=', '>=', '<=']:
            return TypeInfo(MoonType.BOOL)
        
        # Operações lógicas
        elif op in ['and', 'or', 'not']:
            return TypeInfo(MoonType.BOOL)
        
        # Variável
        elif op == 'var':
            var_name = ast[1]
            var_type = env.get_variable_type(var_name)
            if var_type:
                return var_type
            self.warnings.append(f"Variável '{var_name}' usada antes de ser definida")
            return TypeInfo(MoonType.UNKNOWN)
        
        # Chamada de função built-in
        elif op in ['len', 'sum', 'max', 'min']:
            if op == 'len':
                return TypeInfo(MoonType.INT)
            else:
                # sum, max, min retornam o tipo dos elementos
                arg_type = self.infer_expression_type(ast[1], env)
                if arg_type.generic_params:
                    return arg_type.generic_params[0]
                return TypeInfo(MoonType.UNKNOWN)
        
        # Conversões de tipo
        elif op in ['int', 'float', 'str', 'bool']:
            return TypeInfo(MoonType[op.upper()])
        
        # Lista
        elif op == 'list':
            if ast[1]:
                # Infere tipo do primeiro elemento
                elem_type = self.infer_expression_type(ast[1][0], env)
                return TypeInfo(MoonType.LIST, [elem_type])
            return TypeInfo(MoonType.LIST, [TypeInfo(MoonType.ANY)])
        
        # Range
        elif op == 'range':
            return TypeInfo(MoonType.LIST, [TypeInfo(MoonType.INT)])
        
        # Lambda
        elif op == 'lambda':
            return TypeInfo(MoonType.FUNCTION)
        
        # Chamada de função
        elif op == 'func_call':
            func_name = ast[1]
            sig = env.get_function_signature(func_name)
            if sig:
                return sig[1]  # return type
            return TypeInfo(MoonType.UNKNOWN)
        
        return TypeInfo(MoonType.UNKNOWN)
    
    def check_assignment(self, var_name: str, value_ast, env: Optional[TypeEnvironment] = None):
        """Verifica uma atribuição e atualiza o ambiente"""
        if env is None:
            env = self.env
        
        value_type = self.infer_expression_type(value_ast, env)
        existing_type = env.get_variable_type(var_name)
        
        if existing_type and not value_type.is_compatible_with(existing_type):
            self.warnings.append(
                f"Atribuição potencialmente perigosa: variável '{var_name}' "
                f"era {existing_type}, agora é {value_type}"
            )
        
        env.define_variable(var_name, value_type)
    
    def analyze_ast(self, ast, env: Optional[TypeEnvironment] = None):
        """Analisa uma AST completa e infere tipos"""
        if env is None:
            env = self.env
        
        if isinstance(ast, list):
            for node in ast:
                self.analyze_ast(node, env)
            return
        
        if not isinstance(ast, tuple):
            return
        
        op = ast[0]
        
        # Atribuição
        if op == 'assign':
            var_name = ast[1]
            value = ast[2]
            self.check_assignment(var_name, value, env)
        
        # Definição de função
        elif op == 'func_def':
            func_name = ast[1]
            params = ast[2]
            body = ast[3]
            
            # Cria novo ambiente para a função
            func_env = TypeEnvironment(env)
            
            # Parâmetros têm tipo desconhecido inicialmente
            param_types = []
            for param in (params or []):
                param_type = TypeInfo(MoonType.UNKNOWN)
                func_env.define_variable(param, param_type)
                param_types.append(param_type)
            
            # Analisa o corpo
            self.analyze_ast(body, func_env)
            
            # Por enquanto, return type é desconhecido
            env.define_function(func_name, param_types, TypeInfo(MoonType.UNKNOWN))
        
        # If/while/for
        elif op in ['if', 'if-else', 'while', 'for']:
            # Analisa blocos
            if op == 'if':
                self.analyze_ast(ast[2], env)
            elif op == 'if-else':
                self.analyze_ast(ast[2], env)
                self.analyze_ast(ast[3], env)
            elif op == 'while':
                self.analyze_ast(ast[2], env)
            elif op == 'for':
                # Inicialização, corpo
                self.analyze_ast(ast[1], env)
                self.analyze_ast(ast[4], env)
    
    def get_warnings(self) -> List[str]:
        """Retorna lista de warnings"""
        return self.warnings
    
    def get_errors(self) -> List[str]:
        """Retorna lista de erros"""
        return self.errors
    
    def clear(self):
        """Limpa warnings e errors"""
        self.warnings.clear()
        self.errors.clear()

# Instância global
type_inferrer = TypeInferrer()

