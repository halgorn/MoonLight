"""Gerador de Código CUDA para MoonLight"""

class CUDACodeGen:
    """Gerador de kernels CUDA e wrappers"""
    
    def __init__(self):
        self.kernels = []
        self.kernel_calls = []
        self.device_arrays = []
        self.device_vars = set()  # Track which variables are on device
        self.gpu_resident_vars = set()  # Track GPU-resident variables (persist across calls)
    
    def generate_kernel(self, func_name, params, body_ast):
        """
        Gera um kernel CUDA a partir de uma função MoonLight
        
        Sintaxe MoonLight:
        cuda kernel def add_vectors(a, b, c, n) {
            i = threadIdx.x + blockIdx.x * blockDim.x
            if (i < n) {
                c[i] = a[i] + b[i]
            }
        }
        """
        kernel_code = f"__global__ void {func_name}("
        
        # Parâmetros do kernel
        param_list = []
        for param in params:
            # Assume arrays de float por padrão
            param_list.append(f"float* {param}")
        
        kernel_code += ", ".join(param_list)
        kernel_code += ") {\n"
        
        # Corpo do kernel
        # Note: Full body translation is handled by transpiler.py
        # This is a simplified template - actual kernel generation
        # uses generate_kernel_from_ast() which properly translates the body
        kernel_code += "    int i = threadIdx.x + blockIdx.x * blockDim.x;\n"
        kernel_code += "    int stride = blockDim.x * gridDim.x;\n"
        kernel_code += "    // Kernel body translation handled by transpiler\n"
        kernel_code += "}\n"
        
        self.kernels.append({
            'name': func_name,
            'code': kernel_code,
            'params': params
        })
        
        return kernel_code
    
    def generate_kernel_launch(self, kernel_name, blocks, threads, args, is_device_side=False):
        """
        Gera código para lançar um kernel
        
        Sintaxe MoonLight:
        gpu[blocks, threads] add_vectors(d_a, d_b, d_c, n)
        
        Args:
            is_device_side: Se True, gera device-side launch (dentro de kernel)
        """
        if is_device_side:
            # Device-side launch (dynamic parallelism)
            # Requires __device__ attribute on child kernel
            launch_code = f"{kernel_name}<<<{blocks}, {threads}>>>(\n"
            launch_code += "    " + ", ".join(args) + "\n"
            launch_code += ");\n"
            # No cudaDeviceSynchronize in device code - use cudaDeviceSynchronize() if needed
        else:
            # Host-side launch
            launch_code = f"{kernel_name}<<<{blocks}, {threads}>>>(\n"
            launch_code += "    " + ", ".join(args) + "\n"
            launch_code += ");\n"
            launch_code += "cudaDeviceSynchronize();\n"
        
        self.kernel_calls.append({
            'kernel': kernel_name,
            'blocks': blocks,
            'threads': threads,
            'args': args,
            'code': launch_code,
            'device_side': is_device_side
        })
        
        return launch_code
    
    def generate_device_array(self, var_name, size, dtype='float'):
        """
        Gera código para alocar array na GPU
        
        Sintaxe MoonLight:
        d_array = device[1024]
        """
        alloc_code = f"{dtype}* {var_name};\n"
        alloc_code += f"cudaMalloc(&{var_name}, {size} * sizeof({dtype}));\n"
        
        free_code = f"cudaFree({var_name});\n"
        
        self.device_arrays.append({
            'name': var_name,
            'size': size,
            'dtype': dtype,
            'alloc_code': alloc_code,
            'free_code': free_code
        })
        
        return alloc_code
    
    def generate_host_to_device_copy(self, host_var, device_var, size, dtype='float'):
        """
        Gera código para copiar dados do host para o device
        
        host_array → d_array
        """
        copy_code = f"cudaMemcpy({device_var}, {host_var}, "
        copy_code += f"{size} * sizeof({dtype}), cudaMemcpyHostToDevice);\n"
        return copy_code
    
    def generate_device_to_host_copy(self, device_var, host_var, size, dtype='float'):
        """
        Gera código para copiar dados do device para o host
        
        d_array → host_array
        """
        copy_code = f"cudaMemcpy({host_var}, {device_var}, "
        copy_code += f"{size} * sizeof({dtype}), cudaMemcpyDeviceToHost);\n"
        return copy_code
    
    def generate_complete_cuda_program(self, kernels_code, main_code):
        """Gera um programa CUDA completo"""
        cuda_program = """#include <cuda_runtime.h>
#include <iostream>
#include <vector>

"""
        # Adiciona kernels
        cuda_program += "// CUDA Kernels\n"
        for kernel in self.kernels:
            cuda_program += kernel['code'] + "\n"
        
        # Adiciona main
        cuda_program += """
int main() {
    // Inicialização
    cudaSetDevice(0);
    
"""
        cuda_program += main_code
        cuda_program += """
    
    // Cleanup
    cudaDeviceReset();
    return 0;
}
"""
        return cuda_program
    
    def generate_shared_memory(self, var_name, size, dtype='float'):
        """
        Gera código para shared memory dentro de um kernel
        
        Sintaxe MoonLight:
        shared_data = shared[256]
        """
        shared_code = f"__shared__ {dtype} {var_name}[{size}];\n"
        return shared_code
    
    def generate_syncthreads(self):
        """Gera sincronização de threads"""
        return "__syncthreads();\n"
    
    def generate_stream(self, stream_name):
        """
        Gera código para criar um CUDA stream
        
        Sintaxe MoonLight:
        stream = cuda_stream()
        """
        create_code = f"cudaStream_t {stream_name};\n"
        create_code += f"cudaStreamCreate(&{stream_name});\n"
        
        destroy_code = f"cudaStreamDestroy({stream_name});\n"
        
        return {
            'create': create_code,
            'destroy': destroy_code
        }
    
    def generate_async_kernel_launch(self, kernel_name, blocks, threads, stream, args):
        """
        Gera lançamento de kernel assíncrono com stream
        
        Sintaxe MoonLight:
        gpu[blocks, threads, stream] kernel(args)
        """
        launch_code = f"{kernel_name}<<<{blocks}, {threads}, 0, {stream}>>>(\n"
        launch_code += "    " + ", ".join(args) + "\n"
        launch_code += ");\n"
        
        return launch_code
    
    def generate_async_memcpy(self, dst, src, size, direction, stream, dtype='float'):
        """
        Gera cópia assíncrona de memória
        
        direction: 'H2D' (host to device) ou 'D2H' (device to host)
        """
        if direction == 'H2D':
            memcpy_type = 'cudaMemcpyHostToDevice'
        else:
            memcpy_type = 'cudaMemcpyDeviceToHost'
        
        async_code = f"cudaMemcpyAsync({dst}, {src}, "
        async_code += f"{size} * sizeof({dtype}), {memcpy_type}, {stream});\n"
        
        return async_code
    
    def generate_multi_gpu_setup(self, num_gpus):
        """
        Gera código para setup multi-GPU
        
        Sintaxe MoonLight:
        gpu_count = cuda_device_count()
        """
        setup_code = "int deviceCount;\n"
        setup_code += "cudaGetDeviceCount(&deviceCount);\n"
        setup_code += f"std::cout << \"Found \" << deviceCount << \" GPUs\" << std::endl;\n\n"
        
        # Código para usar múltiplas GPUs
        multi_gpu_code = "// Multi-GPU processing\n"
        multi_gpu_code += "for (int dev = 0; dev < deviceCount; dev++) {\n"
        multi_gpu_code += "    cudaSetDevice(dev);\n"
        multi_gpu_code += "    // Processar no dispositivo dev\n"
        multi_gpu_code += "}\n"
        
        return {
            'setup': setup_code,
            'multi_gpu': multi_gpu_code
        }
    
    def generate_reduction_kernel(self, kernel_name, operation='sum'):
        """
        Gera kernel de redução paralela otimizado
        
        Operações: 'sum', 'max', 'min', 'prod'
        """
        ops = {
            'sum': '+',
            'max': 'fmaxf',
            'min': 'fminf',
            'prod': '*'
        }
        
        op_code = ops.get(operation, '+')
        
        kernel_code = f"""__global__ void {kernel_name}(float* input, float* output, int n) {{
    extern __shared__ float sdata[];
    
    unsigned int tid = threadIdx.x;
    unsigned int i = blockIdx.x * blockDim.x + threadIdx.x;
    
    // Carrega dados para shared memory
    sdata[tid] = (i < n) ? input[i] : 0;
    __syncthreads();
    
    // Redução em árvore na shared memory
    for (unsigned int s = blockDim.x / 2; s > 0; s >>= 1) {{
        if (tid < s) {{
"""
        
        if operation in ['max', 'min']:
            kernel_code += f"            sdata[tid] = {op_code}(sdata[tid], sdata[tid + s]);\n"
        else:
            kernel_code += f"            sdata[tid] = sdata[tid] {op_code} sdata[tid + s];\n"
        
        kernel_code += """        }
        __syncthreads();
    }
    
    // Thread 0 escreve resultado do bloco
    if (tid == 0) output[blockIdx.x] = sdata[0];
}
"""
        
        self.kernels.append({
            'name': kernel_name,
            'code': kernel_code,
            'type': 'reduction'
        })
        
        return kernel_code
    
    def translate_ast_to_cuda(self, node, indent=1, in_kernel=False):
        """
        Traduz um nó da AST MoonLight para código CUDA C++
        
        Args:
            in_kernel: Se True, estamos dentro de um kernel (device-side launches)
        """
        ind = "    " * indent
        
        if node is None:
            return ""
        
        if isinstance(node, list):
            code = ""
            for n in node:
                code += self.translate_ast_to_cuda(n, indent, in_kernel)
            return code
        
        if not isinstance(node, tuple):
            # Literal values
            if isinstance(node, str):
                return f'"{node}"'
            return str(node)
        
        op = node[0]
        
        # Assignments
        if op == 'assign':
            var, expr = node[1], node[2]
            expr_code = self.translate_ast_to_cuda(expr, 0, in_kernel)
            return f"{ind}{var} = {expr_code};\n"
        
        # CUDA built-in variables
        elif op == 'cuda_builtin':
            return node[1]  # Already mapped (e.g., "threadIdx.x")
        
        # Device allocation: d_array = device[size]
        elif op == 'device_alloc':
            size_expr = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            return f"device_alloc({size_expr})"  # Placeholder, handled in transpiler
        
        # Shared memory: shared_data = shared[size]
        elif op == 'shared_alloc':
            size_expr = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            return f"shared_alloc({size_expr})"  # Placeholder
        
        # GPU launch (conditional launch inside kernel)
        elif op == 'gpu_launch':
            # gpu[blocks, threads] kernel(args) - device-side launch if in_kernel
            blocks = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            threads = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            kernel_name = node[3]
            args = node[4]
            stream = node[6] if len(node) > 6 and node[6] is not None else None
            
            args_str = ", ".join([self.translate_ast_to_cuda(arg, 0, in_kernel) for arg in args])
            
            if in_kernel:
                # Device-side launch (dynamic parallelism)
                # Child kernel must be __device__ function
                if stream:
                    stream_expr = self.translate_ast_to_cuda(stream, 0, in_kernel)
                    return f"{ind}{kernel_name}<<<{blocks}, {threads}, 0, {stream_expr}>>>({args_str});\n"
                else:
                    return f"{ind}{kernel_name}<<<{blocks}, {threads}>>>({args_str});\n"
            else:
                # Host-side launch (shouldn't happen in translate_ast_to_cuda, but handle it)
                if stream:
                    stream_expr = self.translate_ast_to_cuda(stream, 0, in_kernel)
                    return f"{ind}{kernel_name}<<<{blocks}, {threads}, 0, {stream_expr}>>>({args_str});\n"
                else:
                    return f"{ind}{kernel_name}<<<{blocks}, {threads}>>>({args_str});\n"
        
        # Control flow
        elif op == 'if':
            cond = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            body = self.translate_ast_to_cuda(node[2], indent + 1, in_kernel)
            return f"{ind}if ({cond}) {{\n{body}{ind}}}\n"
        
        elif op == 'if-else':
            cond = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            if_body = self.translate_ast_to_cuda(node[2], indent + 1, in_kernel)
            else_body = self.translate_ast_to_cuda(node[3], indent + 1, in_kernel)
            return f"{ind}if ({cond}) {{\n{if_body}{ind}}} else {{\n{else_body}{ind}}}\n"
        
        elif op == 'while':
            cond = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            body = self.translate_ast_to_cuda(node[2], indent + 1, in_kernel)
            return f"{ind}while ({cond}) {{\n{body}{ind}}}\n"
        
        elif op == 'for':
            init = self.translate_ast_to_cuda(node[1], 0, in_kernel).strip().rstrip(';')
            cond = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            update = self.translate_ast_to_cuda(node[3], 0, in_kernel).strip().rstrip(';')
            body = self.translate_ast_to_cuda(node[4], indent + 1, in_kernel)
            return f"{ind}for ({init}; {cond}; {update}) {{\n{body}{ind}}}\n"
        
        # Expressions
        elif op in ['add', 'sub', 'mul', 'div', 'mod']:
            left = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            right = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            ops = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/', 'mod': '%'}
            return f"({left} {ops[op]} {right})"
        
        elif op in ['gt', 'lt', 'eq', 'neq', 'ge', 'le']:
            left = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            right = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            ops = {'gt': '>', 'lt': '<', 'eq': '==', 'neq': '!=', 'ge': '>=', 'le': '<='}
            return f"({left} {ops[op]} {right})"
        
        elif op in ['and', 'or']:
            left = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            right = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            ops = {'and': '&&', 'or': '||'}
            return f"({left} {ops[op]} {right})"
        
        elif op == 'not':
            expr = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            return f"(!{expr})"
        
        # Array indexing
        elif op == 'list_index':
            var = node[1]
            index = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            return f"{var}[{index}]"
        
        # Array assignment
        elif op == 'list_assign':
            var = node[1]
            index = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            value = self.translate_ast_to_cuda(node[3], 0, in_kernel)
            return f"{ind}{var}[{index}] = {value};\n"
        
        # Compound assignments
        elif op == 'compound_assign':
            var, op_str, expr = node[1], node[2], node[3]
            expr_code = self.translate_ast_to_cuda(expr, 0, in_kernel)
            return f"{ind}{var} {op_str} {expr_code};\n"
        
        # Increment/decrement
        elif op == 'post_increment':
            var, op_str = node[1], node[2]
            return f"{ind}{var}{op_str};\n"
        
        elif op == 'pre_increment':
            op_str, var = node[1], node[2]
            return f"{ind}{op_str}{var};\n"
        
        # Sync operations
        elif op == 'syncthreads':
            return f"{ind}__syncthreads();\n"
        
        elif op == 'syncwarp':
            return f"{ind}__syncwarp();\n"
        
        # Atomic operations
        elif op == 'atomic_add':
            addr = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            val = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            return f"atomicAdd({addr}, {val})"
        
        elif op == 'atomic_sub':
            addr = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            val = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            return f"atomicSub({addr}, {val})"
        
        elif op == 'atomic_min':
            addr = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            val = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            return f"atomicMin({addr}, {val})"
        
        elif op == 'atomic_max':
            addr = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            val = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            return f"atomicMax({addr}, {val})"
        
        elif op == 'atomic_cas':
            addr = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            compare = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            val = self.translate_ast_to_cuda(node[3], 0, in_kernel)
            return f"atomicCAS({addr}, {compare}, {val})"
        
        elif op == 'atomic_exch':
            addr = self.translate_ast_to_cuda(node[1], 0, in_kernel)
            val = self.translate_ast_to_cuda(node[2], 0, in_kernel)
            return f"atomicExch({addr}, {val})"
        
        # Return statement
        elif op == 'return':
            if node[1] is not None:
                expr = self.translate_ast_to_cuda(node[1], 0, in_kernel)
                return f"{ind}return {expr};\n"
            return f"{ind}return;\n"
        
        # Function calls
        elif op == 'func_call':
            func_name = node[1]
            args = [self.translate_ast_to_cuda(arg, 0, in_kernel) for arg in node[2]]
            return f"{func_name}({', '.join(args)})"
        
        # Identifiers
        elif isinstance(op, str) and len(node) == 1:
            return op
        
        # Default: return string representation
        return str(node)
    
    def generate_kernel_from_ast(self, func_name, params, body_ast, is_persistent=False, has_auto_shared=False, has_predict_taken=False, has_profile=False, optimize_level=None, has_hints=False):
        """
        Gera um kernel CUDA completo a partir da AST
        """
        if is_persistent:
            # Persistent kernel - otimizado para longa execução
            # __launch_bounds__ ajuda o compilador a otimizar registros
            kernel_code = f"__global__ void __launch_bounds__(256, 4) {func_name}("
        else:
            kernel_code = f"__global__ void {func_name}("
        
        # Parâmetros do kernel com type inference melhorado
        param_list = []
        for param in params:
            param_type = self._infer_param_type(param)
            param_list.append(f"{param_type} {param}")
        
        kernel_code += ", ".join(param_list)
        kernel_code += ") {\n"
        
        if is_persistent:
            # Adiciona comentário explicativo
            kernel_code += "    // Persistent kernel - runs continuously until stop signal\n"
        
        if has_predict_taken:
            # Branch prediction hint
            kernel_code += "    // @predict_taken: Branch prediction optimization enabled\n"
        
        if has_profile:
            # Profiling enabled
            kernel_code += "    // @profile: Profiling enabled - timing and metrics will be collected\n"
        
        if optimize_level is not None:
            # Optimization level specified
            kernel_code += f"    // @optimize(level={optimize_level}): Optimization level {optimize_level} enabled\n"
            if optimize_level >= 3:
                kernel_code += "    // Level 3: Kernel fusion, dead code elimination, register optimization\n"
            elif optimize_level >= 2:
                kernel_code += "    // Level 2: Aggressive optimizations, memory coalescing\n"
            else:
                kernel_code += "    // Level 1: Basic optimizations\n"
        
        if has_hints:
            # Performance hints enabled
            kernel_code += "    // @hints(): Performance hints enabled - compiler will use hints for optimization\n"
        
        # Transpila o corpo do kernel (dentro de kernel, então gpu_launch será device-side)
        body_code = self.translate_ast_to_cuda(body_ast, 1, in_kernel=True)
        kernel_code += body_code
        
        kernel_code += "}\n"
        
        self.kernels.append({
            'name': func_name,
            'code': kernel_code,
            'params': params,
            'persistent': is_persistent,
            'predict_taken': has_predict_taken
        })
        
        return kernel_code
    
    def _infer_param_type(self, param):
        """
        Infere o tipo do parâmetro baseado no nome
        """
        # Ponteiros de device (arrays)
        if param.startswith('d_') or param.endswith('_queue'):
            if 'queue' in param:
                return 'GPUQueue*'  # Generic queue pointer
            return 'float*'
        
        # Arrays comuns
        if param in ['a', 'b', 'c', 'data', 'input', 'output', 'buffer']:
            return 'float*'
        
        # Tamanhos e contadores
        if param in ['n', 'size', 'count', 'length', 'width', 'height']:
            return 'int'
        
        # Flags e estados
        if param.startswith('flag') or param.startswith('is_'):
            return 'bool'
        
        # Default: int para escalares
        return 'int'
    
    def reset(self):
        """Limpa estado do gerador"""
        self.kernels = []
        self.kernel_calls = []
        self.device_arrays = []
        self.device_vars = set()
        self.gpu_resident_vars = set()

# Instância global
cuda_codegen = CUDACodeGen()

# Funções helper
def cuda_kernel_def(func_name, params, body):
    """Define um kernel CUDA"""
    return cuda_codegen.generate_kernel(func_name, params, body)

def cuda_kernel_launch(kernel_name, blocks, threads, *args):
    """Lança um kernel CUDA"""
    return cuda_codegen.generate_kernel_launch(kernel_name, blocks, threads, list(args))

def device_array(size, dtype='float'):
    """Aloca array na GPU"""
    var_name = f"d_array_{len(cuda_codegen.device_arrays)}"
    return cuda_codegen.generate_device_array(var_name, size, dtype)

def copy_to_device(host_var, device_var, size):
    """Copia dados para GPU"""
    return cuda_codegen.generate_host_to_device_copy(host_var, device_var, size)

def copy_to_host(device_var, host_var, size):
    """Copia dados da GPU"""
    return cuda_codegen.generate_device_to_host_copy(device_var, host_var, size)


