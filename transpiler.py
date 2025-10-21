from parser import parser

def traduzir_ast(node, indent=1, in_class=False):
    """Traduz um nó da AST para código C++ com a indentação apropriada."""
    ind = "    " * indent
    
    if isinstance(node, list):
        codigo = ""
        for n in node:
            codigo += traduzir_ast(n, indent, in_class) + "\n"
        return codigo
    elif isinstance(node, tuple):
        op = node[0]
        
        if op == 'assign':
            valor = node[2]
            if isinstance(valor, tuple) and valor[0] == 'list':
                elementos = valor[1]
                if elementos:
                    elementos_str = ", ".join([traduzir_ast(elem, 0, in_class) for elem in elementos])
                    return f"{ind}std::vector<int> {node[1]} = {{{elementos_str}}};"
                else:
                    return f"{ind}std::vector<int> {node[1]};"
            elif isinstance(valor, tuple) and valor[0] == 'func_call' and node[2][1] in ['int', 'float', 'str']:
                # Conversão de tipo
                tipo_cpp = {'int': 'int', 'float': 'float', 'str': 'string'}[node[2][1]]
                arg = traduzir_ast(node[2][2][0], 0, in_class)
                return f"{ind}{tipo_cpp} {node[1]} = {node[2][1]}({arg});"
            elif isinstance(valor, str):
                return f'{ind}std::string {node[1]} = "{valor}";'
            elif isinstance(valor, float):
                return f"{ind}float {node[1]} = {valor};"
            elif isinstance(valor, int):
                return f"{ind}int {node[1]} = {valor};"
            elif isinstance(valor, bool):
                return f"{ind}bool {node[1]} = {'true' if valor else 'false'};"
            else:
                expr = traduzir_ast(valor, 0, in_class)
                return f"{ind}auto {node[1]} = {expr};"

        elif op == 'compound_assign':
            var = node[1]
            op_symbol = node[2]
            expr = traduzir_ast(node[3], 0, in_class)
            return f"{ind}{var} {op_symbol} {expr};"

        elif op in ['post_increment', 'pre_increment']:
            var = node[1] if op == 'post_increment' else node[2]
            op_symbol = node[2] if op == 'post_increment' else node[1]
            if op == 'post_increment':
                return f"{ind}{var}{op_symbol};"
            else:
                return f"{ind}{op_symbol}{var};"

        elif op == 'class_def':
            class_name = node[1]
            parent = node[2]
            body = node[3]
            
            # Herança
            inheritance = f" : public {parent}" if parent else ""
            
            codigo = f"class {class_name}{inheritance} {{\n"
            codigo += "public:\n"
            
            # Processa métodos e atributos
            for item in body:
                if isinstance(item, tuple) and item[0] == 'method_def':
                    method_name = item[1]
                    params = item[2]
                    method_body = item[3]
                    
                    # Construtor especial
                    if method_name == '__init__':
                        if params:
                            params_str = ", ".join([f"auto {p}" for p in params])
                        else:
                            params_str = ""
                        method_code = traduzir_ast(method_body, 2, True)
                        codigo += f"    {class_name}({params_str}) {{\n{method_code}    }}\n\n"
                    else:
                        # Método normal
                        if params:
                            params_str = ", ".join([f"auto {p}" for p in params])
                        else:
                            params_str = ""
                        method_code = traduzir_ast(method_body, 2, True)
                        codigo += f"    auto {method_name}({params_str}) {{\n{method_code}    }}\n\n"
            
            codigo += "};\n"
            return codigo

        elif op == 'attr_assign':
            obj = node[1]
            attr = node[2]
            valor = traduzir_ast(node[3], 0, in_class)
            if in_class and obj == 'self':
                return f"{ind}this->{attr} = {valor};"
            else:
                return f"{ind}{obj}.{attr} = {valor};"

        elif op == 'attr_access':
            obj = node[1]
            attr = node[2]
            if in_class and obj == 'self':
                return f"this->{attr}"
            else:
                return f"{obj}.{attr}"

        elif op == 'method_call':
            obj = node[1]
            method = node[2]
            args = node[3]
            
            if args:
                args_str = ", ".join([traduzir_ast(arg, 0, in_class) for arg in args])
            else:
                args_str = ""
            
            if in_class and obj == 'self':
                return f"this->{method}({args_str})"
            elif obj in ['append', 'push_back'] and method == 'append':
                return f"{ind}{obj}.push_back({args_str});"
            else:
                return f"{obj}.{method}({args_str})"

        elif op == 'ternary':
            condition = traduzir_ast(node[1], 0, in_class)
            true_val = traduzir_ast(node[2], 0, in_class)
            false_val = traduzir_ast(node[3], 0, in_class)
            return f"({condition} ? {true_val} : {false_val})"

        elif op == 'try':
            try_block = traduzir_ast(node[1], indent+1, in_class)
            except_clauses = node[2]
            finally_block = node[3]
            
            codigo = f"{ind}try {{\n{try_block}{ind}}}"
            
            for clause in except_clauses:
                except_body = traduzir_ast(clause[-1], indent+1, in_class)
                codigo += f" catch(...) {{\n{except_body}{ind}}}"
            
            if finally_block:
                # C++ não tem finally, mas podemos simular
                finally_code = traduzir_ast(finally_block, indent+1, in_class)
                codigo = f"{ind}{{\n{codigo}\n{finally_code}{ind}}}"
            
            return codigo

        elif op == 'raise':
            if node[1]:
                expr = traduzir_ast(node[1], 0, in_class)
                return f"{ind}throw std::runtime_error({expr});"
            else:
                return f"{ind}throw std::runtime_error(\"Exception raised\");"

        elif op == 'break':
            return f"{ind}break;"

        elif op == 'continue':
            return f"{ind}continue;"

        elif op in ['+', '-', '*', '/']:
            return f"({traduzir_ast(node[1], 0, in_class)} {op} {traduzir_ast(node[2], 0, in_class)})"
        
        elif op in ['>', '<', '==', '!=', '>=', '<=']:
            return f"({traduzir_ast(node[1], 0, in_class)} {op} {traduzir_ast(node[2], 0, in_class)})"
        
        elif op == 'and':
            return f"({traduzir_ast(node[1], 0, in_class)} && {traduzir_ast(node[2], 0, in_class)})"
        elif op == 'or':
            return f"({traduzir_ast(node[1], 0, in_class)} || {traduzir_ast(node[2], 0, in_class)})"
        elif op == 'not':
            return f"(!{traduzir_ast(node[1], 0, in_class)})"

        elif op == 'in':
            item = traduzir_ast(node[1], 0, in_class)
            container = traduzir_ast(node[2], 0, in_class)
            return f"(std::find({container}.begin(), {container}.end(), {item}) != {container}.end())"

        elif op == 'list':
            elementos = node[1]
            if elementos:
                elementos_str = ", ".join([traduzir_ast(elem, 0, in_class) for elem in elementos])
                return f"{{{elementos_str}}}"
            else:
                return "{}"

        elif op == 'list_index':
            lista = node[1]
            indice = traduzir_ast(node[2], 0, in_class)
            return f"{lista}[{indice}]"

        # Funções built-in
        elif op in ['len', 'sum', 'max', 'min']:
            objeto = traduzir_ast(node[1], 0, in_class)
            if op == 'len':
                return f"{objeto}.size()"
            elif op == 'sum':
                return f"std::accumulate({objeto}.begin(), {objeto}.end(), 0)"
            elif op == 'max':
                return f"*std::max_element({objeto}.begin(), {objeto}.end())"
            elif op == 'min':
                return f"*std::min_element({objeto}.begin(), {objeto}.end())"

        elif op in ['type', 'str', 'int', 'float']:
            expr = traduzir_ast(node[1], 0, in_class)
            if op == 'type':
                return f"typeid({expr}).name()"
            elif op == 'str':
                return f"std::to_string({expr})"
            elif op == 'int':
                return f"static_cast<int>({expr})"
            elif op == 'float':
                return f"static_cast<float>({expr})"

        elif op == 'range':
            if len(node) == 2:
                fim = traduzir_ast(node[1], 0, in_class)
                return f"range_vector(0, {fim})"
            elif len(node) == 3:
                inicio = traduzir_ast(node[1], 0, in_class)
                fim = traduzir_ast(node[2], 0, in_class)
                return f"range_vector({inicio}, {fim})"
            else:
                inicio = traduzir_ast(node[1], 0, in_class)
                fim = traduzir_ast(node[2], 0, in_class)
                passo = traduzir_ast(node[3], 0, in_class)
                return f"range_vector({inicio}, {fim}, {passo})"

        elif op == 'if':
            cond = traduzir_ast(node[1], 0, in_class)
            bloco = traduzir_ast(node[2], indent+1, in_class)
            return f"{ind}if ({cond}) {{\n{bloco}{ind}}}"
        elif op == 'if-else':
            cond = traduzir_ast(node[1], 0, in_class)
            bloco_if = traduzir_ast(node[2], indent+1, in_class)
            bloco_else = traduzir_ast(node[3], indent+1, in_class)
            return f"{ind}if ({cond}) {{\n{bloco_if}{ind}}} else {{\n{bloco_else}{ind}}}"
        elif op == 'while':
            cond = traduzir_ast(node[1], 0, in_class)
            bloco = traduzir_ast(node[2], indent+1, in_class)
            return f"{ind}while ({cond}) {{\n{bloco}{ind}}}"
        elif op == 'for':
            init = traduzir_ast(node[1], 0, in_class)
            cond = traduzir_ast(node[2], 0, in_class)
            update = traduzir_ast(node[3], 0, in_class)
            bloco = traduzir_ast(node[4], indent+1, in_class)
            return f"{ind}for ({init} {cond}; {update}) {{\n{bloco}{ind}}}"

        elif op == 'print':
            argumentos = node[1]
            if argumentos:
                prints = []
                for i, arg in enumerate(argumentos):
                    if i > 0:
                        prints.append(f'{ind}std::cout << " ";')
                    expr = traduzir_ast(arg, 0, in_class)
                    prints.append(f'{ind}std::cout << {expr};')
                prints.append(f'{ind}std::cout << std::endl;')
                return '\n'.join(prints)
            else:
                return f'{ind}std::cout << std::endl;'

        elif op == 'func_def':
            nome = node[1]
            parametros = node[2]
            corpo = node[3]
            if parametros:
                params_str = ", ".join([f"auto {p}" for p in parametros])
            else:
                params_str = ""
            corpo_str = traduzir_ast(corpo, indent+1, in_class)
            return f"auto {nome}({params_str}) {{\n{corpo_str}{'    ' * indent}}}\n"
        elif op == 'return':
            if node[1]:
                return f"{ind}return {traduzir_ast(node[1], 0, in_class)};"
            else:
                return f"{ind}return;"
        elif op == 'func_call':
            nome = node[1]
            argumentos = node[2]
            if argumentos:
                args_str = ", ".join([traduzir_ast(arg, 0, in_class) for arg in argumentos])
            else:
                args_str = ""
            return f"{nome}({args_str})"
        elif op == 'var':
            return node[1]
        else:
            return f"{ind}// Operação desconhecida: {op}"
    else:
        if isinstance(node, bool):
            return "true" if node else "false"
        elif isinstance(node, str):
            return f'"{node}"'
        elif node is None:
            return "nullptr"
        else:
            return str(node)

