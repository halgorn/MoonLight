from parser import parser
import time

# Dicionário global para armazenar variáveis
variaveis = {}
classes = {}

# Import do module loader (lazy para evitar import circular)
_module_loader = None

def get_module_loader():
    global _module_loader
    if _module_loader is None:
        from module_loader import module_loader
        _module_loader = module_loader
    return _module_loader

# Exceções básicas
class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class YieldException(Exception):
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

def tem_yield(ast):
    """Verifica se a AST contém yield"""
    if not ast:
        return False
    if isinstance(ast, tuple) and len(ast) > 0 and ast[0] == 'yield':
        return True
    if isinstance(ast, list):
        return any(tem_yield(item) for item in ast)
    if isinstance(ast, tuple):
        return any(tem_yield(item) for item in ast if isinstance(item, (list, tuple)))
    return False

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
        
        elif op == 'multi_assign':
            # Multiple assignment: x = y = z
            names = ast[1]
            valor = interpretar(ast[2])
            for name in names:
                variaveis[name] = valor
        
        elif op == 'unpack':
            # Unpacking: a, b, c = [1, 2, 3]
            names = ast[1]
            valores = interpretar(ast[2])
            if not hasattr(valores, '__iter__'):
                print(f"Erro: Cannot unpack non-iterable")
                return
            valores_list = list(valores) if not isinstance(valores, list) else valores
            if len(names) != len(valores_list):
                print(f"Erro: Cannot unpack {len(valores_list)} values into {len(names)} variables")
                return
            for i, name in enumerate(names):
                variaveis[name] = valores_list[i]

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

        elif op == 'with':
            # with expr as var { block }: bind var = expr, run block, then remove only var from scope
            expr_val = interpretar(ast[1])
            var_name = ast[2]
            block = ast[3]
            variaveis[var_name] = expr_val
            interpretar(block)
            if var_name in variaveis:
                del variaveis[var_name]

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
                if isinstance(item, tuple) and (item[0] == 'method_def' or item[0] == 'func_def'):
                    # Parser may reduce def inside class as func_def (shift/reduce conflict); treat as method
                    name = item[1]
                    params = item[2]
                    method_body = item[3]
                    class_context[name] = ('method', params, method_body)
            
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
        
        elif op == 'unary':
            operator = ast[1]
            operand = interpretar(ast[2])
            if operator == '-':
                return -operand
            elif operator == '+':
                return +operand
            elif operator == '~':
                return ~operand
            return operand

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

        elif op == 'list_comp':
            # ('list_comp', expr, var, iterable, condition)
            expr, var, iterable_ast, condition = ast[1], ast[2], ast[3], ast[4]
            iterable = interpretar(iterable_ast)
            if not hasattr(iterable, '__iter__') or isinstance(iterable, str):
                iterable = list(iterable) if iterable else []
            result = []
            for item in iterable:
                variaveis[var] = item
                if condition is not None and not interpretar(condition):
                    continue
                result.append(interpretar(expr))
            return result

        elif op == 'dict_comp':
            # ('dict_comp', key_expr, value_expr, var, iterable, condition)
            key_expr, value_expr, var, iterable_ast, condition = ast[1], ast[2], ast[3], ast[4], ast[5]
            iterable = interpretar(iterable_ast)
            if not hasattr(iterable, '__iter__') or isinstance(iterable, str):
                iterable = list(iterable) if iterable else []
            result = {}
            for item in iterable:
                variaveis[var] = item
                if condition is not None and not interpretar(condition):
                    continue
                k, v = interpretar(key_expr), interpretar(value_expr)
                result[k] = v
            return result

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
                # Se é um módulo (dict/namespace)
                if isinstance(obj, dict):
                    return obj.get(attr_name)
                # Se é um objeto
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

        elif op == 'lambda':
            # Lambda: ('lambda', params, body)
            params = ast[1]
            body = ast[2]
            return ('lambda_func', params, body)
        
        elif op == 'func_def':
            func_name = ast[1]
            params = ast[2]
            body = ast[3]
            decorators = ast[4] if len(ast) > 4 else []
            
            # Verificar se tem decorator @jit
            has_jit = False
            if decorators:
                for dec in decorators:
                    if isinstance(dec, tuple) and len(dec) > 1 and dec[1] == 'jit':
                        has_jit = True
                        break
            
            # Verifica se é generator (tem yield)
            is_generator = tem_yield(body)
            
            # Armazenar função com AST para JIT
            func_info = ('function', params, body)
            if has_jit:
                # Marcar função para JIT compilation
                func_info = ('jit_function', params, body, ast)
            
            if is_generator:
                variaveis[func_name] = ('generator', params, body)
            else:
                variaveis[func_name] = func_info

        elif op == 'func_call':
            func_name = ast[1]
            args = ast[2]
            
            if func_name in variaveis:
                func = variaveis[func_name]
                
                if isinstance(func, tuple):
                    func_type = func[0]
                    
                    # Se é generator, retorna um iterador
                    if func_type == 'generator':
                        params = func[1]
                        body = func[2]
                        
                        # Generator iterator que coleta todos os yields
                        def generator_func():
                            contexto_anterior = variaveis.copy()
                            
                            # Define parâmetros
                            if params and args:
                                for i, param in enumerate(params):
                                    if i < len(args):
                                        variaveis[param] = interpretar(args[i])
                            
                            # Executa e coleta yields
                            results = []
                            try:
                                interpretar(body)
                            except YieldException as e:
                                results.append(e.value)
                            except ReturnException:
                                pass
                            finally:
                                variaveis.clear()
                                variaveis.update(contexto_anterior)
                            
                            return results
                        
                        return generator_func()
                    
                    elif func_type in ['function', 'jit_function', 'lambda_func']:
                        params = func[1]
                        body = func[2]
                        func_ast = func[3] if len(func) > 3 and func_type == 'jit_function' else None
                        
                        # Tentar usar JIT se disponível
                        if func_type == 'jit_function':
                            try:
                                from llvm_backend import generate_llvm_for_ast, jit_compiler, LLVM_AVAILABLE
                                
                                if LLVM_AVAILABLE and jit_compiler and func_ast:
                                    # Gerar LLVM IR
                                    llvm_ir = generate_llvm_for_ast(func_ast)
                                    
                                    if llvm_ir:
                                        # Compilar função
                                        func_ptr = jit_compiler.compile_function(llvm_ir, func_name)
                                        
                                        if func_ptr:
                                            # Interpretar argumentos
                                            interpreted_args = []
                                            for arg in args:
                                                interpreted_args.append(interpretar(arg))
                                            
                                            # Executar função compilada
                                            resultado = jit_compiler.execute_jit(func_name, *interpreted_args)
                                            
                                            if resultado is not None:
                                                return resultado
                            except Exception as e:
                                # Fallback para interpretador se JIT falhar
                                pass
                        
                        # Executar no interpretador (fallback ou função normal)
                        contexto_anterior = variaveis.copy()
                        
                        if params and args:
                            for i, param in enumerate(params):
                                if i < len(args):
                                    variaveis[param] = interpretar(args[i])
                        
                        resultado = None
                        try:
                            if func_type == 'lambda_func':
                                # Lambda retorna diretamente a expressão
                                resultado = interpretar(body)
                            else:
                                interpretar(body)
                        except ReturnException as e:
                            resultado = e.value
                        
                        variaveis.clear()
                        variaveis.update(contexto_anterior)
                        
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
            valor = interpretar(ast[1]) if len(ast) > 1 else None
            raise ReturnException(valor)
        
        elif op == 'yield':
            # Yield: Implementação básica de generator
            valor = interpretar(ast[1]) if len(ast) > 1 else None
            raise YieldException(valor)

        elif op == 'import':
            # Import: ('import', module_name, alias)
            module_name = ast[1]
            alias = ast[2] if len(ast) > 2 and ast[2] else module_name
            
            loader = get_module_loader()
            try:
                module_namespace = loader.import_module(module_name)
                variaveis[alias] = module_namespace
            except ImportError as e:
                print(f"Erro ao importar '{module_name}': {e}")
        
        elif op == 'from_import':
            # From Import: ('from_import', module_name, item_name, alias)
            module_name = ast[1]
            item_name = ast[2]
            alias = ast[3] if len(ast) > 3 and ast[3] else item_name
            
            loader = get_module_loader()
            try:
                imports = loader.import_from(module_name, [item_name])
                variaveis[alias] = imports.get(item_name)
            except ImportError as e:
                print(f"Erro ao importar '{item_name}' de '{module_name}': {e}")
        
        elif op == 'from_import_all':
            # From Import All: ('from_import_all', module_name)
            module_name = ast[1]
            
            loader = get_module_loader()
            try:
                imports = loader.import_from(module_name, ['*'])
                variaveis.update(imports)
            except ImportError as e:
                print(f"Erro ao importar tudo de '{module_name}': {e}")
        
        elif op == 'with':
            # With statement (context manager): ('with', context_expr, var_name, body)
            context_expr = interpretar(ast[1])
            var_name = ast[2]
            body = ast[3]
            
            # Implementação básica - sem __enter__/__exit__
            if var_name:
                variaveis[var_name] = context_expr
            
            try:
                interpretar(body)
            finally:
                # Cleanup básico
                if var_name and var_name in variaveis:
                    del variaveis[var_name]
        
        elif op == 'var':
            nome = ast[1]
            if nome in variaveis:
                valor = variaveis[nome]
                # Se for um dict (namespace de módulo), retorna ele mesmo
                if isinstance(valor, dict):
                    return valor
                return valor
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