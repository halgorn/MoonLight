#include "moonlight/ast.h"
#include <sstream>

namespace moonlight {

// IntegerLiteral
std::string IntegerLiteral::toString() const {
    return std::to_string(value);
}

// FloatLiteral
std::string FloatLiteral::toString() const {
    return std::to_string(value);
}

// StringLiteral
std::string StringLiteral::toString() const {
    return "\"" + value + "\"";
}

// BooleanLiteral
std::string BooleanLiteral::toString() const {
    return value ? "True" : "False";
}

// NoneLiteral
std::string NoneLiteral::toString() const {
    return "None";
}

// Identifier
std::string Identifier::toString() const {
    return name;
}

// BinaryOp
std::string BinaryOp::toString() const {
    std::stringstream ss;
    ss << "(" << left->toString() << " " << op << " " << right->toString() << ")";
    return ss.str();
}

// UnaryOp
std::string UnaryOp::toString() const {
    return "(" + op + operand->toString() + ")";
}

// FunctionCall
std::string FunctionCall::toString() const {
    std::stringstream ss;
    ss << function->toString() << "(";
    for (size_t i = 0; i < arguments.size(); ++i) {
        if (i > 0) ss << ", ";
        ss << arguments[i]->toString();
    }
    ss << ")";
    return ss.str();
}

// IndexAccess
std::string IndexAccess::toString() const {
    return array->toString() + "[" + index->toString() + "]";
}

// MemberAccess
std::string MemberAccess::toString() const {
    return object->toString() + "." + member;
}

// ListLiteral
std::string ListLiteral::toString() const {
    std::stringstream ss;
    ss << "[";
    for (size_t i = 0; i < elements.size(); ++i) {
        if (i > 0) ss << ", ";
        ss << elements[i]->toString();
    }
    ss << "]";
    return ss.str();
}

// LambdaExpr
std::string LambdaExpr::toString() const {
    std::stringstream ss;
    ss << "lambda(";
    for (size_t i = 0; i < parameters.size(); ++i) {
        if (i > 0) ss << ", ";
        ss << parameters[i];
    }
    ss << ") " << body->toString();
    return ss.str();
}

// ExpressionStmt
std::string ExpressionStmt::toString() const {
    return expression->toString();
}

// Assignment
std::string Assignment::toString() const {
    if (array_index) {
        return variable + "[" + array_index->toString() + "] = " + value->toString();
    }
    return variable + " = " + value->toString();
}

// IfStatement
std::string IfStatement::toString() const {
    std::stringstream ss;
    ss << "if (" << condition->toString() << ") { ... }";
    if (!else_block.empty()) {
        ss << " else { ... }";
    }
    return ss.str();
}

// WhileStatement
std::string WhileStatement::toString() const {
    return "while (" + condition->toString() + ") { ... }";
}

// ForStatement
std::string ForStatement::toString() const {
    return "for (...) { ... }";
}

// FunctionDef
std::string FunctionDef::toString() const {
    std::stringstream ss;
    ss << "def " << name << "(";
    for (size_t i = 0; i < parameters.size(); ++i) {
        if (i > 0) ss << ", ";
        ss << parameters[i];
    }
    ss << ") { ... }";
    return ss.str();
}

// ReturnStatement
std::string ReturnStatement::toString() const {
    if (value) {
        return "return " + value->toString();
    }
    return "return";
}

// BreakStatement
std::string BreakStatement::toString() const {
    return "break";
}

// ContinueStatement
std::string ContinueStatement::toString() const {
    return "continue";
}

// PrintStatement
std::string PrintStatement::toString() const {
    std::stringstream ss;
    ss << "print(";
    for (size_t i = 0; i < expressions.size(); ++i) {
        if (i > 0) ss << ", ";
        ss << expressions[i]->toString();
    }
    ss << ")";
    return ss.str();
}

// BuiltInVariable
std::string BuiltInVariable::toString() const {
    return name;
}

// DeviceAlloc
std::string DeviceAlloc::toString() const {
    return "device[" + size->toString() + "]";
}

// SharedAlloc
std::string AtomicOp::toString() const {
    return "atomic" + op + "(" + address->toString() + ", " + value->toString() + ")";
}

std::string SharedAlloc::toString() const {
    return "shared[" + size->toString() + "]";
}

// CudaKernelDef
std::string CudaKernelDef::toString() const {
    std::stringstream ss;
    ss << "cuda kernel def " << name << "(";
    for (size_t i = 0; i < parameters.size(); ++i) {
        if (i > 0) ss << ", ";
        ss << parameters[i];
    }
    ss << ") { ... }";
    if (is_persistent) {
        ss << " [persistent]";
    }
    return ss.str();
}

// GpuLaunch
std::string GpuLaunch::toString() const {
    std::stringstream ss;
    if (gpu_id >= 0) {
        ss << "gpu[" << gpu_id << "]";
    }
    ss << "gpu[" << blocks->toString() << ", " << threads->toString() << "] " 
       << kernel->toString();
    return ss.str();
}

// MemoryTransfer
std::string MemoryTransfer::toString() const {
    if (is_host_to_device) {
        return destination->toString() + " <- " + source->toString();
    } else {
        return source->toString() + " <- " + destination->toString();
    }
}

// FreeStatement
std::string FreeStatement::toString() const {
    return "free(" + variable->toString() + ")";
}

// Program
std::string Program::toString() const {
    std::stringstream ss;
    ss << "Program {\n";
    for (const auto& stmt : statements) {
        ss << "  " << stmt->toString() << "\n";
    }
    ss << "}";
    return ss.str();
}

} // namespace moonlight







