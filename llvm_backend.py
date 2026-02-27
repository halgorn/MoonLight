"""Backend LLVM IR para MoonLight
Gera código LLVM IR e compila JIT para performance máxima
"""

try:
    from llvmlite import ir, binding
    LLVM_AVAILABLE = True
except ImportError:
    LLVM_AVAILABLE = False
    print("Warning: llvmlite não instalado. JIT compilation desabilitada.")
    print("Instale com: pip install llvmlite")

class LLVMCodeGen:
    """Gerador de código LLVM IR"""
    
    def __init__(self):
        if not LLVM_AVAILABLE:
            return
        
        # Inicializar LLVM
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()
        
        # Criar módulo
        self.module = ir.Module(name="moonlight_module")
        
        # Builder para instruções
        self.builder = None
        
        # Tabela de símbolos (variáveis)
        self.variables = {}
        
        # Função atual
        self.current_function = None
    
    def create_function(self, name, return_type=ir.IntType(32), param_types=[]):
        """Cria uma função LLVM"""
        if not LLVM_AVAILABLE:
            return None
        
        # Tipo da função
        func_type = ir.FunctionType(return_type, param_types)
        
        # Criar função
        func = ir.Function(self.module, func_type, name=name)
        
        # Criar bloco de entrada
        block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        
        self.current_function = func
        return func
    
    def generate_constant(self, value, typ=ir.IntType(32)):
        """Gera constante"""
        if isinstance(typ, ir.IntType):
            return ir.Constant(typ, int(value))
        elif isinstance(typ, ir.DoubleType):
            return ir.Constant(typ, float(value))
        return None
    
    def generate_add(self, left, right):
        """Gera adição"""
        if isinstance(left.type, ir.IntType):
            return self.builder.add(left, right, name="add_tmp")
        else:
            return self.builder.fadd(left, right, name="fadd_tmp")
    
    def generate_sub(self, left, right):
        """Gera subtração"""
        if isinstance(left.type, ir.IntType):
            return self.builder.sub(left, right, name="sub_tmp")
        else:
            return self.builder.fsub(left, right, name="fsub_tmp")
    
    def generate_mul(self, left, right):
        """Gera multiplicação"""
        if isinstance(left.type, ir.IntType):
            return self.builder.mul(left, right, name="mul_tmp")
        else:
            return self.builder.fmul(left, right, name="fmul_tmp")
    
    def generate_div(self, left, right):
        """Gera divisão"""
        if isinstance(left.type, ir.IntType):
            return self.builder.sdiv(left, right, name="div_tmp")
        else:
            return self.builder.fdiv(left, right, name="fdiv_tmp")
    
    def generate_return(self, value):
        """Gera return"""
        self.builder.ret(value)
    
    def generate_alloca(self, name, typ=ir.IntType(32)):
        """Aloca variável local"""
        alloca = self.builder.alloca(typ, name=name)
        self.variables[name] = alloca
        return alloca
    
    def generate_store(self, value, ptr):
        """Armazena valor em ponteiro"""
        self.builder.store(value, ptr)
    
    def generate_load(self, ptr, name="load_tmp"):
        """Carrega valor de ponteiro"""
        return self.builder.load(ptr, name=name)
    
    def get_llvm_ir(self):
        """Retorna código LLVM IR como string"""
        return str(self.module)
    
    def optimize(self):
        """Aplica otimizações LLVM"""
        if not LLVM_AVAILABLE:
            return
        
        # Parse módulo
        llvm_module = binding.parse_assembly(str(self.module))
        
        # Criar pass manager
        pmb = binding.PassManagerBuilder()
        pmb.opt_level = 2  # O2 optimization
        
        # Aplicar passes de otimização
        pm = binding.ModulePassManager()
        pmb.populate(pm)
        
        pm.run(llvm_module)
        
        return llvm_module

