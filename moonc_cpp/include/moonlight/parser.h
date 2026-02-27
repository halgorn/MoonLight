#pragma once

#include "moonlight/lexer.h"
#include "moonlight/ast.h"
#include "moonlight/token.h"
#include <vector>
#include <memory>

namespace moonlight {

class Parser {
public:
    explicit Parser(const std::vector<Token>& tokens, bool debug = false);
    
    // Parse entire program
    std::shared_ptr<Program> parseProgram();
    
private:
    std::vector<Token> tokens_;
    size_t position_;
    bool debug_;
    int recursion_depth_;
    int max_recursion_depth_;
    int loop_iterations_;
    int max_loop_iterations_;
    
    // Token management
    Token currentToken() const;
    Token peekToken(int offset = 1) const;
    void advance();
    bool isAtEnd() const;
    bool check(TokenType type) const;
    bool match(TokenType type);
    Token consume(TokenType type, const std::string& error_message);
    
    // Parsing methods
    StmtPtr parseStatement();
    StmtPtr parseAssignment();
    StmtPtr parseIfStatement();
    StmtPtr parseWhileStatement();
    StmtPtr parseForStatement();
    StmtPtr parseFunctionDef();
    StmtPtr parseReturnStatement();
    StmtPtr parsePrintStatement();
    StmtPtr parseExpressionStatement();
    std::vector<StmtPtr> parseBlock();
    
    // Expression parsing (precedence climbing)
    ExprPtr parseExpression();
    ExprPtr parseLogicalOr();
    ExprPtr parseLogicalAnd();
    ExprPtr parseEquality();
    ExprPtr parseComparison();
    ExprPtr parseBitwiseOr();
    ExprPtr parseBitwiseXor();
    ExprPtr parseBitwiseAnd();
    ExprPtr parseShift();
    ExprPtr parseTerm();
    ExprPtr parseFactor();
    ExprPtr parsePower();
    ExprPtr parseUnary();
    ExprPtr parsePostfix();
    ExprPtr parsePrimary();
    
    // Helper methods
    ExprPtr parseFunctionCall(ExprPtr function);
    ExprPtr parseIndexAccess(ExprPtr array);
    ExprPtr parseMemberAccess(ExprPtr object);
    std::vector<ExprPtr> parseArgumentList();
    std::vector<std::string> parseParameterList();
    ExprPtr parseListLiteral();
    ExprPtr parseLambda();
    
    // CUDA parsing methods
    StmtPtr parseCudaKernelDef();
    StmtPtr parseGpuLaunch();
    StmtPtr parseMemoryTransfer();
    StmtPtr parseFreeStatement();
    ExprPtr parseDeviceAlloc();
    ExprPtr parseSharedAlloc();
    ExprPtr parseBuiltInVariable();
    std::vector<std::string> parseDecorators();
    
    // Error handling
    void reportError(const std::string& message);
    void synchronize();
    
    // Debug and safety
    void logDebug(const std::string& message, const std::string& function_name) const;
    void checkRecursionLimit(const std::string& function_name);
    void checkLoopLimit(const std::string& function_name);
    void enterRecursion(const std::string& function_name);
    void exitRecursion();
};

} // namespace moonlight







