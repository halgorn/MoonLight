#include "moonlight/ptx_generator.h"
#include <sstream>
#include <stdexcept>

namespace moonlight {

PTXGenerator::PTXGenerator()
    : ptx_version_("7.0"), compute_capability_("sm_75"), 
      register_counter_(0), label_counter_(0) {
    shared_variables_.clear();
    register_types_.clear();
    used_registers_.clear();
    parameter_registers_.clear();
}

void PTXGenerator::setComputeCapability(const std::string& cc) {
    compute_capability_ = cc;
}

void PTXGenerator::setPTXVersion(const std::string& version) {
    ptx_version_ = version;
}

std::string PTXGenerator::generatePTX(std::shared_ptr<Program> program) {
    register_counter_ = 0;
    label_counter_ = 0;
    variable_registers_.clear();
    shared_variables_.clear();
    register_types_.clear();
    used_registers_.clear();
    parameter_registers_.clear();
    
    std::stringstream ptx;
    ptx << generateHeader();
    ptx << "\n";
    
    // Generate kernels
    for (const auto& stmt : program->statements) {
        if (auto kernel = std::dynamic_pointer_cast<CudaKernelDef>(stmt)) {
            ptx << generateKernel(kernel);
            ptx << "\n";
        }
    }
    
    return ptx.str();
}

std::string PTXGenerator::generateHeader() {
    std::stringstream header;
    header << ".version " << ptx_version_ << "\n";
    header << ".target " << compute_capability_ << "\n";
    header << ".address_size 64";
    return header.str();
}

std::string PTXGenerator::generateKernel(std::shared_ptr<CudaKernelDef> kernel) {
    // Reset per-kernel state
    register_counter_ = 0;
    register_types_.clear();
    used_registers_.clear();
    parameter_registers_.clear();
    variable_registers_.clear();
    
    std::stringstream ptx;
    
    // .entry kernel_name(.param .u64 param1, .param .u64 param2, ...)
    ptx << ".entry " << kernel->name << "(";
    ptx << generateKernelParameters(kernel);
    ptx << ") {\n";
    
    // Generate body
    ptx << generateKernelBody(kernel->body);
    
    ptx << "    ret;\n";
    ptx << "}\n";
    
    return ptx.str();
}

std::string PTXGenerator::generateKernelParameters(std::shared_ptr<CudaKernelDef> kernel) {
    std::stringstream params;
    
    for (size_t i = 0; i < kernel->parameters.size(); ++i) {
        if (i > 0) params << ", ";
        // For now, assume all parameters are pointers (u64) or scalars (u32)
        // TODO: Add type inference
        std::string param_name = kernel->parameters[i];
        if (param_name[0] == 'd' && param_name[1] == '_') {
            // Device pointer
            params << ".param .u64 " << param_name;
        } else if (param_name == "n" || param_name == "size" || param_name == "count") {
            // Scalar (size parameter)
            params << ".param .u32 " << param_name;
        } else {
            // Default to pointer
            params << ".param .u64 " << param_name;
        }
    }
    
    return params.str();
}

std::string PTXGenerator::generateKernelBody(std::vector<StmtPtr> body) {
    std::stringstream ptx;
    
    // First pass: collect shared memory allocations
    shared_variables_.clear();
    for (const auto& stmt : body) {
        if (auto assign = std::dynamic_pointer_cast<Assignment>(stmt)) {
            if (auto shared_alloc = std::dynamic_pointer_cast<SharedAlloc>(assign->value)) {
                // Track shared variable
                size_t size = 256; // Default
                if (auto size_expr = std::dynamic_pointer_cast<IntegerLiteral>(shared_alloc->size)) {
                    size = static_cast<size_t>(size_expr->value);
                }
                std::string ptx_name = "__shared_" + assign->variable;
                shared_variables_[assign->variable] = std::make_pair(size, ptx_name);
            }
        }
    }
    
    // Declare shared memory arrays
    for (const auto& [var_name, size_name] : shared_variables_) {
        size_t size = size_name.first;
        std::string ptx_name = size_name.second;
        ptx << "    .shared .f32 " << ptx_name << "[" << size << "];\n";
    }
    
    if (!shared_variables_.empty()) {
        ptx << "\n";
    }
    
    // Generate code first to collect all used registers
    std::stringstream code_stream;
    for (const auto& stmt : body) {
        // Clear pending PTX before each statement
        pending_ptx_.str("");
        pending_ptx_.clear();
        
        std::string stmt_ptx = generateStatement(stmt);
        
        // Output any pending PTX code first
        std::string pending = pending_ptx_.str();
        if (!pending.empty()) {
            std::stringstream ss(pending);
            std::string line;
            while (std::getline(ss, line)) {
                if (!line.empty()) {
                    code_stream << "    " << line << "\n";
                }
            }
        }
        
        if (!stmt_ptx.empty()) {
            // Indent each line
            std::stringstream ss(stmt_ptx);
            std::string line;
            while (std::getline(ss, line)) {
                if (!line.empty()) {
                    code_stream << "    " << line << "\n";
                }
            }
        }
    }
    
    // Now declare all used registers grouped by type
    std::map<std::string, std::vector<std::string>> registers_by_type;
    for (const auto& reg : used_registers_) {
        auto it = register_types_.find(reg);
        if (it != register_types_.end()) {
            registers_by_type[it->second].push_back(reg);
        }
    }
    
    // Declare registers by type
    for (const auto& [type, regs] : registers_by_type) {
        if (!regs.empty()) {
            ptx << "    .reg " << type << " ";
            for (size_t i = 0; i < regs.size(); ++i) {
                if (i > 0) ptx << ", ";
                ptx << regs[i];
            }
            ptx << ";\n";
        }
    }
    
    // Declare built-in variable registers (always needed)
    ptx << "    .reg .u32 %tid, %ctaid, %ntid;\n";
    ptx << "\n";
    
    // Load built-in variables into registers
    ptx << "    mov.u32 %tid, %tid.x;\n";
    ptx << "    mov.u32 %ctaid, %ctaid.x;\n";
    ptx << "    mov.u32 %ntid, %ntid.x;\n";
    ptx << "\n";
    
    // Output the generated code
    ptx << code_stream.str();
    
    return ptx.str();
}

std::string PTXGenerator::generateStatement(StmtPtr stmt) {
    if (auto assign = std::dynamic_pointer_cast<Assignment>(stmt)) {
        return generateAssignment(assign);
    } else if (auto if_stmt = std::dynamic_pointer_cast<IfStatement>(stmt)) {
        return generateIfStatement(if_stmt);
    } else if (auto while_stmt = std::dynamic_pointer_cast<WhileStatement>(stmt)) {
        return generateWhileStatement(while_stmt);
    } else if (auto for_stmt = std::dynamic_pointer_cast<ForStatement>(stmt)) {
        return generateForStatement(for_stmt);
    } else if (auto ret = std::dynamic_pointer_cast<ReturnStatement>(stmt)) {
        return generateReturnStatement(ret);
    } else if (auto expr_stmt = std::dynamic_pointer_cast<ExpressionStmt>(stmt)) {
        return generateExpression(expr_stmt->expression) + ";\n";
    }
    
    return "";
}

std::string PTXGenerator::generateAssignment(std::shared_ptr<Assignment> assign) {
    std::stringstream ptx;
    
    // Output any pending PTX from value evaluation
    std::string pending = pending_ptx_.str();
    if (!pending.empty()) {
        std::stringstream ss(pending);
        std::string line;
        while (std::getline(ss, line)) {
            if (!line.empty()) {
                ptx << line << "\n";
            }
        }
        pending_ptx_.str("");
        pending_ptx_.clear();
    }
    
    std::string value_ptx = generateExpression(assign->value);
    
    // Output any pending PTX from value evaluation
    pending = pending_ptx_.str();
    if (!pending.empty()) {
        std::stringstream ss(pending);
        std::string line;
        while (std::getline(ss, line)) {
            if (!line.empty()) {
                ptx << line << "\n";
            }
        }
        pending_ptx_.str("");
        pending_ptx_.clear();
    }
    
    // Check if this is a shared memory allocation: shared = shared[size]
    if (auto shared_alloc = std::dynamic_pointer_cast<SharedAlloc>(assign->value)) {
        // This is handled in generateKernelBody() - just track the variable
        // The shared array is already declared, so we just need to note the variable name
        // For now, return empty - the actual handling is in generateKernelBody
        return "";
    }
    
    // Check if this is an array element assignment: arr[i] = value
    if (assign->array_index) {
        // Array element assignment
        std::string var_name = assign->variable;
        bool is_shared = shared_variables_.find(var_name) != shared_variables_.end();
        
        std::string index_ptx = generateExpression(assign->array_index);
        std::string index_reg = allocateRegister(".u32");
        
        // Convert index to register if it's a literal
        if (index_ptx.find_first_not_of("0123456789") == std::string::npos) {
            ptx << "mov.u32 " << index_reg << ", " << index_ptx << ";\n";
        } else {
            index_reg = index_ptx;
        }
        
        if (is_shared) {
            // Write to shared memory
            std::string shared_name = shared_variables_[var_name].second;
            ptx << "st.shared.f32 [" << shared_name << "+" << index_reg << "*4], " << value_ptx << ";\n";
        } else {
            // Write to global memory
            // Load the parameter into a register if not already loaded
            std::string base_reg;
            auto param_it = parameter_registers_.find(var_name);
            if (param_it != parameter_registers_.end()) {
                base_reg = param_it->second;
            } else {
                base_reg = allocateRegister(".u64");
                parameter_registers_[var_name] = base_reg;
                ptx << "ld.param.u64 " << base_reg << ", [" << var_name << "];\n";
            }
            
            std::string offset_reg = allocateRegister(".u64");
            ptx << "mul.wide.u32 " << offset_reg << ", " << index_reg << ", 4;\n";
            
            std::string addr_reg = allocateRegister(".u64");
            ptx << "add.u64 " << addr_reg << ", " << base_reg << ", " << offset_reg << ";\n";
            
            // Ensure value is in a register
            std::string value_reg = value_ptx;
            if (value_ptx.find("%") != 0) {
                value_reg = allocateRegister(".f32");
                if (value_ptx.find(".") != std::string::npos || 
                    value_ptx.find("e") != std::string::npos || 
                    value_ptx.find("E") != std::string::npos) {
                    ptx << "mov.f32 " << value_reg << ", 0f" << value_ptx << ";\n";
                } else {
                    std::string temp_reg = allocateRegister(".u32");
                    ptx << "mov.u32 " << temp_reg << ", " << value_ptx << ";\n";
                    ptx << "cvt.f32.u32 " << value_reg << ", " << temp_reg << ";\n";
                }
            }
            
            ptx << "st.global.f32 [" << addr_reg << "], " << value_reg << ";\n";
        }
        
        return ptx.str();
    }
    
    // Check if assignment is to a shared variable (simple assignment, not array access)
    bool is_shared_var = shared_variables_.find(assign->variable) != shared_variables_.end();
    
    if (is_shared_var) {
        // This is assigning to a shared variable name itself (not an array element)
        // This shouldn't happen in practice, but handle it
        // For now, treat as regular variable
    }
    
    // For simple variable assignment
    std::string var_reg = getVariableRegister(assign->variable);
    if (var_reg.empty()) {
        // Infer type from value
        std::string type = inferPTXType(assign->value);
        var_reg = allocateRegister(type);
        setVariableRegister(assign->variable, var_reg);
    }
    
    // Get the type of the variable register
    std::string var_type = ".u32";  // default
    auto type_it = register_types_.find(var_reg);
    if (type_it != register_types_.end()) {
        var_type = type_it->second;
    }
    
    // Ensure value is in a register with correct type
    std::string value_reg = value_ptx;
    if (value_ptx.find("%") != 0) {
        // It's a literal, load into register
        value_reg = allocateRegister(var_type);
        if (var_type == ".f32") {
            if (value_ptx.find(".") != std::string::npos || 
                value_ptx.find("e") != std::string::npos || 
                value_ptx.find("E") != std::string::npos) {
                ptx << "mov.f32 " << value_reg << ", 0f" << value_ptx << ";\n";
            } else {
                std::string temp_reg = allocateRegister(".u32");
                ptx << "mov.u32 " << temp_reg << ", " << value_ptx << ";\n";
                ptx << "cvt.f32.u32 " << value_reg << ", " << temp_reg << ";\n";
            }
        } else {
            ptx << "mov" << var_type << " " << value_reg << ", " << value_ptx << ";\n";
        }
    }
    
    ptx << "mov" << var_type << " " << var_reg << ", " << value_reg << ";\n";
    
    return ptx.str();
}

std::string PTXGenerator::generateIfStatement(std::shared_ptr<IfStatement> if_stmt) {
    std::stringstream ptx;
    
    // Output any pending PTX from condition evaluation
    std::string pending = pending_ptx_.str();
    if (!pending.empty()) {
        std::stringstream ss(pending);
        std::string line;
        while (std::getline(ss, line)) {
            if (!line.empty()) {
                ptx << line << "\n";
            }
        }
        pending_ptx_.str("");
        pending_ptx_.clear();
    }
    
    std::string cond_ptx = generateExpression(if_stmt->condition);
    
    // Output any pending PTX from condition evaluation
    pending = pending_ptx_.str();
    if (!pending.empty()) {
        std::stringstream ss(pending);
        std::string line;
        while (std::getline(ss, line)) {
            if (!line.empty()) {
                ptx << line << "\n";
            }
        }
        pending_ptx_.str("");
        pending_ptx_.clear();
    }
    
    // Condition should already be a predicate from generateBinaryOp if it's a comparison
    // Otherwise, convert to predicate
    std::string cond_reg;
    if (cond_ptx.find("%p") == 0) {
        // Already a predicate register
        cond_reg = cond_ptx;
    } else {
        // Convert to predicate: setp.ne.type pred, value, 0
        cond_reg = allocateRegister(".pred");
        std::string type = inferPTXType(if_stmt->condition);
        std::string value_reg = cond_ptx;
        if (cond_ptx.find("%") != 0) {
            // It's a literal, load into register
            value_reg = allocateRegister(type);
            ptx << "mov" << type << " " << value_reg << ", " << cond_ptx << ";\n";
        }
        ptx << "setp.ne" << type << " " << cond_reg << ", " << value_reg << ", 0;\n";
    }
    
    std::string else_label = generateLabel("else");
    std::string end_label = generateLabel("endif");
    
    // Branch if false
    ptx << "@!" << cond_reg << " bra " << else_label << ";\n";
    
    // Then block
    for (const auto& stmt : if_stmt->then_block) {
        std::string stmt_ptx = generateStatement(stmt);
        if (!stmt_ptx.empty()) {
            std::stringstream ss(stmt_ptx);
            std::string line;
            while (std::getline(ss, line)) {
                if (!line.empty()) {
                    ptx << line << "\n";
                }
            }
        }
    }
    
    if (!if_stmt->else_block.empty()) {
        ptx << "bra " << end_label << ";\n";
        ptx << else_label << ":\n";
        
        // Else block
        for (const auto& stmt : if_stmt->else_block) {
            std::string stmt_ptx = generateStatement(stmt);
            if (!stmt_ptx.empty()) {
                std::stringstream ss(stmt_ptx);
                std::string line;
                while (std::getline(ss, line)) {
                    if (!line.empty()) {
                        ptx << line << "\n";
                    }
                }
            }
        }
    } else {
        ptx << else_label << ":\n";
    }
    
    ptx << end_label << ":\n";
    
    return ptx.str();
}

std::string PTXGenerator::generateWhileStatement(std::shared_ptr<WhileStatement> while_stmt) {
    std::stringstream ptx;
    
    std::string loop_label = generateLabel("loop");
    std::string end_label = generateLabel("endloop");
    
    ptx << loop_label << ":\n";
    
    // Output any pending PTX from condition evaluation
    std::string pending = pending_ptx_.str();
    if (!pending.empty()) {
        std::stringstream ss(pending);
        std::string line;
        while (std::getline(ss, line)) {
            if (!line.empty()) {
                ptx << line << "\n";
            }
        }
        pending_ptx_.str("");
        pending_ptx_.clear();
    }
    
    // Evaluate condition
    std::string cond_ptx = generateExpression(while_stmt->condition);
    
    // Output any pending PTX from condition evaluation
    pending = pending_ptx_.str();
    if (!pending.empty()) {
        std::stringstream ss(pending);
        std::string line;
        while (std::getline(ss, line)) {
            if (!line.empty()) {
                ptx << line << "\n";
            }
        }
        pending_ptx_.str("");
        pending_ptx_.clear();
    }
    
    // Condition should already be a predicate from generateBinaryOp if it's a comparison
    std::string cond_reg;
    if (cond_ptx.find("%p") == 0) {
        // Already a predicate register
        cond_reg = cond_ptx;
    } else {
        // Convert to predicate
        cond_reg = allocateRegister(".pred");
        std::string type = inferPTXType(while_stmt->condition);
        std::string value_reg = cond_ptx;
        if (cond_ptx.find("%") != 0) {
            value_reg = allocateRegister(type);
            ptx << "mov" << type << " " << value_reg << ", " << cond_ptx << ";\n";
        }
        ptx << "setp.ne" << type << " " << cond_reg << ", " << value_reg << ", 0;\n";
    }
    
    ptx << "@!" << cond_reg << " bra " << end_label << ";\n";
    
    // Body
    for (const auto& stmt : while_stmt->body) {
        std::string stmt_ptx = generateStatement(stmt);
        if (!stmt_ptx.empty()) {
            std::stringstream ss(stmt_ptx);
            std::string line;
            while (std::getline(ss, line)) {
                if (!line.empty()) {
                    ptx << line << "\n";
                }
            }
        }
    }
    
    ptx << "bra " << loop_label << ";\n";
    ptx << end_label << ":\n";
    
    return ptx.str();
}

std::string PTXGenerator::generateForStatement(std::shared_ptr<ForStatement> for_stmt) {
    std::stringstream ptx;
    
    // Init
    if (for_stmt->init) {
        std::string init_ptx = generateStatement(for_stmt->init);
        if (!init_ptx.empty()) {
            std::stringstream ss(init_ptx);
            std::string line;
            while (std::getline(ss, line)) {
                if (!line.empty()) {
                    ptx << line << "\n";
                }
            }
        }
    }
    
    std::string loop_label = generateLabel("forloop");
    std::string end_label = generateLabel("endfor");
    
    ptx << loop_label << ":\n";
    
    // Condition
    if (for_stmt->condition) {
        // Output any pending PTX
        std::string pending = pending_ptx_.str();
        if (!pending.empty()) {
            std::stringstream ss(pending);
            std::string line;
            while (std::getline(ss, line)) {
                if (!line.empty()) {
                    ptx << line << "\n";
                }
            }
            pending_ptx_.str("");
            pending_ptx_.clear();
        }
        
        std::string cond_ptx = generateExpression(for_stmt->condition);
        
        // Output any pending PTX
        pending = pending_ptx_.str();
        if (!pending.empty()) {
            std::stringstream ss(pending);
            std::string line;
            while (std::getline(ss, line)) {
                if (!line.empty()) {
                    ptx << line << "\n";
                }
            }
            pending_ptx_.str("");
            pending_ptx_.clear();
        }
        
        std::string cond_reg;
        if (cond_ptx.find("%p") == 0) {
            cond_reg = cond_ptx;
        } else {
            cond_reg = allocateRegister(".pred");
            std::string type = inferPTXType(for_stmt->condition);
            std::string value_reg = cond_ptx;
            if (cond_ptx.find("%") != 0) {
                value_reg = allocateRegister(type);
                ptx << "mov" << type << " " << value_reg << ", " << cond_ptx << ";\n";
            }
            ptx << "setp.ne" << type << " " << cond_reg << ", " << value_reg << ", 0;\n";
        }
        
        ptx << "@!" << cond_reg << " bra " << end_label << ";\n";
    }
    
    // Body
    for (const auto& stmt : for_stmt->body) {
        std::string stmt_ptx = generateStatement(stmt);
        if (!stmt_ptx.empty()) {
            std::stringstream ss(stmt_ptx);
            std::string line;
            while (std::getline(ss, line)) {
                if (!line.empty()) {
                    ptx << line << "\n";
                }
            }
        }
    }
    
    // Increment
    if (for_stmt->increment) {
        std::string inc_ptx = generateStatement(for_stmt->increment);
        if (!inc_ptx.empty()) {
            std::stringstream ss(inc_ptx);
            std::string line;
            while (std::getline(ss, line)) {
                if (!line.empty()) {
                    ptx << line << "\n";
                }
            }
        }
    }
    
    ptx << "bra " << loop_label << ";\n";
    ptx << end_label << ":\n";
    
    return ptx.str();
}

std::string PTXGenerator::generateReturnStatement(std::shared_ptr<ReturnStatement> ret) {
    if (ret->value) {
        // For kernels, return is usually void
        // But we can generate the expression if needed
        return "ret;\n";
    }
    return "ret;\n";
}

std::string PTXGenerator::generateExpression(ExprPtr expr) {
    if (auto bin_op = std::dynamic_pointer_cast<BinaryOp>(expr)) {
        return generateBinaryOp(bin_op);
    } else if (auto un_op = std::dynamic_pointer_cast<UnaryOp>(expr)) {
        return generateUnaryOp(un_op);
    } else if (auto call = std::dynamic_pointer_cast<FunctionCall>(expr)) {
        return generateFunctionCall(call);
    } else if (auto idx = std::dynamic_pointer_cast<IndexAccess>(expr)) {
        return generateIndexAccess(idx);
    } else if (auto builtin = std::dynamic_pointer_cast<BuiltInVariable>(expr)) {
        return generateBuiltInVariable(builtin);
    } else if (auto dev_alloc = std::dynamic_pointer_cast<DeviceAlloc>(expr)) {
        return generateDeviceAlloc(dev_alloc);
    } else if (auto shared_alloc = std::dynamic_pointer_cast<SharedAlloc>(expr)) {
        return generateSharedAlloc(shared_alloc);
    } else if (auto atomic_op = std::dynamic_pointer_cast<AtomicOp>(expr)) {
        return generateAtomicOp(atomic_op);
    } else {
        return generateLiteral(expr);
    }
}

std::string PTXGenerator::generateBinaryOp(std::shared_ptr<BinaryOp> op) {
    std::string left_ptx = generateExpression(op->left);
    std::string right_ptx = generateExpression(op->right);
    
    std::string ptx_op = getPTXOp(op->op);
    
    // Check if this is a comparison operation (returns predicate)
    bool is_comparison = (op->op == "==" || op->op == "!=" || op->op == "<" || 
                          op->op == ">" || op->op == "<=" || op->op == ">=");
    
    if (is_comparison) {
        // Comparison operations return predicates
        std::string result_reg = allocateRegister(".pred");
        std::string type = inferPTXType(op->left);
        
        // Ensure operands are in registers (load literals if needed)
        std::string left_reg = left_ptx;
        if (left_ptx.find("%") != 0) {
            // It's a literal, load into register
            left_reg = allocateRegister(type);
            pending_ptx_ << "mov" << type << " " << left_reg << ", " << left_ptx << ";\n";
        }
        
        std::string right_reg = right_ptx;
        if (right_ptx.find("%") != 0) {
            // It's a literal, load into register
            right_reg = allocateRegister(type);
            pending_ptx_ << "mov" << type << " " << right_reg << ", " << right_ptx << ";\n";
        }
        
        // Format: setp.op.type pred, src1, src2;
        pending_ptx_ << ptx_op << type << " " << result_reg << ", " 
            << left_reg << ", " << right_reg << ";\n";
        
        return result_reg;
    } else {
        // Arithmetic operations
        std::string type = inferPTXType(op->left);
        // If right operand is float, use float type
        std::string right_type = inferPTXType(op->right);
        if (right_type == ".f32" || type == ".f32") {
            type = ".f32";
        }
        
        std::string result_reg = allocateRegister(type);
        
        // Ensure operands are in registers (load literals if needed)
        std::string left_reg = left_ptx;
        if (left_ptx.find("%") != 0) {
            // It's a literal, load into register
            left_reg = allocateRegister(type);
            if (type == ".f32") {
                // Check if it's a float literal
                if (left_ptx.find(".") != std::string::npos || 
                    left_ptx.find("e") != std::string::npos || 
                    left_ptx.find("E") != std::string::npos) {
                    pending_ptx_ << "mov.f32 " << left_reg << ", 0f" << left_ptx << ";\n";
                } else {
                    // Integer to float conversion
                    std::string temp_reg = allocateRegister(".u32");
                    pending_ptx_ << "mov.u32 " << temp_reg << ", " << left_ptx << ";\n";
                    pending_ptx_ << "cvt.f32.u32 " << left_reg << ", " << temp_reg << ";\n";
                }
            } else {
                pending_ptx_ << "mov" << type << " " << left_reg << ", " << left_ptx << ";\n";
            }
        }
        
        std::string right_reg = right_ptx;
        if (right_ptx.find("%") != 0) {
            // It's a literal, load into register
            right_reg = allocateRegister(type);
            if (type == ".f32") {
                // Check if it's a float literal
                if (right_ptx.find(".") != std::string::npos || 
                    right_ptx.find("e") != std::string::npos || 
                    right_ptx.find("E") != std::string::npos) {
                    pending_ptx_ << "mov.f32 " << right_reg << ", 0f" << right_ptx << ";\n";
                } else {
                    // Integer to float conversion
                    std::string temp_reg = allocateRegister(".u32");
                    pending_ptx_ << "mov.u32 " << temp_reg << ", " << right_ptx << ";\n";
                    pending_ptx_ << "cvt.f32.u32 " << right_reg << ", " << temp_reg << ";\n";
                }
            } else {
                pending_ptx_ << "mov" << type << " " << right_reg << ", " << right_ptx << ";\n";
            }
        }
        
        // Format: op.type dest, src1, src2;
        pending_ptx_ << ptx_op << type << " " << result_reg << ", " 
            << left_reg << ", " << right_reg << ";\n";
        
        return result_reg;
    }
}

std::string PTXGenerator::generateUnaryOp(std::shared_ptr<UnaryOp> op) {
    std::stringstream ptx;
    
    std::string result_reg = allocateRegister();
    std::string operand_ptx = generateExpression(op->operand);
    
    if (op->op == "-") {
        ptx << "neg.f32 " << result_reg << ", " << operand_ptx << ";\n";
    } else if (op->op == "not") {
        ptx << "not.pred " << result_reg << ", " << operand_ptx << ";\n";
    } else if (op->op == "~") {
        ptx << "not.b32 " << result_reg << ", " << operand_ptx << ";\n";
    }
    
    return result_reg;
}

std::string PTXGenerator::generateFunctionCall(std::shared_ptr<FunctionCall> call) {
    // Handle built-in functions
    if (auto ident = std::dynamic_pointer_cast<Identifier>(call->function)) {
        if (ident->name == "float") {
            // Type conversion
            if (!call->arguments.empty()) {
                return generateExpression(call->arguments[0]);
            }
        } else if (ident->name == "syncthreads") {
            // CUDA synchronization barrier
            return generateBarrier();
        }
    }
    
    throw std::runtime_error("Function calls not yet fully supported in PTX generation");
}

std::string PTXGenerator::generateIndexAccess(std::shared_ptr<IndexAccess> access) {
    // Check if accessing shared memory
    std::string var_name;
    if (auto ident = std::dynamic_pointer_cast<Identifier>(access->array)) {
        var_name = ident->name;
    }
    
    // Check if this is a shared variable
    bool is_shared = shared_variables_.find(var_name) != shared_variables_.end();
    
    std::string index_ptx = generateExpression(access->index);
    std::string index_reg = allocateRegister(".u32");
    
    // Convert index to register if it's a literal
    if (index_ptx.find("%") != 0) {
        // It's a literal, load into register
        pending_ptx_ << "mov.u32 " << index_reg << ", " << index_ptx << ";\n";
    } else {
        index_reg = index_ptx;
    }
    
    // Load value from memory
    std::string result_reg = allocateRegister(".f32");
    
    if (is_shared) {
        // Use shared memory access
        std::string shared_name = shared_variables_[var_name].second;
        pending_ptx_ << "ld.shared.f32 " << result_reg << ", [" << shared_name << "+" << index_reg << "*4];\n";
    } else {
        // Use global memory access
        // For array access, the array name is the parameter name
        // Load the parameter into a register if not already loaded
        std::string base_reg;
        auto param_it = parameter_registers_.find(var_name);
        if (param_it != parameter_registers_.end()) {
            base_reg = param_it->second;
        } else {
            base_reg = allocateRegister(".u64");
            parameter_registers_[var_name] = base_reg;
            pending_ptx_ << "ld.param.u64 " << base_reg << ", [" << var_name << "];\n";
        }
        
        std::string offset_reg = allocateRegister(".u64");
        // offset = index * 4 (for float)
        pending_ptx_ << "mul.wide.u32 " << offset_reg << ", " << index_reg << ", 4;\n";
        
        // Calculate address: base + offset
        std::string addr_reg = allocateRegister(".u64");
        pending_ptx_ << "add.u64 " << addr_reg << ", " << base_reg << ", " << offset_reg << ";\n";
        
        pending_ptx_ << "ld.global.f32 " << result_reg << ", [" << addr_reg << "];\n";
    }
    
    return result_reg;
}

std::string PTXGenerator::generateBuiltInVariable(std::shared_ptr<BuiltInVariable> builtin) {
    // Built-in variables are already loaded into %tid, %ctaid, %ntid in generateKernelBody
    // Map MoonLight built-in variables to these registers
    if (builtin->name == "threadIdx_x") {
        return "%tid";
    } else if (builtin->name == "threadIdx_y") {
        // Need to load %tid.y separately
        std::string reg = allocateRegister(".u32");
        pending_ptx_ << "mov.u32 " << reg << ", %tid.y;\n";
        return reg;
    } else if (builtin->name == "threadIdx_z") {
        std::string reg = allocateRegister(".u32");
        pending_ptx_ << "mov.u32 " << reg << ", %tid.z;\n";
        return reg;
    } else if (builtin->name == "blockIdx_x") {
        return "%ctaid";
    } else if (builtin->name == "blockIdx_y") {
        std::string reg = allocateRegister(".u32");
        pending_ptx_ << "mov.u32 " << reg << ", %ctaid.y;\n";
        return reg;
    } else if (builtin->name == "blockIdx_z") {
        std::string reg = allocateRegister(".u32");
        pending_ptx_ << "mov.u32 " << reg << ", %ctaid.z;\n";
        return reg;
    } else if (builtin->name == "blockDim_x") {
        return "%ntid";
    } else if (builtin->name == "blockDim_y") {
        std::string reg = allocateRegister(".u32");
        pending_ptx_ << "mov.u32 " << reg << ", %ntid.y;\n";
        return reg;
    } else if (builtin->name == "blockDim_z") {
        std::string reg = allocateRegister(".u32");
        pending_ptx_ << "mov.u32 " << reg << ", %ntid.z;\n";
        return reg;
    } else if (builtin->name == "gridDim_x") {
        std::string reg = allocateRegister(".u32");
        pending_ptx_ << "mov.u32 " << reg << ", %nctaid.x;\n";
        return reg;
    } else if (builtin->name == "gridDim_y") {
        std::string reg = allocateRegister(".u32");
        pending_ptx_ << "mov.u32 " << reg << ", %nctaid.y;\n";
        return reg;
    } else if (builtin->name == "gridDim_z") {
        std::string reg = allocateRegister(".u32");
        pending_ptx_ << "mov.u32 " << reg << ", %nctaid.z;\n";
        return reg;
    }
    
    throw std::runtime_error("Unknown built-in variable: " + builtin->name);
}

std::string PTXGenerator::generateDeviceAlloc(std::shared_ptr<DeviceAlloc> alloc) {
    // Device allocation is handled at runtime, not in PTX
    // This should not appear in kernel code
    throw std::runtime_error("Device allocation should not appear in kernel code");
}

std::string PTXGenerator::generateSharedAlloc(std::shared_ptr<SharedAlloc> alloc) {
    // Shared memory allocation is handled in generateKernelBody()
    // This is called when shared[size] appears in an assignment
    // Return the PTX name of the shared array
    // Note: This should only be called during assignment processing
    // The actual declaration is done in generateKernelBody()
    
    // For now, return a placeholder - the actual variable name will be
    // resolved when processing the assignment
    return "__shared_temp";
}

std::string PTXGenerator::generateAtomicOp(std::shared_ptr<AtomicOp> atomic) {
    std::stringstream ptx;
    
    // Generate address expression
    std::string addr_ptx = generateExpression(atomic->address);
    std::string value_ptx = generateExpression(atomic->value);
    
    // For atomic operations, we need the address in a register
    std::string addr_reg = allocateRegister(".u64");
    
    // Check if address is an IndexAccess (array element)
    if (auto idx_access = std::dynamic_pointer_cast<IndexAccess>(atomic->address)) {
        // Calculate address from array and index
        std::string base_ptx = generateExpression(idx_access->array);
        std::string index_ptx = generateExpression(idx_access->index);
        std::string index_reg = allocateRegister(".u32");
        
        // Convert index to register if it's a literal
        if (index_ptx.find_first_not_of("0123456789") == std::string::npos) {
            ptx << "mov.u32 " << index_reg << ", " << index_ptx << ";\n";
        } else {
            index_reg = index_ptx;
        }
        
        // offset = index * 4 (for float)
        std::string offset_reg = allocateRegister(".u64");
        ptx << "mul.wide.u32 " << offset_reg << ", " << index_reg << ", 4;\n";
        
        // Load base pointer if it's a parameter
        if (base_ptx.find("%") != 0) {
            std::string base_reg = allocateRegister(".u64");
            ptx << "ld.param.u64 " << base_reg << ", [" << base_ptx << "];\n";
            ptx << "add.u64 " << addr_reg << ", " << base_reg << ", " << offset_reg << ";\n";
        } else {
            ptx << "add.u64 " << addr_reg << ", " << base_ptx << ", " << offset_reg << ";\n";
        }
    } else {
        // Address is already a pointer/register
        if (addr_ptx.find("%") == 0) {
            addr_reg = addr_ptx;
        } else {
            // Load parameter
            ptx << "ld.param.u64 " << addr_reg << ", [" << addr_ptx << "];\n";
        }
    }
    
    // Generate value register
    std::string value_reg = allocateRegister(".u32");
    if (value_ptx.find("%") == 0) {
        value_reg = value_ptx;
    } else {
        // Convert value to register
        ptx << "mov.u32 " << value_reg << ", " << value_ptx << ";\n";
    }
    
    // Generate atomic operation
    if (atomic->op == "add") {
        // atom.add.u32 [addr], value;
        ptx << "atom.add.u32 [" << addr_reg << "], " << value_reg << ";\n";
    } else if (atomic->op == "sub") {
        ptx << "atom.sub.u32 [" << addr_reg << "], " << value_reg << ";\n";
    } else {
        throw std::runtime_error("Unsupported atomic operation: " + atomic->op);
    }
    
    // Atomic operations return the old value, so we need a result register
    std::string result_reg = allocateRegister(".u32");
    // The atom.add instruction stores the old value in the result
    // We need to capture it - but PTX atom.add doesn't return a value directly
    // For now, we'll just execute the operation
    // TODO: Handle return value if needed
    
    return result_reg;
}

std::string PTXGenerator::generateLiteral(ExprPtr literal) {
    if (auto int_lit = std::dynamic_pointer_cast<IntegerLiteral>(literal)) {
        return std::to_string(int_lit->value);
    } else if (auto float_lit = std::dynamic_pointer_cast<FloatLiteral>(literal)) {
        return std::to_string(float_lit->value);
    } else if (auto str_lit = std::dynamic_pointer_cast<StringLiteral>(literal)) {
        // Strings are not directly supported in PTX
        throw std::runtime_error("String literals not supported in PTX");
    } else if (auto bool_lit = std::dynamic_pointer_cast<BooleanLiteral>(literal)) {
        return bool_lit->value ? "1" : "0";
    } else if (auto ident = std::dynamic_pointer_cast<Identifier>(literal)) {
        return getVariableRegister(ident->name);
    }
    
    throw std::runtime_error("Unknown literal type");
}

std::string PTXGenerator::allocateRegister(const std::string& type) {
    std::stringstream reg;
    // Use different prefixes for different types
    if (type == ".f32") {
        reg << "%f" << register_counter_++;
    } else if (type == ".u64" || type == ".s64") {
        reg << "%rd" << register_counter_++;
    } else if (type == ".pred") {
        reg << "%p" << register_counter_++;
    } else {
        reg << "%r" << register_counter_++;
    }
    std::string reg_name = reg.str();
    register_types_[reg_name] = type;
    used_registers_.insert(reg_name);
    return reg_name;
}

std::string PTXGenerator::getVariableRegister(const std::string& var_name) {
    auto it = variable_registers_.find(var_name);
    if (it != variable_registers_.end()) {
        return it->second;
    }
    return "";
}

void PTXGenerator::setVariableRegister(const std::string& var_name, const std::string& reg) {
    variable_registers_[var_name] = reg;
}


std::string PTXGenerator::inferPTXType(ExprPtr expr) {
    if (auto int_lit = std::dynamic_pointer_cast<IntegerLiteral>(expr)) {
        return ".u32";
    } else if (auto float_lit = std::dynamic_pointer_cast<FloatLiteral>(expr)) {
        return ".f32";
    } else if (auto bool_lit = std::dynamic_pointer_cast<BooleanLiteral>(expr)) {
        return ".pred";
    } else if (auto bin_op = std::dynamic_pointer_cast<BinaryOp>(expr)) {
        // For binary operations, infer from operands
        std::string left_type = inferPTXType(bin_op->left);
        std::string right_type = inferPTXType(bin_op->right);
        // If either is float, result is float
        if (left_type == ".f32" || right_type == ".f32") {
            return ".f32";
        }
        return left_type;  // Default to left type
    } else if (auto idx = std::dynamic_pointer_cast<IndexAccess>(expr)) {
        // Array access - assume float for now (can be improved with type info)
        return ".f32";
    } else if (auto ident = std::dynamic_pointer_cast<Identifier>(expr)) {
        // Check if variable is already registered and get its type
        auto reg_it = variable_registers_.find(ident->name);
        if (reg_it != variable_registers_.end()) {
            auto type_it = register_types_.find(reg_it->second);
            if (type_it != register_types_.end()) {
                return type_it->second;
            }
        }
        // Default to float for variables (can be improved)
        return ".f32";
    }
    
    // Default to u32
    return ".u32";
}

std::string PTXGenerator::inferPTXTypeFromLiteral(ExprPtr literal) {
    return inferPTXType(literal);
}

std::string PTXGenerator::generateLabel(const std::string& prefix) {
    std::stringstream label;
    label << "$" << prefix << label_counter_++;
    return label.str();
}

std::string PTXGenerator::getPTXOp(const std::string& op) {
    if (op == "+") return "add";
    else if (op == "-") return "sub";
    else if (op == "*") return "mul";
    else if (op == "/") return "div";
    else if (op == "%") return "rem";
    else if (op == "**") return "pow";  // Power
    else if (op == "==") return "setp.eq";
    else if (op == "!=") return "setp.ne";
    else if (op == "<") return "setp.lt";
    else if (op == ">") return "setp.gt";
    else if (op == "<=") return "setp.le";
    else if (op == ">=") return "setp.ge";
    else if (op == "&") return "and";
    else if (op == "|") return "or";
    else if (op == "^") return "xor";
    else if (op == "<<") return "shl";
    else if (op == ">>") return "shr";
    
    return "add";  // Default
}

std::string PTXGenerator::getPTXType(const std::string& type) {
    if (type == "int" || type == "u32") return ".u32";
    else if (type == "float" || type == "f32") return ".f32";
    else if (type == "double" || type == "f64") return ".f64";
    else if (type == "bool" || type == "pred") return ".pred";
    
    return ".u32";  // Default
}

std::string PTXGenerator::generateBarrier() {
    return "bar.sync 0;\n";
}

} // namespace moonlight