class JITCompiler:
    """Compilador JIT usando LLVM"""
    
    def __init__(self):
        if not LLVM_AVAILABLE:
            self.enabled = False
            return
        
        self.enabled = True
        
        # Target machine
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        
        # Execution engine
        self.execution_engine = None
        
        # Cache de funções compiladas
        self.compiled_functions = {}
    
    def compile_function(self, llvm_ir, func_name):
        """Compila função LLVM IR para código nativo"""
        if not self.enabled:
            return None
        
        try:
            # Parse LLVM IR
            llvm_module = binding.parse_assembly(llvm_ir)
            llvm_module.verify()
            
            # Criar execution engine
            target_machine = binding.Target.from_default_triple().create_target_machine()
            backing_mod = binding.parse_assembly("")
            engine = binding.create_mcjit_compiler(backing_mod, target_machine)
            
            # Adicionar módulo
            engine.add_module(llvm_module)
            engine.finalize_object()
            
            # Obter ponteiro da função
            func_ptr = engine.get_function_address(func_name)
            
            # Cache
            self.compiled_functions[func_name] = {
                'ptr': func_ptr,
                'engine': engine
            }
            
            return func_ptr
            
        except Exception as e:
            print(f"Erro ao compilar função JIT: {e}")
            return None
    
    def execute_jit(self, func_name, *args):
        """Executa função compilada JIT usando ctypes"""
        if func_name not in self.compiled_functions:
            return None
        
        import ctypes
        
        func_info = self.compiled_functions[func_name]
        func_ptr = func_info['ptr']
        
        if func_ptr == 0:
            return None
        
        # Criar função ctypes baseada nos tipos dos argumentos
        # Por enquanto, assumir que todos são int32
        arg_types = []
        for arg in args:
            if isinstance(arg, int):
                arg_types.append(ctypes.c_int32)
            elif isinstance(arg, float):
                arg_types.append(ctypes.c_double)
            else:
                arg_types.append(ctypes.c_int32)  # Default
        
        # Criar função
        func_type = ctypes.CFUNCTYPE(ctypes.c_int32, *arg_types)
        c_func = func_type(func_ptr)
        
        # Chamar função
        try:
            result = c_func(*args)
            return result
        except Exception as e:
            print(f"Erro ao executar função JIT {func_name}: {e}")
            return None

# Instâncias globais
llvm_codegen = LLVMCodeGen() if LLVM_AVAILABLE else None
jit_compiler = JITCompiler() if LLVM_AVAILABLE else None