def gerar_codigo_cpp(ast):
    """Gera o código C++ completo."""
    classes_code = ""
    functions_code = ""
    main_code = ""
    
    for stmt in ast:
        if isinstance(stmt, tuple):
            if stmt[0] == 'class_def':
                classes_code += traduzir_ast(stmt, indent=0) + "\n"
            elif stmt[0] == 'func_def':
                functions_code += traduzir_ast(stmt, indent=0) + "\n"
            else:
                main_code += traduzir_ast(stmt, indent=1) + "\n"
        else:
            main_code += traduzir_ast(stmt, indent=1) + "\n"
    
    # Headers e utilitários
    codigo = """#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <numeric>
#include <stdexcept>
#include <typeinfo>

// Função auxiliar para range
std::vector<int> range_vector(int start, int stop, int step = 1) {
    std::vector<int> result;
    if (step > 0) {
        for (int i = start; i < stop; i += step) {
            result.push_back(i);
        }
    } else if (step < 0) {
        for (int i = start; i > stop; i += step) {
            result.push_back(i);
        }
    }
    return result;
}

"""
    
    codigo += classes_code + "\n"
    codigo += functions_code + "\n"
    codigo += "int main() {\n    try {\n" + main_code + "    } catch(const std::exception& e) {\n        std::cout << \"Erro: \" << e.what() << std::endl;\n    }\n    return 0;\n}\n"
    return codigo

def compilar_codigo(codigo, output_file="output.cpp"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(codigo)
    print(f"Código C++ gerado salvo em {output_file}")

def main():
    import sys
    if len(sys.argv) != 2:
        print("Uso: python transpiler.py <arquivo.gpu>")
        sys.exit(1)
    arquivo = sys.argv[1]
    with open(arquivo, "r", encoding="utf-8") as f:
        codigo_moonlight = f.read()
    ast = parser.parse(codigo_moonlight)
    codigo_cpp = gerar_codigo_cpp(ast)
    compilar_codigo(codigo_cpp)

if __name__ == "__main__":
    main()