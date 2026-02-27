#pragma once

#include <string>
#include <vector>
#include <memory>
#include <variant>

namespace moonlight {

// Forward declarations
class ASTNode;
class Expression;
class Statement;

using ASTNodePtr = std::shared_ptr<ASTNode>;
using ExprPtr = std::shared_ptr<Expression>;
using StmtPtr = std::shared_ptr<Statement>;

// Base AST Node
class ASTNode {
public:
    virtual ~ASTNode() = default;
    virtual std::string toString() const = 0;
};

// Expressions
class Expression : public ASTNode {
public:
    virtual ~Expression() = default;
};

// Literal values
class IntegerLiteral : public Expression {
public:
    int value;
    explicit IntegerLiteral(int v) : value(v) {}
    std::string toString() const override;
};

class FloatLiteral : public Expression {
public:
    double value;
    explicit FloatLiteral(double v) : value(v) {}
    std::string toString() const override;
};

class StringLiteral : public Expression {
public:
    std::string value;
    explicit StringLiteral(const std::string& v) : value(v) {}
    std::string toString() const override;
};

class BooleanLiteral : public Expression {
public:
    bool value;
    explicit BooleanLiteral(bool v) : value(v) {}
    std::string toString() const override;
};

class NoneLiteral : public Expression {
public:
    std::string toString() const override;
};

// Identifier
class Identifier : public Expression {
public:
    std::string name;
    explicit Identifier(const std::string& n) : name(n) {}
    std::string toString() const override;
};

// Binary operations
class BinaryOp : public Expression {
public:
    std::string op;
    ExprPtr left;
    ExprPtr right;
    
    BinaryOp(const std::string& o, ExprPtr l, ExprPtr r)
        : op(o), left(std::move(l)), right(std::move(r)) {}
    std::string toString() const override;
};

// Unary operations
class UnaryOp : public Expression {
public:
    std::string op;
    ExprPtr operand;
    
    UnaryOp(const std::string& o, ExprPtr expr)
        : op(o), operand(std::move(expr)) {}
    std::string toString() const override;
};

// Function call
class FunctionCall : public Expression {
public:
    ExprPtr function;
    std::vector<ExprPtr> arguments;
    
    FunctionCall(ExprPtr func, std::vector<ExprPtr> args)
        : function(std::move(func)), arguments(std::move(args)) {}
    std::string toString() const override;
};

// Array/List access
class IndexAccess : public Expression {
public:
    ExprPtr array;
    ExprPtr index;
    
    IndexAccess(ExprPtr arr, ExprPtr idx)
        : array(std::move(arr)), index(std::move(idx)) {}
    std::string toString() const override;
};

// Member access
class MemberAccess : public Expression {
public:
    ExprPtr object;
    std::string member;
    
    MemberAccess(ExprPtr obj, const std::string& mem)
        : object(std::move(obj)), member(mem) {}
    std::string toString() const override;
};

// Atomic operation
class AtomicOp : public Expression {
public:
    std::string op;  // e.g., "add", "sub", "min", "max"
    ExprPtr address;  // Memory address (pointer or index access)
    ExprPtr value;    // Value to add/sub/etc.
    
    AtomicOp(const std::string& operation, ExprPtr addr, ExprPtr val)
        : op(operation), address(std::move(addr)), value(std::move(val)) {}
    std::string toString() const override;
};

// List literal
class ListLiteral : public Expression {
public:
    std::vector<ExprPtr> elements;
    
    explicit ListLiteral(std::vector<ExprPtr> elems)
        : elements(std::move(elems)) {}
    std::string toString() const override;
};

// Lambda expression
class LambdaExpr : public Expression {
public:
    std::vector<std::string> parameters;
    ExprPtr body;
    
    LambdaExpr(std::vector<std::string> params, ExprPtr b)
        : parameters(std::move(params)), body(std::move(b)) {}
    std::string toString() const override;
};

// Statements
class Statement : public ASTNode {
public:
    virtual ~Statement() = default;
};

// Expression statement
class ExpressionStmt : public Statement {
public:
    ExprPtr expression;
    
    explicit ExpressionStmt(ExprPtr expr) : expression(std::move(expr)) {}
    std::string toString() const override;
};

// Assignment
class Assignment : public Statement {
public:
    std::string variable;
    ExprPtr value;
    ExprPtr array_index;  // Optional: if set, this is an array element assignment: arr[i] = value
    
    Assignment(const std::string& var, ExprPtr val, ExprPtr arr_idx = nullptr)
        : variable(var), value(std::move(val)), array_index(std::move(arr_idx)) {}
    std::string toString() const override;
};

// If statement
class IfStatement : public Statement {
public:
    ExprPtr condition;
    std::vector<StmtPtr> then_block;
    std::vector<StmtPtr> else_block;
    
