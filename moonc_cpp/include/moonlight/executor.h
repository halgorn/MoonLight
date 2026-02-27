#pragma once

#include "moonlight/ast.h"
#include "moonlight/value.h"
#include "moonlight/cuda_loader.h"
#include <cuda.h>  // For CUmodule type
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <stack>

namespace moonlight {

class MemoryManager;

class Executor {
public:
    Executor();
    ~Executor();
    
    // Execute entire program
    void executeProgram(std::shared_ptr<Program> program);
    
    // Evaluate expression and return Value
    Value evaluateExpression(ExprPtr expr);
    
    // Execute statement
    void executeStatement(StmtPtr stmt);
    
    // Call function
    Value callFunction(const std::string& name, const std::vector<Value>& args);
    
    // Set memory manager (for GPU operations)
    void setMemoryManager(MemoryManager* mm) { memory_manager_ = mm; }
    
    // Set CUDA loader (for kernel execution)
    void setCUDALoader(CUDALoader* loader) { cuda_loader_ = loader; }
    void setPTXModule(CUmodule module) { ptx_module_ = module; }
    
private:
    // Variable scope management
    std::stack<std::map<std::string, Value>> scopes_;
    std::map<std::string, std::shared_ptr<FunctionDef>> functions_;
    std::map<std::string, std::shared_ptr<CudaKernelDef>> kernels_;
    
    MemoryManager* memory_manager_;
    CUDALoader* cuda_loader_;
    CUmodule ptx_module_;
    
    // Track device allocation sizes by pointer
    std::map<void*, size_t> device_ptr_sizes_;
    
    // GPU timing events
    CUevent gpu_start_event_;
    CUevent gpu_stop_event_;
    bool gpu_timer_started_;
    
    // Scope management
    void pushScope();
    void popScope();
    void setVariable(const std::string& name, const Value& value);
    Value getVariable(const std::string& name);
    bool hasVariable(const std::string& name);
    
    // Expression evaluation
    Value evaluateLiteral(ExprPtr literal);
    Value evaluateBinaryOp(std::shared_ptr<BinaryOp> op);
    Value evaluateUnaryOp(std::shared_ptr<UnaryOp> op);
    Value evaluateFunctionCall(std::shared_ptr<FunctionCall> call);
    Value evaluateIndexAccess(std::shared_ptr<IndexAccess> access);
    Value evaluateMemberAccess(std::shared_ptr<MemberAccess> access);
    Value evaluateBuiltInVariable(std::shared_ptr<BuiltInVariable> builtin);
    Value evaluateDeviceAlloc(std::shared_ptr<DeviceAlloc> alloc);
    Value evaluateSharedAlloc(std::shared_ptr<SharedAlloc> alloc);
    
    // Statement execution
    void executeAssignment(std::shared_ptr<Assignment> assign);
    void executeIfStatement(std::shared_ptr<IfStatement> if_stmt);
    void executeWhileStatement(std::shared_ptr<WhileStatement> while_stmt);
    void executeForStatement(std::shared_ptr<ForStatement> for_stmt);
    void executeReturnStatement(std::shared_ptr<ReturnStatement> ret);
    void executePrintStatement(std::shared_ptr<PrintStatement> print);
    void executeFunctionDef(std::shared_ptr<FunctionDef> func);
    void executeCudaKernelDef(std::shared_ptr<CudaKernelDef> kernel);
    void executeGpuLaunch(std::shared_ptr<GpuLaunch> launch);
    void executeMemoryTransfer(std::shared_ptr<MemoryTransfer> transfer);
    void executeFreeStatement(std::shared_ptr<FreeStatement> free_stmt);
    
    // Helper methods
    bool isTruthy(const Value& v);
    Value performBinaryOperation(const std::string& op, const Value& left, const Value& right);
    Value performUnaryOperation(const std::string& op, const Value& operand);
    
    // Return value handling
    Value return_value_;
    bool has_return_;
    void setReturnValue(const Value& v);
    Value getReturnValue();
    void clearReturn();
};

} // namespace moonlight

