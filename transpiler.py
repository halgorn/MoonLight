from parser import parser
from cuda_codegen import CUDACodeGen

# Global CUDA code generator
cuda_gen = CUDACodeGen()

# Track variable sizes for memory transfers
# Maps variable name to size expression
var_sizes = {}

def traduzir_ast(node, indent=1, in_class=False, in_cuda_kernel=False):
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
            elif isinstance(valor, tuple) and valor[0] == 'device_alloc':
                # d_array = device[size]
                var = node[1]
                size_expr = traduzir_ast(valor[1], 0, in_class)
                var_sizes[var] = size_expr  # Track size for transfers
                cuda_gen.device_vars.add(var)
                return f"{ind}float* {var};\n{ind}cudaMalloc(&{var}, {size_expr} * sizeof(float));\n"
            elif isinstance(valor, tuple) and valor[0] == 'cuda_stream':
                # stream = cuda_stream()
                var = node[1]
                return f"{ind}cudaStream_t {var};\n{ind}cudaStreamCreate(&{var});\n"
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
        
        # CUDA OPERATIONS
        elif op == 'cuda_kernel':
            # cuda kernel def name(params) { body }
            # Structure: ('cuda_kernel', func_name, params, body, is_persistent, decorators)
            func_name = node[1]
            params = node[2]
            body = node[3]
            is_persistent = node[4] if len(node) > 4 else False
            decorators = node[5] if len(node) > 5 else []
            
            # Check for decorators
            has_auto_shared = any(d[1] == 'auto_shared' for d in decorators if isinstance(d, tuple) and len(d) > 1)
            has_predict_taken = any(d[1] == 'predict_taken' for d in decorators if isinstance(d, tuple) and len(d) > 1)
            has_profile = any(d[1] == 'profile' for d in decorators if isinstance(d, tuple) and len(d) > 1)
            
            # Get optimization level and hints
            optimize_level = None
            for d in decorators:
                if isinstance(d, tuple) and len(d) > 1 and d[1] == 'optimize' and len(d) > 2:
                    optimize_level = d[2][0] if d[2] else None
            
            has_hints = any(d[1] == 'hints' for d in decorators if isinstance(d, tuple) and len(d) > 1)
            
            # Use CUDA code generator
            kernel_code = cuda_gen.generate_kernel_from_ast(func_name, params, body, is_persistent, has_auto_shared, has_predict_taken, has_profile, optimize_level, has_hints)
            return kernel_code
        
        elif op == 'gpu_launch':
            # gpu[blocks, threads] kernel(args) or gpu[blocks, threads, stream=stream_var] kernel(args)
            blocks = traduzir_ast(node[1], 0, in_class)
            threads = traduzir_ast(node[2], 0, in_class)
            kernel_name = node[3]
            args = node[4]
            stream = node[6] if len(node) > 6 and node[6] is not None else None
            
            args_str = ", ".join([traduzir_ast(arg, 0, in_class) for arg in args])
            
            if in_cuda_kernel:
                # Device-side launch (dynamic parallelism)
                # Child kernel must be __device__ function
                if stream:
                    # Async device-side launch
                    stream_expr = traduzir_ast(stream, 0, in_class)
                    launch_code = f"{ind}{kernel_name}<<<{blocks}, {threads}, 0, {stream_expr}>>>({args_str});\n"
                else:
                    # Synchronous device-side launch
                    launch_code = f"{ind}{kernel_name}<<<{blocks}, {threads}>>>({args_str});\n"
                    launch_code += f"{ind}cudaDeviceSynchronize();  // Wait for child kernel\n"
            else:
                # Host-side launch
                if stream:
                    # Async launch with stream
                    stream_expr = traduzir_ast(stream, 0, in_class)
                    launch_code = f"{ind}{kernel_name}<<<{blocks}, {threads}, 0, {stream_expr}>>>({args_str});\n"
                    # Don't add cudaDeviceSynchronize() for async launches
                else:
                    # Synchronous launch
                    launch_code = f"{ind}{kernel_name}<<<{blocks}, {threads}>>>({args_str});\n"
                    launch_code += f"{ind}cudaDeviceSynchronize();\n"
            return launch_code
        
        elif op == 'gpu_launch_2d':
            # gpu[(bx, by), (tx, ty)] kernel(args) or gpu[(bx, by), (tx, ty), stream=stream_var] kernel(args)
            blocks = node[1]  # (bx, by)
            threads = node[2]  # (tx, ty)
            kernel_name = node[3]
            args = node[4]
            stream = node[5] if len(node) > 5 and node[5] is not None else None
            
            bx = traduzir_ast(blocks[0], 0, in_class)
            by = traduzir_ast(blocks[1], 0, in_class)
            tx = traduzir_ast(threads[0], 0, in_class)
            ty = traduzir_ast(threads[1], 0, in_class)
            args_str = ", ".join([traduzir_ast(arg, 0, in_class) for arg in args])
            
            launch_code = f"{ind}dim3 dimGrid({bx}, {by});\n"
            launch_code += f"{ind}dim3 dimBlock({tx}, {ty});\n"
            
            if stream:
                # Async launch with stream
                stream_expr = traduzir_ast(stream, 0, in_class)
                launch_code += f"{ind}{kernel_name}<<<dimGrid, dimBlock, 0, {stream_expr}>>>({args_str});\n"
                # Don't add cudaDeviceSynchronize() for async launches
            else:
                # Synchronous launch
                launch_code += f"{ind}{kernel_name}<<<dimGrid, dimBlock>>>({args_str});\n"
                launch_code += f"{ind}cudaDeviceSynchronize();\n"
            return launch_code
        
        elif op == 'gpu_launch_device':
            # gpu[device_id][blocks, threads] kernel(args)
            device_id = node[1]
            blocks = traduzir_ast(node[2], 0, in_class)
            threads = traduzir_ast(node[3], 0, in_class)
            kernel_name = node[4]
            args = node[5]
            
            args_str = ", ".join([traduzir_ast(arg, 0, in_class) for arg in args])
            launch_code = f"{ind}cudaSetDevice({device_id});\n"
            launch_code += f"{ind}{kernel_name}<<<{blocks}, {threads}>>>({args_str});\n"
            launch_code += f"{ind}cudaDeviceSynchronize();\n"
            return launch_code
        
        elif op == 'device_alloc':
            # d_array = device[size]
            size_expr = traduzir_ast(node[1], 0, in_class)
            return f"device_alloc({size_expr})"  # Placeholder - handled in assignment
            # Note: Size tracking is handled in assignment statement
        
        elif op == 'shared_alloc':
            # shared_data = shared[size] (inside kernel)
            size_expr = traduzir_ast(node[1], 0, in_class)
            return f"__shared__ float shared_data[{size_expr}]"
        
        elif op == 'mem_transfer' or op == 'mem_transfer_h2d':
            # d_array <- h_array or h_array <- d_array
            dest = node[1]
            src = node[2]
            
            # Determine direction by variable naming convention
            if dest.startswith('d_'):
                # Host to Device
                direction = "cudaMemcpyHostToDevice"
                # Try to get size from destination (device array)
                size_var = dest
            else:
                # Device to Host
                direction = "cudaMemcpyDeviceToHost"
                # Try to get size from source (device array)
                size_var = src
            
            # Try to determine size from tracked variables
            if size_var in var_sizes:
                size_expr = var_sizes[size_var]
                transfer_code = f"{ind}cudaMemcpy({dest}, {src}, {size_expr} * sizeof(float), {direction});\n"
            else:
                # Fallback: try common size variable names (n, size, count, len)
                # Or use a variable if it exists in the context
                transfer_code = f"{ind}// Note: Size not automatically determined for {dest} <- {src}\n"
                transfer_code += f"{ind}// Please specify size explicitly or ensure variable size is tracked\n"
                transfer_code += f"{ind}// cudaMemcpy({dest}, {src}, n * sizeof(float), {direction});\n"
            
            return transfer_code
        
        elif op == 'cuda_free':
            # free(d_array)
            var = node[1]
            cuda_gen.device_vars.discard(var)
            return f"{ind}cudaFree({var});\n"
        
        elif op == 'gpu_resident_alloc':
            # gpu_resident d_array = device[size]
            var = node[1]
            size_expr = traduzir_ast(node[2], 0, in_class)
            cuda_gen.device_vars.add(var)
            cuda_gen.gpu_resident_vars.add(var)  # Track as resident
            var_sizes[var] = size_expr  # Track size for transfers
            # Generate as global device pointer (not freed automatically)
            return f"{ind}// GPU-resident: {var} persists across function calls\n{ind}cudaMalloc(&{var}, {size_expr} * sizeof(float));\n"

        elif op == 'gpu_device_alloc':
            # gpu[device_id] var = device[size] - allocate on specific GPU
            device_id_expr = traduzir_ast(node[1], 0, in_class)
            var = node[2]
            size_expr = traduzir_ast(node[3], 0, in_class)
            cuda_gen.device_vars.add(var)
            var_sizes[var] = size_expr  # Track size for transfers
            return f"{ind}cudaSetDevice({device_id_expr});\n{ind}cudaMalloc(&{var}, {size_expr} * sizeof(float));\n"
        
        elif op == 'device_malloc':
            # device_malloc(size) - allocate on GPU from within kernel
            size_expr = traduzir_ast(node[1], 0, in_class)
            return f"malloc({size_expr} * sizeof(float))"  # Device-side malloc
        
        elif op == 'device_free':
            # device_free(ptr) - free memory on GPU
            ptr_expr = traduzir_ast(node[1], 0, in_class)
            return f"{ind}free({ptr_expr});\n"
        
        elif op == 'unified_memory_alloc':
            # unified_data = unified memory[size]
            var = node[1]
            size_expr = traduzir_ast(node[2], 0, in_class)
            cuda_gen.device_vars.add(var)
            var_sizes[var] = size_expr  # Track size for transfers
            # Generate cudaMallocManaged for unified memory
            return f"{ind}// Unified memory: accessible from both CPU and GPU\n{ind}cudaMallocManaged(&{var}, {size_expr} * sizeof(float));\n"
        
        elif op == 'pinned_memory_alloc':
            # pinned_data = pinned memory[size]
            var = node[1]
            size_expr = traduzir_ast(node[2], 0, in_class)
            var_sizes[var] = size_expr  # Track size for transfers
            # Generate cudaHostAlloc for pinned memory
            return f"{ind}// Pinned memory: page-locked for fast transfers\n{ind}cudaHostAlloc(&{var}, {size_expr} * sizeof(float), cudaHostAllocDefault);\n"
        
        elif op == 'syncthreads':
            return f"{ind}__syncthreads();\n"
        
        elif op == 'syncwarp':
            return f"{ind}__syncwarp();\n"
        
        elif op == 'gpu_printf':
            # gpu_printf(format, args...) - GPU-side printf
            args = node[1] if len(node) > 1 else []
            if isinstance(args, list) and len(args) > 0:
                format_str = traduzir_ast(args[0], 0, in_class)
                if len(args) > 1:
                    arg_list = ", ".join([traduzir_ast(arg, 0, in_class) for arg in args[1:]])
                    return f"{ind}printf({format_str}, {arg_list});\n"
                else:
                    return f"{ind}printf({format_str});\n"
            return f"{ind}printf(\"GPU printf\\n\");\n"
        
        elif op == 'gpu_breakpoint':
            # gpu_breakpoint() - GPU-side breakpoint (for debugging)
            return f"{ind}__debugbreak();  // GPU breakpoint (requires debugger)\n"
        
        elif op == 'cuda_builtin':
            # CUDA built-in variables (threadIdx.x, etc.)
            return node[1]
        
        # Warp primitives
        elif op == 'warp_reduce_sum':
            # warp_reduce_sum(value) - warp-level reduction
            val = traduzir_ast(node[1], 0, in_class)
            return f"warp_reduce_sum({val})"  # Would use __shfl_down_sync in real CUDA
        
        elif op == 'warp_reduce_max':
            val = traduzir_ast(node[1], 0, in_class)
            return f"warp_reduce_max({val})"
        
        elif op == 'warp_reduce_min':
            val = traduzir_ast(node[1], 0, in_class)
            return f"warp_reduce_min({val})"
        
        elif op == 'warp_shuffle':
            # warp_shuffle(value, src_lane) - warp shuffle
            val = traduzir_ast(node[1], 0, in_class)
            src = traduzir_ast(node[2], 0, in_class) if len(node) > 2 else "0"
            return f"__shfl_sync(0xffffffff, {val}, {src})"  # CUDA intrinsic
        
        # CUDA Streams
        elif op == 'cuda_stream':
            # cuda_stream() - create CUDA stream
            return f"cudaStream_t stream_{id(node)};\n{ind}cudaStreamCreate(&stream_{id(node)});\n"
        
        elif op == 'sync_stream':
            # sync_stream(stream) - synchronize stream
            stream = traduzir_ast(node[1], 0, in_class) if len(node) > 1 else "0"
            return f"{ind}cudaStreamSynchronize({stream});\n"
        
        elif op == 'cuda_graph_begin':
            # cuda_graph_begin() - start graph capture
            return f"{ind}cudaGraph_t graph;\n{ind}cudaGraphExec_t graphExec;\n{ind}cudaStreamBeginCapture(stream, cudaStreamCaptureModeGlobal);\n"
        
        elif op == 'cuda_graph_end':
            # cuda_graph_end() - end graph capture
            return f"{ind}cudaStreamEndCapture(stream, &graph);\n{ind}cudaGraphInstantiate(&graphExec, graph, NULL, NULL, 0);\n"
        
        elif op == 'cuda_graph_launch':
            # cuda_graph_launch(graph) - launch graph
            graph = traduzir_ast(node[1], 0, in_class) if len(node) > 1 else "graphExec"
            return f"{ind}cudaGraphLaunch({graph}, stream);\n"
        
        # Multi-GPU operations
        elif op == 'enable_p2p':
            # enable_p2p(gpu0, gpu1) - enable P2P access
            gpu0 = traduzir_ast(node[1], 0, in_class)
            gpu1 = traduzir_ast(node[2], 0, in_class)
            return f"{ind}int canAccessPeer = 0;\n{ind}cudaDeviceCanAccessPeer(&canAccessPeer, {gpu0}, {gpu1});\n{ind}if (canAccessPeer) {{\n{ind}    cudaSetDevice({gpu0});\n{ind}    cudaDeviceEnablePeerAccess({gpu1}, 0);\n{ind}}}\n"
        
        elif op == 'p2p_copy':
            # p2p_copy(dest, src, size) - GPU to GPU copy
            dest = traduzir_ast(node[1], 0, in_class)
            src = traduzir_ast(node[2], 0, in_class)
            size = traduzir_ast(node[3], 0, in_class)
            return f"{ind}cudaMemcpyPeerAsync({dest}, dest_device, {src}, src_device, {size}, stream);\n"
        
        # Atomic operations
        elif op == 'atomic_add':
            addr = traduzir_ast(node[1], 0, in_class)
            val = traduzir_ast(node[2], 0, in_class)
            return f"atomicAdd(&{addr}, {val})"
        
        elif op == 'atomic_sub':
            addr = traduzir_ast(node[1], 0, in_class)
            val = traduzir_ast(node[2], 0, in_class)
            return f"atomicSub(&{addr}, {val})"
        
        elif op == 'atomic_min':
            addr = traduzir_ast(node[1], 0, in_class)
            val = traduzir_ast(node[2], 0, in_class)
            return f"atomicMin(&{addr}, {val})"
        
        elif op == 'atomic_max':
            addr = traduzir_ast(node[1], 0, in_class)
            val = traduzir_ast(node[2], 0, in_class)
            return f"atomicMax(&{addr}, {val})"
        
        elif op == 'atomic_cas':
            addr = traduzir_ast(node[1], 0, in_class)
            compare = traduzir_ast(node[2], 0, in_class)
            val = traduzir_ast(node[3], 0, in_class)
            return f"atomicCAS(&{addr}, {compare}, {val})"
        
        elif op == 'atomic_exch':
            addr = traduzir_ast(node[1], 0, in_class)
            val = traduzir_ast(node[2], 0, in_class)
            return f"atomicExch(&{addr}, {val})"
        
        # Work Queue operations
        elif op == 'gpu_queue_decl':
            queue_name = node[1]
            elem_type = node[2]
            capacity = traduzir_ast(node[3], 0, in_class)
            
            code = f"{ind}GPUQueue<{elem_type}>* {queue_name} = "
            code += f"create_gpu_queue<{elem_type}>({capacity});\n"
            return code
        
        elif op == 'enqueue_host':
            queue = node[1]
            item = traduzir_ast(node[2], 0, in_class)
            return f"{ind}enqueue_from_host({queue}, {item});\n"
        
        elif op == 'dequeue_host':
            var = node[1]
            queue = node[2]
            return f"{ind}{var} = dequeue_to_host({queue}, &{var});\n"
        
        elif op == 'dequeue_wait':
            queue = node[1]
            return f"{queue}->dequeue_wait()"
        
        elif op == 'enqueue':
            queue = node[1]
            args = node[2] if len(node) > 2 and isinstance(node[2], list) else [node[2]] if len(node) > 2 else []
            if args:
                args_str = ", ".join([traduzir_ast(arg, 0, in_class) for arg in args])
                return f"{ind}{queue}->enqueue({args_str});\n"
            else:
                return f"{ind}{queue}->enqueue();\n"
        
        # Pipeline operations
        elif op == 'pipeline_def':
            pipeline_name = node[1]
            stages = node[2]
            
            # Generate pipeline structure
            code = f"{ind}// Pipeline: {pipeline_name}\n"
            code += f"{ind}struct Pipeline_{pipeline_name} {{\n"
            
            # Generate queues between stages
            for i in range(len(stages)):
                code += f"{ind}    GPUQueue* queue_{i};\n"
            code += f"{ind}    GPUQueue* queue_{len(stages)};\n"
            
            # Add stage info
            for stage in stages:
                stage_name = stage[1]
                kernel_func = stage[2]
                params = stage[3]
                code += f"{ind}    // Stage: {stage_name} -> {kernel_func}\n"
            
            code += f"{ind}}};\n"
            return code
        
        elif op == 'pipeline_start':
            pipeline = node[1]
            return f"{ind}{pipeline}.start();\n"
        
        elif op == 'pipeline_stop':
            pipeline = node[1]
            return f"{ind}{pipeline}.stop();\n"

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

        elif op in ['+', '-', '*', '/', '%', 'power', '**']:
            if op in ['power', '**']:
                left = traduzir_ast(node[1], 0, in_class)
                right = traduzir_ast(node[2], 0, in_class)
                return f"std::pow({left}, {right})"
            return f"({traduzir_ast(node[1], 0, in_class)} {op} {traduzir_ast(node[2], 0, in_class)})"
        
        # Operações bitwise
        elif op in ['&', '|', '^', '<<', '>>']:
            return f"({traduzir_ast(node[1], 0, in_class)} {op} {traduzir_ast(node[2], 0, in_class)})"
        
        elif op in ['>', '<', '==', '!=', '>=', '<=']:
            return f"({traduzir_ast(node[1], 0, in_class)} {op} {traduzir_ast(node[2], 0, in_class)})"
        
        elif op == 'and':
            return f"({traduzir_ast(node[1], 0, in_class)} && {traduzir_ast(node[2], 0, in_class)})"
        elif op == 'or':
            return f"({traduzir_ast(node[1], 0, in_class)} || {traduzir_ast(node[2], 0, in_class)})"
        elif op == 'not':
            return f"(!{traduzir_ast(node[1], 0, in_class)})"
        
        elif op == 'unary':
            operator = node[1]
            operand = traduzir_ast(node[2], 0, in_class)
            if operator == '~':
                return f"(~{operand})"
            elif operator == '-':
                return f"(-{operand})"
            elif operator == '+':
                return f"(+{operand})"
            return f"({operator}{operand})"

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
        
        elif op == 'list_comp':
            # List comprehension: ('list_comp', expr, var, iterable, condition)
            expr = node[1]
            var = node[2]
            iterable = node[3]
            condition = node[4] if len(node) > 4 else None
            
            # Gera código C++ usando lambda e std::transform ou loop
            iter_str = traduzir_ast(iterable, 0, in_class)
            expr_str = traduzir_ast(expr, 0, in_class)
            
            # Versão simples usando loop
            if condition:
                cond_str = traduzir_ast(condition, 0, in_class)
                return f"list_comprehension_if({iter_str}, [&](auto {var}) {{ return {expr_str}; }}, [&](auto {var}) {{ return {cond_str}; }})"
            else:
                return f"list_comprehension({iter_str}, [&](auto {var}) {{ return {expr_str}; }})"
        
        elif op == 'dict_comp':
            # Dict comprehension: ('dict_comp', key_expr, value_expr, var, iterable, condition)
            # Por simplicidade, não implementado completamente ainda
            return "{/* dict comprehension not fully implemented */}"
        
        elif op == 'set_comp':
            # Set comprehension similar a list comp
            return "{/* set comprehension not fully implemented */}"

        elif op == 'list_index':
            lista = node[1]
            indice = traduzir_ast(node[2], 0, in_class)
            return f"{lista}[{indice}]"
        
        elif op == 'slice':
            # Slice: node = ('slice', container, start, stop, step)
            container = node[1]
            start = traduzir_ast(node[2], 0, in_class) if node[2] else "0"
            stop = traduzir_ast(node[3], 0, in_class) if node[3] else f"{container}.size()"
            step = traduzir_ast(node[4], 0, in_class) if node[4] and len(node) > 4 else "1"
            
            # Gera código C++ para slice
            return f"slice_vector({container}, {start}, {stop}, {step})"

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

        elif op == 'func_call_stmt':
            # Function call as statement (e.g., main(), sync_stream(stream))
            nome = node[1]
            argumentos = node[2] if len(node) > 2 else []
            
            # Special handling for stream and graph functions
            if nome == 'sync_stream' and argumentos:
                stream = traduzir_ast(argumentos[0], 0, in_class)
                return f"{ind}cudaStreamSynchronize({stream});\n"
            elif nome == 'cuda_graph_begin':
                # cuda_graph_begin() - start graph capture
                return f"{ind}cudaGraph_t graph;\n{ind}cudaGraphExec_t graphExec;\n{ind}cudaStream_t graphStream;\n{ind}cudaStreamCreate(&graphStream);\n{ind}cudaStreamBeginCapture(graphStream, cudaStreamCaptureModeGlobal);\n"
            elif nome == 'cuda_graph_end':
                # cuda_graph_end() - end graph capture
                return f"{ind}cudaStreamEndCapture(graphStream, &graph);\n{ind}cudaGraphInstantiate(&graphExec, graph, NULL, NULL, 0);\n"
            elif nome == 'cuda_graph_launch' and argumentos:
                graph = traduzir_ast(argumentos[0], 0, in_class)
                return f"{ind}cudaGraphLaunch(graphExec, graphStream);\n"
            elif nome == 'enable_p2p' and len(argumentos) == 2:
                # enable_p2p(gpu0, gpu1)
                gpu0 = traduzir_ast(argumentos[0], 0, in_class)
                gpu1 = traduzir_ast(argumentos[1], 0, in_class)
                return f"{ind}enable_p2p_access({gpu0}, {gpu1});\n"
            elif nome == 'p2p_copy' and len(argumentos) == 3:
                # p2p_copy(dest, src, size)
                dest = traduzir_ast(argumentos[0], 0, in_class)
                src = traduzir_ast(argumentos[1], 0, in_class)
                size = traduzir_ast(argumentos[2], 0, in_class)
                return f"{ind}p2p_memcpy({dest}, dst_device, {src}, src_device, {size}, stream);\n"
            
            # Regular function call
            if argumentos:
                args_str = ", ".join([traduzir_ast(arg, 0, in_class) for arg in argumentos])
            else:
                args_str = ""
            return f"{ind}{nome}({args_str});\n"
        
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

        elif op == 'lambda':
            # Lambda: node = ('lambda', params, body)
            parametros = node[1]
            corpo = node[2]
            if parametros:
                params_str = ", ".join([f"auto {p}" for p in parametros])
            else:
                params_str = ""
            # Em C++, lambda pode retornar uma expressão diretamente
            corpo_str = traduzir_ast(corpo, 0, in_class)
            return f"[&]({params_str}) {{ return {corpo_str}; }}"
        
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
#include <cmath>

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

