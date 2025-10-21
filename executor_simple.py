from parser import parser
import time

# Dicionário global para armazenar variáveis
variaveis = {}
classes = {}

# Exceções básicas
class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class MoonlightException(Exception):
    def __init__(self, message):
        self.message = message

# Classe base para objetos
class MoonlightObject:
    def __init__(self, class_name, attributes=None):
        self.class_name = class_name
        self.attributes = attributes or {}
    
    def get_attr(self, name):
        return self.attributes.get(name, None)
    
    def set_attr(self, name, value):
        self.attributes[name] = value

def interpretar(ast):
    if isinstance(ast, list):
        resultado = None
        for node in ast:
            resultado = interpretar(node)
        return resultado

    if isinstance(ast, tuple):
        op = ast[0]

        # ASSIGNMENTS
        if op == 'assign':
            variaveis[ast[1]] = interpretar(ast[2])

        elif op == 'list_assign':
            lista_nome = ast[1]
            indice = interpretar(ast[2])
            valor = interpretar(ast[3])
            if lista_nome in variaveis and isinstance(variaveis[lista_nome], (list, dict)):
                variaveis[lista_nome][indice] = valor

        elif op == 'attr_assign':
            obj_name = ast[1]
            attr_name = ast[2]
            valor = interpretar(ast[3])
            if obj_name in variaveis and isinstance(variaveis[obj_name], MoonlightObject):
                variaveis[obj_name].set_attr(attr_name, valor)

        elif op == 'compound_assign':
            var_name = ast[1]
            operator = ast[2]
            valor = interpretar(ast[3])
            if var_name in variaveis:
                atual = variaveis[var_name]
                ops = {
                    '+=': lambda a, b: a + b,
                    '-=': lambda a, b: a - b,
                    '*=': lambda a, b: a * b,
                    '/=': lambda a, b: a / b,
                    '%=': lambda a, b: a % b,
                    '**=': lambda a, b: a ** b
                }
                if operator in ops:
                    variaveis[var_name] = ops[operator](atual, valor)

        elif op in ['post_increment', 'pre_increment']:
            var_name = ast[1] if op == 'post_increment' else ast[2]
            operator = ast[2] if op == 'post_increment' else ast[1]
            if var_name in variaveis:
                atual = variaveis[var_name]
                if operator == '++':
                    variaveis[var_name] = atual + 1
                    return atual if op == 'post_increment' else atual + 1
                elif operator == '--':
                    variaveis[var_name] = atual - 1
                    return atual if op == 'post_increment' else atual - 1

        # DECORADORES SIMPLES
        elif op == 'decorated_func_def':
            decorator_list = ast[1]
            func_name = ast[2]
            params = ast[3]
            body = ast[4]
            
            func = ('function', params, body)
            
            # Aplica decoradores simples
            for decorator in decorator_list:
                dec_name = decorator[1]
                if dec_name == 'jit':
                    func = ('jit_function', params, body)
            
            variaveis[func_name] = func

        # CLASSES
        elif op == 'class_def':
            class_name = ast[1]
            parents = ast[2] if ast[2] else []
            body = ast[3]
            
            if isinstance(parents, str):
                parents = [parents]
            elif parents is None:
                parents = []
            
            class_context = {}
            
            for item in body:
                if isinstance(item, tuple) and item[0] == 'method_def':
                    class_context[item[1]] = ('method', item[2], item[3])
            
            classes[class_name] = {
                'parents': parents,
                'methods': class_context,
                'attributes': {}
            }

        # OPERADORES ARITMÉTICOS
        elif op in ['+', '-', '*', '/', '%', 'power', '**']:
            val_esq = interpretar(ast[1])
            val_dir = interpretar(ast[2])
            if op == '+':
                return val_esq + val_dir
            elif op == '-':
                return val_esq - val_dir
            elif op == '*':
                return val_esq * val_dir
            elif op == '/':
                return val_esq / val_dir
            elif op == '%':
                return val_esq % val_dir
            elif op in ['power', '**']:
                return val_esq ** val_dir

        elif op in ['>', '<', '==', '!=', '>=', '<=']:
            val_esq = interpretar(ast[1])
            val_dir = interpretar(ast[2])
            ops = {
                '>': lambda a, b: a > b,
                '<': lambda a, b: a < b,
                '==': lambda a, b: a == b,
                '!=': lambda a, b: a != b,
                '>=': lambda a, b: a >= b,
                '<=': lambda a, b: a <= b
            }
            return ops[op](val_esq, val_dir)

        elif op == 'and':
            return interpretar(ast[1]) and interpretar(ast[2])

        elif op == 'or':
            return interpretar(ast[1]) or interpretar(ast[2])

        elif op == 'not':
            return not interpretar(ast[1])

        elif op == 'ternary':
            condition = interpretar(ast[1])
            if condition:
                return interpretar(ast[2])
            else:
                return interpretar(ast[3])

        # ESTRUTURAS DE DADOS
        elif op == 'list':
            elementos = ast[1]
            if elementos:
                return [interpretar(elem) for elem in elementos]
            else:
                return []

        elif op == 'dict':
            elementos = ast[1]
            result = {}
            for key_expr, value_expr in elementos:
                key = interpretar(key_expr)
                value = interpretar(value_expr)
                result[key] = value
            return result

        elif op == 'tuple':
            elementos = ast[1]
            if elementos:
                return tuple(interpretar(elem) for elem in elementos)
            else:
                return tuple()

        elif op == 'list_index':
            obj_name = ast[1]
            indice = interpretar(ast[2])
            if obj_name in variaveis:
                obj = variaveis[obj_name]
                if hasattr(obj, '__getitem__'):
                    return obj[indice]

        elif op == 'attr_access':
            obj_name = ast[1]
            attr_name = ast[2]
            if obj_name in variaveis:
                obj = variaveis[obj_name]
                if isinstance(obj, MoonlightObject):
                    return obj.get_attr(attr_name)

        # FUNÇÕES BUILT-IN
        elif op in ['len', 'sum', 'max', 'min', 'type', 'str', 'int', 'float', 'bool']:
            arg = interpretar(ast[1])
            funcs = {
                'len': len,
                'sum': sum,
                'max': max,
                'min': min,
                'type': lambda x: type(x).__name__,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool
            }
            return funcs[op](arg)

        elif op == 'range':
            if len(ast) == 2:
                return list(range(interpretar(ast[1])))
            elif len(ast) == 3:
                return list(range(interpretar(ast[1]), interpretar(ast[2])))
            else:
                return list(range(interpretar(ast[1]), interpretar(ast[2]), interpretar(ast[3])))

        # CONTROLE DE FLUXO
        elif op == 'break':
            raise BreakException()

        elif op == 'continue':
            raise ContinueException()

        elif op == 'if':
            if interpretar(ast[1]):
                return interpretar(ast[2])

        elif op == 'if-else':
            if interpretar(ast[1]):
                return interpretar(ast[2])
            else:
                return interpretar(ast[3])

        elif op == 'while':
            try:
                while interpretar(ast[1]):
                    try:
                        interpretar(ast[2])
                    except ContinueException:
                        continue
                    except BreakException:
                        break
            except BreakException:
                pass

        elif op == 'for':
            try:
                interpretar(ast[1])  # inicialização
                while interpretar(ast[2]):
                    try:
                        interpretar(ast[4])  # corpo
                        interpretar(ast[3])  # atualização
                    except ContinueException:
                        interpretar(ast[3])
                        continue
                    except BreakException:
                        break
            except BreakException:
                pass

        elif op == 'print':
            argumentos = ast[1]
            if argumentos:
                valores = []
                for arg in argumentos:
                    val = interpretar(arg)
                    if isinstance(val, MoonlightObject):
                        valores.append(f"<{val.class_name} object>")
                    else:
                        valores.append(str(val))
                print(' '.join(valores))
            else:
                print()

        elif op == 'func_def':
            func_name = ast[1]
            params = ast[2]
            body = ast[3]
            variaveis[func_name] = ('function', params, body)

        elif op == 'func_call':
            func_name = ast[1]
            args = ast[2]
            
            if func_name in variaveis:
                func = variaveis[func_name]
                
                if isinstance(func, tuple):
                    func_type = func[0]
                    
                    if func_type in ['function', 'jit_function']:
                        params = func[1]
                        body = func[2]
                        
                        if func_type == 'jit_function':
                            start_time = time.time()
                        
                        contexto_anterior = variaveis.copy()
                        
                        if params and args:
                            for i, param in enumerate(params):
                                if i < len(args):
                                    variaveis[param] = interpretar(args[i])
                        
                        resultado = None
                        try:
                            interpretar(body)
                        except ReturnException as e:
                            resultado = e.value
                        
                        variaveis.clear()
                        variaveis.update(contexto_anterior)
                        
                        if func_type == 'jit_function':
                            end_time = time.time()
                            print(f"JIT: {func_name} executado em {end_time - start_time:.4f}s")
                        
                        return resultado
            
            elif func_name in classes:
                class_def = classes[func_name]
                obj = MoonlightObject(func_name)
                
                if '__init__' in class_def['methods']:
                    init_method = class_def['methods']['__init__']
                    params = init_method[1]
                    body = init_method[2]
                    
                    contexto_anterior = variaveis.copy()
                    variaveis['self'] = obj
                    
                    if params and args:
                        for i, param in enumerate(params):
                            if i < len(args):
                                variaveis[param] = interpretar(args[i])
                    
                    try:
                        interpretar(body)
                    except ReturnException:
                        pass
                    
                    variaveis.clear()
                    variaveis.update(contexto_anterior)
                
                return obj

        elif op == 'method_call':
            obj_name = ast[1]
            method_name = ast[2]
            args = ast[3]
            
            if obj_name in variaveis:
                obj = variaveis[obj_name]
                
                if isinstance(obj, MoonlightObject):
                    class_def = classes.get(obj.class_name, {})
                    methods = class_def.get('methods', {})
                    
                    if method_name in methods:
                        method = methods[method_name]
                        params = method[1]
                        body = method[2]
                        
                        contexto_anterior = variaveis.copy()
                        variaveis['self'] = obj
                        
                        if params and args:
                            for i, param in enumerate(params):
                                if i < len(args):
                                    variaveis[param] = interpretar(args[i])
                        
                        resultado = None
                        try:
                            interpretar(body)
                        except ReturnException as e:
                            resultado = e.value
                        
                        variaveis.clear()
                        variaveis.update(contexto_anterior)
                        return resultado
                
                elif isinstance(obj, list) and hasattr(obj, method_name):
                    method = getattr(obj, method_name)
                    if args:
                        arg_values = [interpretar(arg) for arg in args]
                        return method(*arg_values)
                    else:
                        return method()

        elif op == 'return':
            valor = interpretar(ast[1]) if ast[1] else None
            raise ReturnException(valor)

        elif op == 'var':
            nome = ast[1]
            if nome in variaveis:
                return variaveis[nome]
            elif nome in classes:
                return classes[nome]
            else:
                return 0  # Default para variáveis não definidas

        else:
            print(f"Operação não implementada: {op}")

    else:
        return ast

def executar_codigo(codigo):
    try:
        ast = parser.parse(codigo)
        interpretar(ast)
        print("\nEstado final das variáveis:", {k: v for k, v in variaveis.items() if not k.startswith('__')})
    except Exception as e:
        print(f"Erro: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste = """
print("=== TESTE BÁSICO MOONLIGHT ===")

x = 10
y = 20
z = x + y
print("Soma:", z)

numeros = [1, 2, 3, 4, 5]
print("Lista:", numeros)
print("Tamanho:", len(numeros))

class Pessoa {
    def __init__(nome) {
        self.nome = nome
    }
    
    def falar() {
        print("Olá, eu sou", self.nome)
    }
}

p = Pessoa("João")
p.falar()

@jit
def fibonacci(n) {
    if (n <= 1) {
        return n
    }
    return fibonacci(n-1) + fibonacci(n-2)
}

print("Fibonacci(8):", fibonacci(8))

contador = 5
contador += 3
print("Contador:", contador)

print("=== TESTE CONCLUÍDO ===")
"""
    executar_codigo(teste)