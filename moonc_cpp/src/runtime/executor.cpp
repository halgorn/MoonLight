#include "moonlight/executor.h"
#include "moonlight/memory_manager.h"
#include <iostream>
#include <stdexcept>
#include <cmath>

namespace moonlight {

Executor::Executor()
    : memory_manager_(nullptr), cuda_loader_(nullptr), ptx_module_(nullptr),
      has_return_(false), gpu_start_event_(nullptr), gpu_stop_event_(nullptr),
      gpu_timer_started_(false) {
    pushScope();
}

Executor::~Executor() {
    while (!scopes_.empty()) {
        popScope();
    }
}

void Executor::executeProgram(std::shared_ptr<Program> program) {
    // First pass: collect function and kernel definitions
    for (const auto& stmt : program->statements) {
        if (auto func = std::dynamic_pointer_cast<FunctionDef>(stmt)) {
            functions_[func->name] = func;
        } else if (auto kernel = std::dynamic_pointer_cast<CudaKernelDef>(stmt)) {
            kernels_[kernel->name] = kernel;
        }
    }
    
    // Second pass: execute statements
    for (const auto& stmt : program->statements) {
        executeStatement(stmt);
        if (has_return_) {
            break;
        }
    }
}

Value Executor::evaluateExpression(ExprPtr expr) {
    if (auto int_lit = std::dynamic_pointer_cast<IntegerLiteral>(expr)) {
        return int_lit->value;
    } else if (auto float_lit = std::dynamic_pointer_cast<FloatLiteral>(expr)) {
        return float_lit->value;
    } else if (auto str_lit = std::dynamic_pointer_cast<StringLiteral>(expr)) {
        return str_lit->value;
    } else if (auto bool_lit = std::dynamic_pointer_cast<BooleanLiteral>(expr)) {
        return bool_lit->value;
    } else if (auto none_lit = std::dynamic_pointer_cast<NoneLiteral>(expr)) {
        return std::string("None");
    } else if (auto ident = std::dynamic_pointer_cast<Identifier>(expr)) {
        return getVariable(ident->name);
    } else if (auto bin_op = std::dynamic_pointer_cast<BinaryOp>(expr)) {
        return evaluateBinaryOp(bin_op);
    } else if (auto un_op = std::dynamic_pointer_cast<UnaryOp>(expr)) {
        return evaluateUnaryOp(un_op);
    } else if (auto call = std::dynamic_pointer_cast<FunctionCall>(expr)) {
        return evaluateFunctionCall(call);
    } else if (auto idx = std::dynamic_pointer_cast<IndexAccess>(expr)) {
        return evaluateIndexAccess(idx);
    } else if (auto member = std::dynamic_pointer_cast<MemberAccess>(expr)) {
        return evaluateMemberAccess(member);
    } else if (auto builtin = std::dynamic_pointer_cast<BuiltInVariable>(expr)) {
        return evaluateBuiltInVariable(builtin);
    } else if (auto dev_alloc = std::dynamic_pointer_cast<DeviceAlloc>(expr)) {
        return evaluateDeviceAlloc(dev_alloc);
    } else if (auto shared_alloc = std::dynamic_pointer_cast<SharedAlloc>(expr)) {
        return evaluateSharedAlloc(shared_alloc);
    } else if (auto list_lit = std::dynamic_pointer_cast<ListLiteral>(expr)) {
        std::vector<Value> elements;
        for (const auto& elem : list_lit->elements) {
            elements.push_back(evaluateExpression(elem));
        }
        return elements;
    }
    
    throw std::runtime_error("Unknown expression type");
}

void Executor::executeStatement(StmtPtr stmt) {
    if (auto assign = std::dynamic_pointer_cast<Assignment>(stmt)) {
        executeAssignment(assign);
    } else if (auto if_stmt = std::dynamic_pointer_cast<IfStatement>(stmt)) {
        executeIfStatement(if_stmt);
    } else if (auto while_stmt = std::dynamic_pointer_cast<WhileStatement>(stmt)) {
        executeWhileStatement(while_stmt);
    } else if (auto for_stmt = std::dynamic_pointer_cast<ForStatement>(stmt)) {
        executeForStatement(for_stmt);
    } else if (auto ret = std::dynamic_pointer_cast<ReturnStatement>(stmt)) {
        executeReturnStatement(ret);
    } else if (auto print = std::dynamic_pointer_cast<PrintStatement>(stmt)) {
        executePrintStatement(print);
    } else if (auto func = std::dynamic_pointer_cast<FunctionDef>(stmt)) {
        executeFunctionDef(func);
    } else if (auto kernel = std::dynamic_pointer_cast<CudaKernelDef>(stmt)) {
        executeCudaKernelDef(kernel);
    } else if (auto launch = std::dynamic_pointer_cast<GpuLaunch>(stmt)) {
        executeGpuLaunch(launch);
    } else if (auto transfer = std::dynamic_pointer_cast<MemoryTransfer>(stmt)) {
        executeMemoryTransfer(transfer);
    } else if (auto free_stmt = std::dynamic_pointer_cast<FreeStatement>(stmt)) {
        executeFreeStatement(free_stmt);
    } else if (auto expr_stmt = std::dynamic_pointer_cast<ExpressionStmt>(stmt)) {
        evaluateExpression(expr_stmt->expression);
    }
}

// Scope management
void Executor::pushScope() {
    scopes_.push(std::map<std::string, Value>());
}

void Executor::popScope() {
    if (!scopes_.empty()) {
        scopes_.pop();
    }
}

void Executor::setVariable(const std::string& name, const Value& value) {
    if (!scopes_.empty()) {
        scopes_.top()[name] = value;
    }
}

Value Executor::getVariable(const std::string& name) {
    // Search from top to bottom of scope stack
    std::stack<std::map<std::string, Value>> temp_stack = scopes_;
    while (!temp_stack.empty()) {
        auto& scope = temp_stack.top();
        auto it = scope.find(name);
        if (it != scope.end()) {
            return it->second;
        }
        temp_stack.pop();
    }
    throw std::runtime_error("Undefined variable: " + name);
}

bool Executor::hasVariable(const std::string& name) {
    std::stack<std::map<std::string, Value>> temp_stack = scopes_;
    while (!temp_stack.empty()) {
        auto& scope = temp_stack.top();
        if (scope.find(name) != scope.end()) {
            return true;
        }
        temp_stack.pop();
    }
    return false;
}

// Expression evaluation implementations
Value Executor::evaluateBinaryOp(std::shared_ptr<BinaryOp> op) {
    Value left = evaluateExpression(op->left);
    Value right = evaluateExpression(op->right);
    return performBinaryOperation(op->op, left, right);
}

Value Executor::evaluateUnaryOp(std::shared_ptr<UnaryOp> op) {
    Value operand = evaluateExpression(op->operand);
    return performUnaryOperation(op->op, operand);
}

Value Executor::evaluateFunctionCall(std::shared_ptr<FunctionCall> call) {
    // Check if it's a built-in function
    if (auto ident = std::dynamic_pointer_cast<Identifier>(call->function)) {
        std::string func_name = ident->name;
        
        if (func_name == "float") {
            if (!call->arguments.empty()) {
                Value arg = evaluateExpression(call->arguments[0]);
                return convertToFloat(arg);
            }
        } else if (func_name == "int") {
            if (!call->arguments.empty()) {
                Value arg = evaluateExpression(call->arguments[0]);
                return convertToInteger(arg);
            }
        } else if (func_name == "str") {
            if (!call->arguments.empty()) {
                Value arg = evaluateExpression(call->arguments[0]);
                return convertToString(arg);
            }
        } else if (func_name == "gpu_start_timer") {
            // Start GPU timer
            if (cuda_loader_ == nullptr) {
                throw std::runtime_error("CUDA loader not set");
            }
            if (gpu_start_event_ != nullptr) {
                cuda_loader_->destroyEvent(gpu_start_event_);
            }
            gpu_start_event_ = cuda_loader_->createEvent();
            if (gpu_start_event_ == nullptr) {
                throw std::runtime_error("Failed to create start event");
            }
            if (!cuda_loader_->recordEvent(gpu_start_event_)) {
                throw std::runtime_error("Failed to record start event");
            }
            gpu_timer_started_ = true;
            return Value(0); // Return dummy value
        } else if (func_name == "gpu_stop_timer") {
            // Stop GPU timer
            if (cuda_loader_ == nullptr) {
                throw std::runtime_error("CUDA loader not set");
            }
            if (!gpu_timer_started_) {
                throw std::runtime_error("gpu_start_timer() must be called before gpu_stop_timer()");
            }
            if (gpu_stop_event_ != nullptr) {
                cuda_loader_->destroyEvent(gpu_stop_event_);
            }
            gpu_stop_event_ = cuda_loader_->createEvent();
            if (gpu_stop_event_ == nullptr) {
                throw std::runtime_error("Failed to create stop event");
            }
            if (!cuda_loader_->recordEvent(gpu_stop_event_)) {
                throw std::runtime_error("Failed to record stop event");
            }
            return Value(0); // Return dummy value
        } else if (func_name == "gpu_elapsed_time") {
            // Get elapsed time in milliseconds
            if (cuda_loader_ == nullptr) {
                throw std::runtime_error("CUDA loader not set");
            }
            if (gpu_start_event_ == nullptr || gpu_stop_event_ == nullptr) {
                throw std::runtime_error("gpu_start_timer() and gpu_stop_timer() must be called first");
            }
            // Synchronize stop event to ensure it's recorded
            if (!cuda_loader_->synchronizeEvent(gpu_stop_event_)) {
                throw std::runtime_error("Failed to synchronize stop event");
            }
            float elapsed_ms = cuda_loader_->getElapsedTime(gpu_start_event_, gpu_stop_event_);
            if (elapsed_ms < 0.0f) {
                throw std::runtime_error("Failed to get elapsed time");
            }
            return Value(static_cast<double>(elapsed_ms));
        } else {
            // User-defined function
            std::vector<Value> args;
            for (const auto& arg_expr : call->arguments) {
                args.push_back(evaluateExpression(arg_expr));
            }
            return callFunction(func_name, args);
        }
    }
    
    throw std::runtime_error("Unknown function call");
}

Value Executor::evaluateIndexAccess(std::shared_ptr<IndexAccess> access) {
    Value array_val = evaluateExpression(access->array);
    Value index_val = evaluateExpression(access->index);
    
    if (!isList(array_val)) {
        throw std::runtime_error("Index access on non-list value");
    }
    
    int idx = 0;
    if (isInteger(index_val)) {
        idx = getInteger(index_val);
    } else if (isFloat(index_val)) {
        idx = static_cast<int>(getFloat(index_val));
    } else {
        throw std::runtime_error("Index must be integer");
    }
    
    auto& list = getList(array_val);
    if (idx < 0 || static_cast<size_t>(idx) >= list.size()) {
        throw std::runtime_error("Index out of bounds");
    }
    
    return list[idx];
}

Value Executor::evaluateMemberAccess(std::shared_ptr<MemberAccess> access) {
    // Member access not fully implemented yet
    throw std::runtime_error("Member access not yet implemented");
}

Value Executor::evaluateBuiltInVariable(std::shared_ptr<BuiltInVariable> builtin) {
    // Built-in variables are only valid inside kernels (PTX)
    // For CPU execution, return 0 or throw error
    throw std::runtime_error("Built-in variables only valid in GPU kernels");
}

Value Executor::evaluateDeviceAlloc(std::shared_ptr<DeviceAlloc> alloc) {
    if (memory_manager_ == nullptr) {
        throw std::runtime_error("Memory manager not set");
    }
    
    Value size_val = evaluateExpression(alloc->size);
    size_t size = 0;
    
    if (isInteger(size_val)) {
        size = static_cast<size_t>(getInteger(size_val));
    } else if (isFloat(size_val)) {
        size = static_cast<size_t>(getFloat(size_val));
    } else {
        throw std::runtime_error("Device allocation size must be numeric");
    }
    
    // Allocate as float array (4 bytes per element)
    size_t bytes = size * sizeof(float);
    
    // Generate a unique temporary name for tracking
    // This will be updated when assigned to a variable in executeAssignment
    static int alloc_counter = 0;
    std::string temp_name = "__device_alloc_" + std::to_string(alloc_counter++);
    
    void* ptr = memory_manager_->allocateDevice(bytes, temp_name);
    memory_manager_->setArraySize(temp_name, bytes);
    
    if (ptr == nullptr) {
        throw std::runtime_error("Failed to allocate device memory");
    }
    
    // Store the size in a map keyed by pointer for later retrieval
    // This allows us to find the size when the pointer is assigned to a variable
    device_ptr_sizes_[ptr] = bytes;
    
    return DevicePointer(ptr);
}

Value Executor::evaluateSharedAlloc(std::shared_ptr<SharedAlloc> alloc) {
    // Shared memory allocation is handled in PTX generation
    // For CPU execution, return placeholder
    throw std::runtime_error("Shared memory allocation only valid in GPU kernels");
}

// Statement execution implementations
void Executor::executeAssignment(std::shared_ptr<Assignment> assign) {
    Value value = evaluateExpression(assign->value);
    
    // If it's a device allocation, register the variable name in memory manager
    if (isPointer(value) && memory_manager_ != nullptr) {
        void* ptr = getPointer(value);
        
        // Find size from map (set during allocation)
        size_t size = 0;
        auto it = device_ptr_sizes_.find(ptr);
        if (it != device_ptr_sizes_.end()) {
            size = it->second;
        }
        
        // Register the variable name with the pointer and size
        if (size > 0) {
            memory_manager_->registerVariable(assign->variable, ptr, size);
        } else {
            // Fallback: try to find from existing allocations
            // This shouldn't happen if allocation tracking works correctly
            memory_manager_->registerVariable(assign->variable, ptr, 0);
        }
    }
    
    setVariable(assign->variable, value);
    
    // Also track list sizes for memory transfers
    if (isList(value) && memory_manager_ != nullptr) {
        const auto& list = getList(value);
        size_t bytes = list.size() * sizeof(float);
        memory_manager_->setArraySize(assign->variable, bytes);
    }
}

void Executor::executeIfStatement(std::shared_ptr<IfStatement> if_stmt) {
    Value condition = evaluateExpression(if_stmt->condition);
    
    if (isTruthy(condition)) {
        pushScope();
        for (const auto& stmt : if_stmt->then_block) {
            executeStatement(stmt);
            if (has_return_) break;
        }
        popScope();
    } else if (!if_stmt->else_block.empty()) {
        pushScope();
        for (const auto& stmt : if_stmt->else_block) {
            executeStatement(stmt);
            if (has_return_) break;
        }
        popScope();
    }
}

void Executor::executeWhileStatement(std::shared_ptr<WhileStatement> while_stmt) {
    while (true) {
        Value condition = evaluateExpression(while_stmt->condition);
        if (!isTruthy(condition)) {
            break;
        }
        
        pushScope();
        for (const auto& stmt : while_stmt->body) {
            executeStatement(stmt);
            if (has_return_) {
                popScope();
                return;
            }
        }
        popScope();
    }
}

void Executor::executeForStatement(std::shared_ptr<ForStatement> for_stmt) {
    pushScope();
    
    // Init
    if (for_stmt->init) {
        executeStatement(for_stmt->init);
    }
    
    // Loop
    while (true) {
        // Condition
        if (for_stmt->condition) {
            Value condition = evaluateExpression(for_stmt->condition);
            if (!isTruthy(condition)) {
                break;
            }
        }
        
        // Body
        for (const auto& stmt : for_stmt->body) {
            executeStatement(stmt);
            if (has_return_) {
                popScope();
                return;
            }
        }
        
        // Increment
        if (for_stmt->increment) {
            executeStatement(for_stmt->increment);
        }
    }
    
    popScope();
}

void Executor::executeReturnStatement(std::shared_ptr<ReturnStatement> ret) {
    if (ret->value) {
        return_value_ = evaluateExpression(ret->value);
    } else {
        return_value_ = std::string("None");
    }
    has_return_ = true;
}

void Executor::executePrintStatement(std::shared_ptr<PrintStatement> print) {
    for (size_t i = 0; i < print->expressions.size(); ++i) {
        if (i > 0) std::cout << " ";
        Value val = evaluateExpression(print->expressions[i]);
        std::cout << valueToString(val);
    }
    std::cout << std::endl;
}

void Executor::executeFunctionDef(std::shared_ptr<FunctionDef> func) {
    // Function definitions are collected in executeProgram
    // This is called during execution but function is already stored
}

void Executor::executeCudaKernelDef(std::shared_ptr<CudaKernelDef> kernel) {
    // Kernel definitions are collected in executeProgram
    // This is called during execution but kernel is already stored
}

void Executor::executeGpuLaunch(std::shared_ptr<GpuLaunch> launch) {
    if (cuda_loader_ == nullptr || ptx_module_ == nullptr) {
        throw std::runtime_error("CUDA loader or PTX module not set");
    }
    
    // Evaluate blocks and threads
    Value blocks_val = evaluateExpression(launch->blocks);
    Value threads_val = evaluateExpression(launch->threads);
    
    unsigned int blocks = 0;
    unsigned int threads = 0;
    
    if (isInteger(blocks_val)) {
        blocks = static_cast<unsigned int>(getInteger(blocks_val));
    } else if (isFloat(blocks_val)) {
        blocks = static_cast<unsigned int>(getFloat(blocks_val));
    }
    
    if (isInteger(threads_val)) {
        threads = static_cast<unsigned int>(getInteger(threads_val));
    } else if (isFloat(threads_val)) {
        threads = static_cast<unsigned int>(getFloat(threads_val));
    }
    
    // Get kernel name and arguments
    if (auto call = std::dynamic_pointer_cast<FunctionCall>(launch->kernel)) {
        if (auto ident = std::dynamic_pointer_cast<Identifier>(call->function)) {
            std::string kernel_name = ident->name;
            
            // Get function from PTX module
            CUfunction function = cuda_loader_->getFunction(ptx_module_, kernel_name);
            if (function == nullptr) {
                throw std::runtime_error("Kernel function not found: " + kernel_name);
            }
            
            // Prepare arguments
            std::vector<void*> kernel_args;
            std::vector<int> int_args;
            std::vector<float> float_args;
            
            for (const auto& arg_expr : call->arguments) {
                Value arg_val = evaluateExpression(arg_expr);
                
                if (isPointer(arg_val)) {
                    // GPU pointer - pass pointer directly
                    void* ptr = getPointer(arg_val);
                    // Also try to get from memory manager if it's a variable
                    if (auto ident = std::dynamic_pointer_cast<Identifier>(arg_expr)) {
                        if (memory_manager_ != nullptr) {
                            void* mgr_ptr = memory_manager_->getDevicePointer(ident->name);
                            if (mgr_ptr != nullptr) {
                                ptr = mgr_ptr;
                            }
                        }
                    }
                    kernel_args.push_back(&ptr);
                } else if (isInteger(arg_val)) {
                    // Integer parameter - store in vector and pass pointer
                    int_args.push_back(getInteger(arg_val));
                    kernel_args.push_back(&int_args.back());
                } else if (isFloat(arg_val)) {
                    // Float parameter - store in vector and pass pointer
                    float_args.push_back(static_cast<float>(getFloat(arg_val)));
                    kernel_args.push_back(&float_args.back());
                } else {
                    throw std::runtime_error("Unsupported kernel argument type");
                }
            }
            
            // Launch kernel
            void** params = kernel_args.empty() ? nullptr : kernel_args.data();
            if (!cuda_loader_->launchKernel(function, blocks, 1, 1, threads, 1, 1, 0, params)) {
                throw std::runtime_error("Failed to launch kernel: " + cuda_loader_->getLastError());
            }
            
            // Synchronize
            cuda_loader_->synchronize();
        }
    }
}

void Executor::executeMemoryTransfer(std::shared_ptr<MemoryTransfer> transfer) {
    if (memory_manager_ == nullptr || cuda_loader_ == nullptr) {
        throw std::runtime_error("Memory manager or CUDA loader not set");
    }
    
    void* dest_ptr = nullptr;
    void* src_ptr = nullptr;
    size_t size = 0;
    
    // Get destination pointer (from variable or direct pointer)
    std::string dest_var_name = "";
    if (auto ident = std::dynamic_pointer_cast<Identifier>(transfer->destination)) {
        dest_var_name = ident->name;
        dest_ptr = memory_manager_->getDevicePointer(dest_var_name);
        if (dest_ptr == nullptr) {
            // Try to get from variable value
            if (hasVariable(dest_var_name)) {
                Value dest_val = getVariable(dest_var_name);
                if (isPointer(dest_val)) {
                    dest_ptr = getPointer(dest_val);
                }
            }
        }
        size = memory_manager_->getArraySize(dest_var_name);
    } else {
        Value dest_val = evaluateExpression(transfer->destination);
        if (isPointer(dest_val)) {
            dest_ptr = getPointer(dest_val);
        }
    }
    
    if (dest_ptr == nullptr) {
        throw std::runtime_error("Invalid destination for memory transfer");
    }
    
    // Get source (could be CPU array or GPU pointer)
    if (transfer->is_host_to_device) {
        // H->D: source is CPU array, dest is GPU pointer
        std::string src_var_name = "";
        if (auto ident = std::dynamic_pointer_cast<Identifier>(transfer->source)) {
            src_var_name = ident->name;
        }
        
        Value src_val = evaluateExpression(transfer->source);
        
        if (isList(src_val)) {
            const auto& list = getList(src_val);
            size_t list_size = list.size() * sizeof(float);
            
            if (size == 0) {
                size = list_size;
                if (!dest_var_name.empty()) {
                    memory_manager_->setArraySize(dest_var_name, size);
                }
            }
            
            // Convert list to float array
            std::vector<float> host_data(list.size());
            for (size_t i = 0; i < list.size(); ++i) {
                if (isFloat(list[i])) {
                    host_data[i] = static_cast<float>(getFloat(list[i]));
                } else if (isInteger(list[i])) {
                    host_data[i] = static_cast<float>(getInteger(list[i]));
                }
            }
            
            if (!cuda_loader_->copyHostToDevice(dest_ptr, host_data.data(), size)) {
                throw std::runtime_error("Failed to copy H->D: " + cuda_loader_->getLastError());
            }
        } else {
            throw std::runtime_error("Source for H->D transfer must be a list/array");
        }
    } else {
        // D->H: source is GPU pointer, dest is CPU array variable
        std::string src_var_name = "";
        if (auto ident = std::dynamic_pointer_cast<Identifier>(transfer->source)) {
            src_var_name = ident->name;
            src_ptr = memory_manager_->getDevicePointer(src_var_name);
            size = memory_manager_->getArraySize(src_var_name);
        }
        
        if (src_ptr == nullptr) {
            Value src_val = evaluateExpression(transfer->source);
            if (isPointer(src_val)) {
                src_ptr = getPointer(src_val);
            }
        }
        
        if (src_ptr == nullptr || size == 0) {
            throw std::runtime_error("Invalid source for D->H transfer");
        }
        
        // Allocate host buffer
        size_t num_elements = size / sizeof(float);
        std::vector<float> host_data(num_elements);
        
        if (!cuda_loader_->copyDeviceToHost(host_data.data(), src_ptr, size)) {
            throw std::runtime_error("Failed to copy D->H: " + cuda_loader_->getLastError());
        }
        
        // Convert to Value list and store in destination variable
        if (auto ident = std::dynamic_pointer_cast<Identifier>(transfer->destination)) {
            std::vector<Value> result_list;
            for (float val : host_data) {
                result_list.push_back(static_cast<double>(val));
            }
            setVariable(ident->name, result_list);
        } else {
            throw std::runtime_error("Destination for D->H transfer must be a variable");
        }
    }
}

void Executor::executeFreeStatement(std::shared_ptr<FreeStatement> free_stmt) {
    if (memory_manager_ == nullptr) {
        throw std::runtime_error("Memory manager not set");
    }
    
    Value var_val = evaluateExpression(free_stmt->variable);
    
    if (isPointer(var_val)) {
        memory_manager_->freeDevice(getPointer(var_val));
    } else if (auto ident = std::dynamic_pointer_cast<Identifier>(free_stmt->variable)) {
        memory_manager_->freeDevice(ident->name);
    }
}

Value Executor::callFunction(const std::string& name, const std::vector<Value>& args) {
    auto it = functions_.find(name);
    if (it == functions_.end()) {
        throw std::runtime_error("Function not found: " + name);
    }
    
    auto func = it->second;
    
    // Check argument count
    if (args.size() != func->parameters.size()) {
        throw std::runtime_error("Argument count mismatch for function: " + name);
    }
    
    // Push new scope
    pushScope();
    
    // Set parameters
    for (size_t i = 0; i < args.size(); ++i) {
        setVariable(func->parameters[i], args[i]);
    }
    
    // Execute function body
    has_return_ = false;
    for (const auto& stmt : func->body) {
        executeStatement(stmt);
        if (has_return_) {
            break;
        }
    }
    
    // Get return value
    Value result = has_return_ ? return_value_ : std::string("None");
    has_return_ = false;
    
    // Pop scope
    popScope();
    
    return result;
}

// Helper methods
bool Executor::isTruthy(const Value& v) {
    if (isBoolean(v)) {
        return getBoolean(v);
    } else if (isInteger(v)) {
        return getInteger(v) != 0;
    } else if (isFloat(v)) {
        return getFloat(v) != 0.0;
    } else if (isString(v)) {
        return !getString(v).empty();
    } else if (isList(v)) {
        return !getList(v).empty();
    }
    return false;
}

Value Executor::performBinaryOperation(const std::string& op, const Value& left, const Value& right) {
    // List multiplication: [0.0] * n
    if (op == "*") {
        if (isList(left) && (isInteger(right) || isFloat(right))) {
            int count = isInteger(right) ? getInteger(right) : static_cast<int>(getFloat(right));
            const auto& original_list = getList(left);
            std::vector<Value> result;
            for (int i = 0; i < count; ++i) {
                result.insert(result.end(), original_list.begin(), original_list.end());
            }
            return result;
        } else if (isList(right) && (isInteger(left) || isFloat(left))) {
            int count = isInteger(left) ? getInteger(left) : static_cast<int>(getFloat(left));
            const auto& original_list = getList(right);
            std::vector<Value> result;
            for (int i = 0; i < count; ++i) {
                result.insert(result.end(), original_list.begin(), original_list.end());
            }
            return result;
        }
    }
    
    // Arithmetic operations
    if (op == "+") {
        if (isInteger(left) && isInteger(right)) {
            return getInteger(left) + getInteger(right);
        } else {
            return getFloat(left) + getFloat(right);
        }
    } else if (op == "-") {
        if (isInteger(left) && isInteger(right)) {
            return getInteger(left) - getInteger(right);
        } else {
            return getFloat(left) - getFloat(right);
        }
    } else if (op == "*") {
        if (isInteger(left) && isInteger(right)) {
            return getInteger(left) * getInteger(right);
        } else {
            return getFloat(left) * getFloat(right);
        }
    } else if (op == "/") {
        // Integer division if both are integers
        if (isInteger(left) && isInteger(right)) {
            int right_val = getInteger(right);
            if (right_val == 0) {
                throw std::runtime_error("Division by zero");
            }
            return getInteger(left) / right_val;
        } else {
            return getFloat(left) / getFloat(right);
        }
    } else if (op == "%") {
        if (isInteger(left) && isInteger(right)) {
            return getInteger(left) % getInteger(right);
        } else {
            return static_cast<int>(getFloat(left)) % static_cast<int>(getFloat(right));
        }
    } else if (op == "**") {
        return std::pow(getFloat(left), getFloat(right));
    }
    // Comparison operations
    else if (op == "==") {
        if (isInteger(left) && isInteger(right)) {
            return getInteger(left) == getInteger(right);
        } else if (isFloat(left) || isFloat(right)) {
            return getFloat(left) == getFloat(right);
        } else if (isString(left) && isString(right)) {
            return getString(left) == getString(right);
        } else if (isBoolean(left) && isBoolean(right)) {
            return getBoolean(left) == getBoolean(right);
        }
    } else if (op == "!=") {
        Value eq = performBinaryOperation("==", left, right);
        return !isTruthy(eq);
    } else if (op == "<") {
        if (isInteger(left) && isInteger(right)) {
            return getInteger(left) < getInteger(right);
        } else {
            return getFloat(left) < getFloat(right);
        }
    } else if (op == ">") {
        if (isInteger(left) && isInteger(right)) {
            return getInteger(left) > getInteger(right);
        } else {
            return getFloat(left) > getFloat(right);
        }
    } else if (op == "<=") {
        Value lt = performBinaryOperation("<", left, right);
        Value eq = performBinaryOperation("==", left, right);
        return (isTruthy(lt) || isTruthy(eq));
    } else if (op == ">=") {
        Value gt = performBinaryOperation(">", left, right);
        Value eq = performBinaryOperation("==", left, right);
        return (isTruthy(gt) || isTruthy(eq));
    }
    // Logical operations
    else if (op == "and") {
        return isTruthy(left) && isTruthy(right);
    } else if (op == "or") {
        return isTruthy(left) || isTruthy(right);
    }
    
    throw std::runtime_error("Unknown binary operation: " + op);
}

Value Executor::performUnaryOperation(const std::string& op, const Value& operand) {
    if (op == "-") {
        if (isInteger(operand)) {
            return -getInteger(operand);
        } else {
            return -getFloat(operand);
        }
    } else if (op == "+") {
        return operand;
    } else if (op == "not") {
        return !isTruthy(operand);
    } else if (op == "~") {
        if (isInteger(operand)) {
            return ~getInteger(operand);
        }
    }
    
    throw std::runtime_error("Unknown unary operation: " + op);
}

void Executor::setReturnValue(const Value& v) {
    return_value_ = v;
    has_return_ = true;
}

Value Executor::getReturnValue() {
    return return_value_;
}

void Executor::clearReturn() {
    has_return_ = false;
}

} // namespace moonlight