// Função auxiliar para slicing
template<typename T>
std::vector<T> slice_vector(const std::vector<T>& vec, int start, int stop, int step = 1) {
    std::vector<T> result;
    int size = vec.size();
    
    // Normaliza índices negativos
    if (start < 0) start += size;
    if (stop < 0) stop += size;
    
    // Limita aos bounds
    start = std::max(0, std::min(start, size));
    stop = std::max(0, std::min(stop, size));
    
    if (step > 0) {
        for (int i = start; i < stop; i += step) {
            result.push_back(vec[i]);
        }
    } else if (step < 0) {
        for (int i = start; i > stop; i += step) {
            result.push_back(vec[i]);
        }
    }
    return result;
}

// Função auxiliar para list comprehension
template<typename T, typename Func>
auto list_comprehension(const std::vector<T>& vec, Func func) {
    std::vector<decltype(func(vec[0]))> result;
    for (const auto& item : vec) {
        result.push_back(func(item));
    }
    return result;
}

// Função auxiliar para list comprehension com condição
template<typename T, typename Func, typename Pred>
auto list_comprehension_if(const std::vector<T>& vec, Func func, Pred pred) {
    std::vector<decltype(func(vec[0]))> result;
    for (const auto& item : vec) {
        if (pred(item)) {
            result.push_back(func(item));
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