def translate_ast_to_llvm(ast_node, codegen, func_name, params, return_type=None):
    """
    Traduz um nó da AST MoonLight para LLVM IR
    
    Args:
        ast_node: Nó da AST (pode ser lista, tupla, ou valor primitivo)
        codegen: Instância de LLVMCodeGen
        func_name: Nome da função
        params: Lista de parâmetros da função
        return_type: Tipo de retorno (None = inferir)
    """
    if not LLVM_AVAILABLE or codegen is None:
        return None
    
    if isinstance(ast_node, list):
        # Lista de statements
        for stmt in ast_node:
            translate_ast_to_llvm(stmt, codegen, func_name, params, return_type)
        return None
    
    if not isinstance(ast_node, tuple):
        # Valor primitivo (int, float, string)
        if isinstance(ast_node, int):
            return codegen.generate_constant(ast_node, ir.IntType(32))
        elif isinstance(ast_node, float):
            return codegen.generate_constant(ast_node, ir.DoubleType())
        elif isinstance(ast_node, bool):
            return codegen.generate_constant(1 if ast_node else 0, ir.IntType(1))
        return None
    
    op = ast_node[0]
    
    if op == 'assign':
        # x = value
        var_name = ast_node[1]
        value = ast_node[2]
        
        # Traduzir valor
        value_llvm = translate_ast_to_llvm(value, codegen, func_name, params, return_type)
        
        if value_llvm is None:
            return None
        
        # Alocar variável se não existir
        if var_name not in codegen.variables:
            var_type = value_llvm.type
            codegen.generate_alloca(var_name, var_type)
        
        # Armazenar valor
        var_ptr = codegen.variables[var_name]
        codegen.generate_store(value_llvm, var_ptr)
        return None
    
    elif op == 'return':
        # return value
        if len(ast_node) > 1:
            value = translate_ast_to_llvm(ast_node[1], codegen, func_name, params, return_type)
            if value is not None:
                codegen.generate_return(value)
            else:
                # Return void
                codegen.builder.ret_void()
        else:
            codegen.builder.ret_void()
        return None
    
    elif op in ['add', 'sub', 'mul', 'div', '+', '-', '*', '/']:
        # Operações aritméticas: (op, left, right); parser pode emitir '+' ou 'add'
        op_map = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div'}
        op = op_map.get(op, op)
        left = translate_ast_to_llvm(ast_node[1], codegen, func_name, params, return_type)
        right = translate_ast_to_llvm(ast_node[2], codegen, func_name, params, return_type)
        
        if left is None or right is None:
            return None
        
        if op == 'add':
            return codegen.generate_add(left, right)
        elif op == 'sub':
            return codegen.generate_sub(left, right)
        elif op == 'mul':
            return codegen.generate_mul(left, right)
        elif op == 'div':
            return codegen.generate_div(left, right)
    
    elif op == 'if':
        # if (condition) { then_body } [else { else_body }]
        condition = translate_ast_to_llvm(ast_node[1], codegen, func_name, params, return_type)
        then_body = ast_node[2]
        else_body = ast_node[3] if len(ast_node) > 3 else None
        
        if condition is None:
            return None
        
        # Criar blocos
        then_block = codegen.current_function.append_basic_block("then")
        merge_block = codegen.current_function.append_basic_block("merge")
        
        if else_body:
            else_block = codegen.current_function.append_basic_block("else")
        else:
            else_block = merge_block
        
        # Branch baseado na condição
        codegen.builder.cbranch(condition, then_block, else_block)
        
        # Then block
        codegen.builder.position_at_end(then_block)
        translate_ast_to_llvm(then_body, codegen, func_name, params, return_type)
        codegen.builder.branch(merge_block)
        
        # Else block (se existir)
        if else_body:
            codegen.builder.position_at_end(else_block)
            translate_ast_to_llvm(else_body, codegen, func_name, params, return_type)
            codegen.builder.branch(merge_block)
        
        # Merge block
        codegen.builder.position_at_end(merge_block)
        return None
    
    elif op == 'for':
        # for (init; condition; update) { body }
        # AST: ('for', init_stmt, condition_expr, update_stmt, body)
        init_stmt = ast_node[1]
        condition = ast_node[2]
        update_stmt = ast_node[3]
        body = ast_node[4]
        
        # Criar blocos: entry, loop, body_block, continue_block, exit
        entry_block = codegen.builder.block
        loop_block = codegen.current_function.append_basic_block("loop")
        body_block = codegen.current_function.append_basic_block("loop_body")
        continue_block = codegen.current_function.append_basic_block("loop_continue")
        exit_block = codegen.current_function.append_basic_block("loop_exit")
        
        # Executar init no bloco atual
        if init_stmt:
            translate_ast_to_llvm(init_stmt, codegen, func_name, params, return_type)
        
        # Branch para loop block
        codegen.builder.branch(loop_block)
        
        # Loop block: verificar condição
        codegen.builder.position_at_end(loop_block)
        condition_value = translate_ast_to_llvm(condition, codegen, func_name, params, return_type)
        
        if condition_value is None:
            # Se não conseguir traduzir condição, pular loop
            codegen.builder.branch(exit_block)
        else:
            # Branch baseado na condição
            codegen.builder.cbranch(condition_value, body_block, exit_block)
        
        # Body block: executar corpo do loop
        codegen.builder.position_at_end(body_block)
        translate_ast_to_llvm(body, codegen, func_name, params, return_type)
        
        # Verificar se há terminator (break/return)
        if codegen.builder.block.terminator is None:
            # Se não há terminator, ir para continue block
            codegen.builder.branch(continue_block)
        
        # Continue block: executar update e voltar para loop
        codegen.builder.position_at_end(continue_block)
        if update_stmt:
            translate_ast_to_llvm(update_stmt, codegen, func_name, params, return_type)
        codegen.builder.branch(loop_block)
        
        # Exit block: continuação após o loop
        codegen.builder.position_at_end(exit_block)
        return None
    
    elif op == 'while':
        # while (condition) { body }
        # AST: ('while', condition_expr, body)
        condition = ast_node[1]
        body = ast_node[2]
        
        # Criar blocos: entry, loop, body_block, exit
        entry_block = codegen.builder.block
        loop_block = codegen.current_function.append_basic_block("while_loop")
        body_block = codegen.current_function.append_basic_block("while_body")
        exit_block = codegen.current_function.append_basic_block("while_exit")
        
        # Branch para loop block
        codegen.builder.branch(loop_block)
        
        # Loop block: verificar condição
        codegen.builder.position_at_end(loop_block)
        condition_value = translate_ast_to_llvm(condition, codegen, func_name, params, return_type)
        
        if condition_value is None:
            # Se não conseguir traduzir condição, pular loop
            codegen.builder.branch(exit_block)
        else:
            # Branch baseado na condição
            codegen.builder.cbranch(condition_value, body_block, exit_block)
        
        # Body block: executar corpo do loop
        codegen.builder.position_at_end(body_block)
        translate_ast_to_llvm(body, codegen, func_name, params, return_type)
        
        # Verificar se há terminator (break/return)
        if codegen.builder.block.terminator is None:
            # Se não há terminator, voltar para loop
            codegen.builder.branch(loop_block)
        
        # Exit block: continuação após o loop
        codegen.builder.position_at_end(exit_block)
        return None
    
    elif op == 'break':
        # break statement
        # Precisa encontrar o bloco de saída do loop mais próximo
        # Por enquanto, apenas adicionar um branch para um bloco de saída
        # (Isso requer contexto de loops, que será implementado depois)
        # Por enquanto, retornar None (será tratado pelo contexto do loop)
        return None
    
    elif op == 'continue':
        # continue statement
        # Similar ao break, precisa de contexto de loops
        return None
    
    elif op == 'func_call':
        # function_name(args)
        # Por enquanto, apenas suporta funções built-in simples
        func_name_call = ast_node[1]
        args = ast_node[2] if len(ast_node) > 2 else []
        
        # Traduzir argumentos
        llvm_args = []
        for arg in args:
            arg_llvm = translate_ast_to_llvm(arg, codegen, func_name, params, return_type)
            if arg_llvm is not None:
                llvm_args.append(arg_llvm)
        
        # Por enquanto, retornar None (funções externas não implementadas ainda)
        return None
    
    elif op == 'number':
        # Literal numérico
        value = ast_node[1]
        if isinstance(value, int):
            return codegen.generate_constant(value, ir.IntType(32))
        elif isinstance(value, float):
            return codegen.generate_constant(value, ir.DoubleType())
    
    elif op in ('identifier', 'var'):
        # Variável ou parâmetro (parser emite 'var' para IDENTIFIER)
        var_name = ast_node[1]
        
        # Verificar se é parâmetro
        if codegen.current_function:
            for i, param in enumerate(codegen.current_function.args):
                if param.name == var_name:
                    return param
        
        # Verificar se é variável local
        if var_name in codegen.variables:
            var_ptr = codegen.variables[var_name]
            return codegen.generate_load(var_ptr, var_name)
        
        return None
    
    return None

