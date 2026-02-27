#pragma once

#include "moonlight/ast.h"
#include <string>
#include <vector>
#include <map>
#include <set>
#include <memory>

namespace moonlight {

class PTXGenerator {
public:
    PTXGenerator();
    
    // Generate PTX from AST
    std::string generatePTX(std::shared_ptr<Program> program);
    
    // Set compute capability (e.g., "sm_75", "sm_86")
    void setComputeCapability(const std::string& cc);
    
    // Set PTX version (default: "7.0")
    void setPTXVersion(const std::string& version);
    
private:
    std::string ptx_version_;
    std::string compute_capability_;
    int register_counter_;
    int label_counter_;
    std::map<std::string, std::string> variable_registers_;  // variable name -> register name
    std::map<std::string, std::pair<size_t, std::string>> shared_variables_;  // var_name -> (size, ptx_name)
    std::map<std::string, std::string> register_types_;  // register name -> type (e.g., ".u32", ".f32")
    std::set<std::string> used_registers_;  // track which registers are used
    std::map<std::string, std::string> parameter_registers_;  // parameter name -> register name (for loaded params)
    std::stringstream pending_ptx_;  // PTX code that needs to be output before the current instruction
    
    // PTX header generation
    std::string generateHeader();
    
    // Kernel generation
    std::string generateKernel(std::shared_ptr<CudaKernelDef> kernel);
    std::string generateKernelParameters(std::shared_ptr<CudaKernelDef> kernel);
    std::string generateKernelBody(std::vector<StmtPtr> body);
    
    // Statement generation
    std::string generateStatement(StmtPtr stmt);
    std::string generateAssignment(std::shared_ptr<Assignment> assign);
    std::string generateIfStatement(std::shared_ptr<IfStatement> if_stmt);
    std::string generateWhileStatement(std::shared_ptr<WhileStatement> while_stmt);
    std::string generateForStatement(std::shared_ptr<ForStatement> for_stmt);
    std::string generateReturnStatement(std::shared_ptr<ReturnStatement> ret);
    
    // Expression generation
    std::string generateExpression(ExprPtr expr);
    std::string generateBinaryOp(std::shared_ptr<BinaryOp> op);
    std::string generateUnaryOp(std::shared_ptr<UnaryOp> op);
    std::string generateFunctionCall(std::shared_ptr<FunctionCall> call);
    std::string generateIndexAccess(std::shared_ptr<IndexAccess> access);
    std::string generateBuiltInVariable(std::shared_ptr<BuiltInVariable> builtin);
    std::string generateDeviceAlloc(std::shared_ptr<DeviceAlloc> alloc);
    std::string generateSharedAlloc(std::shared_ptr<SharedAlloc> alloc);
    std::string generateAtomicOp(std::shared_ptr<AtomicOp> atomic);
    
    // Literal generation
    std::string generateLiteral(ExprPtr literal);
    
    // Register management
    std::string allocateRegister(const std::string& type = ".u32");
    std::string getVariableRegister(const std::string& var_name);
    void setVariableRegister(const std::string& var_name, const std::string& reg);
    
    // Type inference
    std::string inferPTXType(ExprPtr expr);
    std::string inferPTXTypeFromLiteral(ExprPtr literal);
    
    // Label generation
    std::string generateLabel(const std::string& prefix = "L");
    
    // Synchronization
    std::string generateBarrier();
    
    // Helper methods
    std::string getPTXOp(const std::string& op);
    std::string getPTXType(const std::string& type);
};

} // namespace moonlight