    IfStatement(ExprPtr cond, std::vector<StmtPtr> then_b, std::vector<StmtPtr> else_b = {})
        : condition(std::move(cond)), then_block(std::move(then_b)), else_block(std::move(else_b)) {}
    std::string toString() const override;
};

// While loop
class WhileStatement : public Statement {
public:
    ExprPtr condition;
    std::vector<StmtPtr> body;
    
    WhileStatement(ExprPtr cond, std::vector<StmtPtr> b)
        : condition(std::move(cond)), body(std::move(b)) {}
    std::string toString() const override;
};

// For loop
class ForStatement : public Statement {
public:
    StmtPtr init;
    ExprPtr condition;
    StmtPtr increment;
    std::vector<StmtPtr> body;
    
    ForStatement(StmtPtr i, ExprPtr cond, StmtPtr inc, std::vector<StmtPtr> b)
        : init(std::move(i)), condition(std::move(cond)), 
          increment(std::move(inc)), body(std::move(b)) {}
    std::string toString() const override;
};

// Function definition
class FunctionDef : public Statement {
public:
    std::string name;
    std::vector<std::string> parameters;
    std::vector<StmtPtr> body;
    
    FunctionDef(const std::string& n, std::vector<std::string> params, std::vector<StmtPtr> b)
        : name(n), parameters(std::move(params)), body(std::move(b)) {}
    std::string toString() const override;
};

// Return statement
class ReturnStatement : public Statement {
public:
    ExprPtr value;
    
    explicit ReturnStatement(ExprPtr val = nullptr) : value(std::move(val)) {}
    std::string toString() const override;
};

// Break/Continue
class BreakStatement : public Statement {
public:
    std::string toString() const override;
};

class ContinueStatement : public Statement {
public:
    std::string toString() const override;
};

// Print statement (built-in)
class PrintStatement : public Statement {
public:
    std::vector<ExprPtr> expressions;
    
    explicit PrintStatement(std::vector<ExprPtr> exprs)
        : expressions(std::move(exprs)) {}
    std::string toString() const override;
};

// CUDA Expressions and Statements

// Built-in CUDA variable (threadIdx_x, blockIdx_x, etc)
class BuiltInVariable : public Expression {
public:
    std::string name;  // e.g., "threadIdx_x", "blockIdx_x"
    
    explicit BuiltInVariable(const std::string& n) : name(n) {}
    std::string toString() const override;
};

// Device allocation: device[size]
class DeviceAlloc : public Expression {
public:
    ExprPtr size;
    
    explicit DeviceAlloc(ExprPtr s) : size(std::move(s)) {}
    std::string toString() const override;
};

// Shared memory allocation: shared[size]
class SharedAlloc : public Expression {
public:
    ExprPtr size;
    
    explicit SharedAlloc(ExprPtr s) : size(std::move(s)) {}
    std::string toString() const override;
};

// CUDA Kernel definition: cuda kernel def name(params) { body }
class CudaKernelDef : public Statement {
public:
    std::string name;
    std::vector<std::string> parameters;
    std::vector<StmtPtr> body;
    bool is_persistent;
    std::vector<std::string> decorators;  // @persistent, @optimize, etc
    
    CudaKernelDef(const std::string& n, std::vector<std::string> params, 
                  std::vector<StmtPtr> b, bool persistent = false,
                  std::vector<std::string> decs = {})
        : name(n), parameters(std::move(params)), body(std::move(b)),
          is_persistent(persistent), decorators(std::move(decs)) {}
    std::string toString() const override;
};

// GPU Kernel launch: gpu[blocks, threads] kernel(args)
class GpuLaunch : public Statement {
public:
    ExprPtr blocks;
    ExprPtr threads;
    ExprPtr kernel;  // Function call to kernel
    int gpu_id;  // For multi-GPU: gpu[0], gpu[1], etc (-1 for default)
    
    GpuLaunch(ExprPtr b, ExprPtr t, ExprPtr k, int gpu = -1)
        : blocks(std::move(b)), threads(std::move(t)), 
          kernel(std::move(k)), gpu_id(gpu) {}
    std::string toString() const override;
};

// Memory transfer: d_a <- h_a (left arrow)
class MemoryTransfer : public Statement {
public:
    ExprPtr destination;  // GPU memory
    ExprPtr source;       // Host memory
    bool is_host_to_device;  // true: H->D, false: D->H
    
    MemoryTransfer(ExprPtr dest, ExprPtr src, bool h2d = true)
        : destination(std::move(dest)), source(std::move(src)), 
          is_host_to_device(h2d) {}
    std::string toString() const override;
};

// Free statement: free(d_a)
class FreeStatement : public Statement {
public:
    ExprPtr variable;
    
    explicit FreeStatement(ExprPtr var) : variable(std::move(var)) {}
    std::string toString() const override;
};

// Program (root node)
class Program : public ASTNode {
public:
    std::vector<StmtPtr> statements;
    
    explicit Program(std::vector<StmtPtr> stmts = {})
        : statements(std::move(stmts)) {}
    std::string toString() const override;
};

} // namespace moonlight