def generate_llvm_for_ast(func_ast):
    """
    Gera LLVM IR a partir de uma AST MoonLight de função
    
    Args:
        func_ast: Tupla ('func_def', name, params, body, decorators)
    
    Returns:
        String com LLVM IR ou None se falhar
    """
    if not LLVM_AVAILABLE:
        return None
    
    if not isinstance(func_ast, tuple) or func_ast[0] != 'func_def':
        return None
    
    func_name = func_ast[1]
    params_ast = func_ast[2]
    body_ast = func_ast[3]
    
    # Criar codegen
    codegen = LLVMCodeGen()
    
    # Inferir tipos de parâmetros e retorno
    int32 = ir.IntType(32)
    double = ir.DoubleType()
    bool_type = ir.IntType(1)
    param_types = []
    param_names = []
    
    # Inferir tipo de retorno baseado no corpo da função
    inferred_return_type = int32  # Default
    
    # Analisar corpo para inferir tipo de retorno
    if isinstance(body_ast, list):
        for stmt in body_ast:
            if isinstance(stmt, tuple) and stmt[0] == 'return' and len(stmt) > 1:
                ret_value = stmt[1]
                if isinstance(ret_value, int):
                    inferred_return_type = int32
                elif isinstance(ret_value, float):
                    inferred_return_type = double
                elif isinstance(ret_value, bool):
                    inferred_return_type = bool_type
                break
    
    # Usar tipo inferido
    final_return_type = inferred_return_type
    
    for param in params_ast:
        if isinstance(param, str):
            param_names.append(param)
            param_types.append(int32)  # Default: int
        elif isinstance(param, tuple):
            # (type, name) ou (name, type)
            if len(param) == 2:
                param_names.append(param[0] if isinstance(param[0], str) else param[1])
                # Tentar inferir tipo do parâmetro
                if isinstance(param[0], str) and param[0] in ['int', 'float', 'bool']:
                    type_map = {'int': int32, 'float': double, 'bool': bool_type}
                    param_types.append(type_map.get(param[0], int32))
                else:
                    param_types.append(int32)
    
    # Criar função
    func = codegen.create_function(func_name, final_return_type, param_types)
    
    # Nomear parâmetros
    for i, param in enumerate(func.args):
        if i < len(param_names):
            param.name = param_names[i]
    
    # Traduzir corpo da função
    translate_ast_to_llvm(body_ast, codegen, func_name, params_ast, final_return_type)
    
    # Se não há return explícito, adicionar return void
    if codegen.builder.block.terminator is None:
        codegen.builder.ret_void()
    
    return codegen.get_llvm_ir()


def generate_llvm_for_program(program_ast):
    """
    Gera LLVM IR para um programa (lista de statements).
    Inclui todas as funções definidas no top-level (func_def).
    Retorna string do módulo IR ou None se não houver funções ou LLVM indisponível.
    """
    if not LLVM_AVAILABLE or not program_ast:
        return None
    int32 = ir.IntType(32)
    double = ir.DoubleType()
    bool_type = ir.IntType(1)
    codegen = LLVMCodeGen()
    for stmt in program_ast:
        if not isinstance(stmt, tuple) or stmt[0] != 'func_def':
            continue
        func_name = stmt[1]
        params_ast = stmt[2]
        body_ast = stmt[3]
        param_types = []
        param_names = []
        inferred_return_type = int32
        if isinstance(body_ast, list):
            for s in body_ast:
                if isinstance(s, tuple) and s[0] == 'return' and len(s) > 1:
                    r = s[1]
                    if isinstance(r, int):
                        inferred_return_type = int32
                    elif isinstance(r, float):
                        inferred_return_type = double
                    elif isinstance(r, bool):
                        inferred_return_type = bool_type
                    break
        for param in params_ast:
            if isinstance(param, str):
                param_names.append(param)
                param_types.append(int32)
            elif isinstance(param, tuple) and len(param) == 2:
                param_names.append(param[0] if isinstance(param[0], str) else param[1])
                param_types.append(int32)
        func = codegen.create_function(func_name, inferred_return_type, param_types)
        for i, p in enumerate(func.args):
            if i < len(param_names):
                p.name = param_names[i]
        translate_ast_to_llvm(body_ast, codegen, func_name, params_ast, inferred_return_type)
        if codegen.builder.block.terminator is None:
            if inferred_return_type == ir.VoidType():
                codegen.builder.ret_void()
            elif inferred_return_type == double:
                codegen.builder.ret(ir.Constant(double, 0.0))
            else:
                codegen.builder.ret(ir.Constant(inferred_return_type, 0))
    ir_str = codegen.get_llvm_ir()
    return ir_str if ir_str and 'define' in ir_str else None


def generate_assembly_from_ir(llvm_ir):
    """Gera assembly (.s) a partir de LLVM IR."""
    if not LLVM_AVAILABLE:
        return None
    try:
        llvm_module = binding.parse_assembly(llvm_ir)
        llvm_module.verify()
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        assembly = target_machine.emit_assembly(llvm_module)
        return assembly
    except Exception as e:
        print(f"Erro ao gerar assembly: {e}")
        return None


def generate_object_from_ir(llvm_ir, output_file):
    """Gera arquivo objeto (.o) a partir de LLVM IR."""
    if not LLVM_AVAILABLE:
        return False
    try:
        llvm_module = binding.parse_assembly(llvm_ir)
        llvm_module.verify()
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        object_code = target_machine.emit_object(llvm_module)
        with open(output_file, 'wb') as f:
            f.write(bytes(object_code))
        return True
    except Exception as e:
        print(f"Erro ao gerar objeto: {e}")
        return False


# Exemplo de uso
if __name__ == "__main__":
    if LLVM_AVAILABLE:
        print("=== Exemplo de Geração LLVM IR ===\n")
        
        # Criar codegen
        codegen = LLVMCodeGen()
        
        # Criar função: int multiply(int a, int b) { return a * b; }
        int32 = ir.IntType(32)
        func = codegen.create_function("multiply", int32, [int32, int32])
        
        # Parâmetros
        a, b = func.args
        a.name = "a"
        b.name = "b"
        
        # Multiplicação
        result = codegen.generate_mul(a, b)
        
        # Return
        codegen.generate_return(result)
        
        # Imprimir LLVM IR
        print(codegen.get_llvm_ir())
        
        print("\n=== IR Otimizado ===\n")
        optimized = codegen.optimize()
        if optimized:
            print(str(optimized))
    else:
        print("LLVM não disponível. Instale llvmlite:")
        print("pip install llvmlite")









