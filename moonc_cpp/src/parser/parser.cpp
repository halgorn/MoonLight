#include "moonlight/parser.h"
#include <iostream>
#include <stdexcept>

namespace moonlight {

Parser::Parser(const std::vector<Token>& tokens, bool debug)
    : tokens_(tokens), position_(0), debug_(debug), 
      recursion_depth_(0), max_recursion_depth_(1000),
      loop_iterations_(0), max_loop_iterations_(10000) {
    if (debug_) {
        std::cout << "[DEBUG PARSER] Constructor called with " << tokens.size() << " tokens" << std::endl;
        std::cout.flush();
    }
}

std::shared_ptr<Program> Parser::parseProgram() {
    logDebug("START parseProgram", "parseProgram");
    logDebug("Total tokens: " + std::to_string(tokens_.size()), "parseProgram");
    
    auto program = std::make_shared<Program>();
    
    int statement_count = 0;
    logDebug("About to enter while loop", "parseProgram");
    logDebug("isAtEnd() check: position=" + std::to_string(position_) + " tokens_.size()=" + std::to_string(tokens_.size()), "parseProgram");
    
    while (!isAtEnd()) {
        logDebug("Loop iteration, statement " + std::to_string(statement_count) + ", position=" + std::to_string(position_), "parseProgram");
        try {
            logDebug("About to call parseStatement()", "parseProgram");
            auto stmt = parseStatement();
            logDebug("parseStatement() returned successfully", "parseProgram");
            if (stmt) {
                program->statements.push_back(stmt);
                statement_count++;
            } else {
                // parseStatement() returned nullptr, which means we're at EOF
                logDebug("parseStatement() returned nullptr (EOF), breaking loop", "parseProgram");
                break;
            }
        } catch (const std::exception& e) {
            logDebug("Exception caught: " + std::string(e.what()), "parseProgram");
            reportError(e.what());
            synchronize();
        }
    }
    
    logDebug("END parseProgram, parsed " + std::to_string(statement_count) + " statements", "parseProgram");
    return program;
}

// Token Management
Token Parser::currentToken() const {
    if (tokens_.empty()) {
        Token eof;
        eof.type = TokenType::EOF_TOKEN;
        eof.value = "";
        eof.line = 0;
        return eof;
    }
    if (position_ >= tokens_.size()) {
        return tokens_.back();
    }
    return tokens_[position_];
}

Token Parser::peekToken(int offset) const {
    if (tokens_.empty()) {
        // Return EOF token if tokens list is empty
        Token eof;
        eof.type = TokenType::EOF_TOKEN;
        eof.value = "";
        eof.line = 0;
        return eof;
    }
    
    size_t pos = position_ + offset;
    if (pos >= tokens_.size()) {
        // Return last token (should be EOF)
        return tokens_.back();
    }
    return tokens_[pos];
}

void Parser::advance() {
    if (!isAtEnd()) {
        position_++;
    }
}

bool Parser::isAtEnd() const {
    if (position_ >= tokens_.size()) {
        return true;
    }
    if (tokens_.empty()) {
        return true;
    }
    return currentToken().type == TokenType::EOF_TOKEN;
}

bool Parser::check(TokenType type) const {
    if (isAtEnd()) return false;
    return currentToken().type == type;
}

bool Parser::match(TokenType type) {
    if (check(type)) {
        advance();
        return true;
    }
    return false;
}

Token Parser::consume(TokenType type, const std::string& error_message) {
    if (check(type)) {
        Token token = currentToken();
        advance();
        return token;
    }
    throw std::runtime_error(error_message + " at line " + 
                           std::to_string(currentToken().line));
}

// Statement Parsing
StmtPtr Parser::parseStatement() {
    enterRecursion("parseStatement");
    logDebug("START", "parseStatement");
    
    // CUDA keywords
    if (match(TokenType::CUDA)) {
        if (match(TokenType::KERNEL) && match(TokenType::DEF)) {
            auto result = parseCudaKernelDef();
            exitRecursion();
            logDebug("END (cuda kernel)", "parseStatement");
            return result;
        }
        // If just "cuda" without "kernel def", treat as identifier
        exitRecursion();
        throw std::runtime_error("Expected 'kernel def' after 'cuda'");
    }
    
    if (match(TokenType::GPU)) {
        auto result = parseGpuLaunch();
        exitRecursion();
        logDebug("END (gpu launch)", "parseStatement");
        return result;
    }
    
    if (match(TokenType::FREE)) {
        auto result = parseFreeStatement();
        exitRecursion();
        logDebug("END (free)", "parseStatement");
        return result;
    }
    
    // Keywords
    if (match(TokenType::IF)) {
        auto result = parseIfStatement();
        exitRecursion();
        logDebug("END (if)", "parseStatement");
        return result;
    }
    if (match(TokenType::WHILE)) {
        auto result = parseWhileStatement();
        exitRecursion();
        logDebug("END (while)", "parseStatement");
        return result;
    }
    if (match(TokenType::FOR)) {
        auto result = parseForStatement();
        exitRecursion();
        logDebug("END (for)", "parseStatement");
        return result;
    }
    if (match(TokenType::DEF)) {
        auto result = parseFunctionDef();
        exitRecursion();
        logDebug("END (def)", "parseStatement");
        return result;
    }
    if (match(TokenType::RETURN)) {
        auto result = parseReturnStatement();
        exitRecursion();
        logDebug("END (return)", "parseStatement");
        return result;
    }
    if (match(TokenType::BREAK)) {
        auto result = std::make_shared<BreakStatement>();
        exitRecursion();
        logDebug("END (break)", "parseStatement");
        return result;
    }
    if (match(TokenType::CONTINUE)) {
        auto result = std::make_shared<ContinueStatement>();
        exitRecursion();
        logDebug("END (continue)", "parseStatement");
        return result;
    }
    
    // Check for print (built-in function special case)
    if (check(TokenType::IDENTIFIER) && currentToken().value == "print") {
        auto result = parsePrintStatement();
        exitRecursion();
        logDebug("END (print)", "parseStatement");
        return result;
    }
    
    // Memory transfer: d_a <- h_a (left arrow)
    // Note: We need to check this before assignment to avoid conflicts
    if (check(TokenType::IDENTIFIER)) {
        Token saved = currentToken();
        advance();
        if (check(TokenType::ARROW)) {
            // It's a memory transfer, parse it
            position_--; // Go back to identifier
            auto result = parseMemoryTransfer();
            exitRecursion();
            logDebug("END (memory transfer)", "parseStatement");
            return result;
        }
        position_--; // Go back
    }
    
    // Assignment or expression statement
    // Check for both direct assignment (var = value) and array assignment (arr[i] = value)
    if (check(TokenType::IDENTIFIER)) {
        size_t saved_pos = position_;
        Token saved_token = currentToken();
        advance();
        
        // Check if next is [ (array index) or = (direct assignment)
        if (check(TokenType::LBRACKET)) {
            // It's array access, check if followed by = (array assignment)
            advance(); // consume [
            parseExpression(); // parse index
            if (match(TokenType::RBRACKET) && check(TokenType::ASSIGN)) {
                // It's array assignment: arr[i] = value
                position_ = saved_pos; // Reset to start of identifier
                auto result = parseAssignment();
                exitRecursion();
                logDebug("END (array assignment)", "parseStatement");
                return result;
            }
            // Not array assignment, reset
            position_ = saved_pos;
        } else if (check(TokenType::ASSIGN)) {
            // Direct assignment: var = value
            position_ = saved_pos; // Go back to identifier
            auto result = parseAssignment();
            exitRecursion();
            logDebug("END (assignment)", "parseStatement");
            return result;
        } else {
            // Not an assignment, go back
            position_ = saved_pos;
        }
    }
    
    // If we're at EOF, return nullptr to signal end of parsing
    if (isAtEnd() || currentToken().type == TokenType::EOF_TOKEN) {
        exitRecursion();
        logDebug("END (EOF)", "parseStatement");
        return nullptr;
    }
    
    auto result = parseExpressionStatement();
    exitRecursion();
    logDebug("END (expression)", "parseStatement");
    return result;
}

StmtPtr Parser::parseAssignment() {
    // Check if this is an array element assignment: arr[i] = value
    std::string var_name = consume(TokenType::IDENTIFIER, "Expected variable name").value;
    
    ExprPtr array_index = nullptr;
    // Check for index access: arr[i]
    if (match(TokenType::LBRACKET)) {
        ExprPtr index = parseExpression();
        consume(TokenType::RBRACKET, "Expected ']' after index");
        array_index = index;
    }
    
    consume(TokenType::ASSIGN, "Expected '='");
    ExprPtr value = parseExpression();
    
    return std::make_shared<Assignment>(var_name, value, array_index);
}

StmtPtr Parser::parseIfStatement() {
    consume(TokenType::LPAREN, "Expected '(' after 'if'");
    ExprPtr condition = parseExpression();
    consume(TokenType::RPAREN, "Expected ')' after condition");
    
    auto then_block = parseBlock();
    
    std::vector<StmtPtr> else_block;
    if (match(TokenType::ELSE)) {
        if (check(TokenType::IF)) {
            // elif chain
            else_block.push_back(parseStatement());
        } else {
            else_block = parseBlock();
        }
    }
    
    return std::make_shared<IfStatement>(condition, then_block, else_block);
}

StmtPtr Parser::parseWhileStatement() {
    consume(TokenType::LPAREN, "Expected '(' after 'while'");
    ExprPtr condition = parseExpression();
    consume(TokenType::RPAREN, "Expected ')' after condition");
    
    auto body = parseBlock();
    
    return std::make_shared<WhileStatement>(condition, body);
}

StmtPtr Parser::parseForStatement() {
    consume(TokenType::LPAREN, "Expected '(' after 'for'");
    
    // Init
    StmtPtr init = nullptr;
    if (!check(TokenType::SEMICOLON)) {
        if (check(TokenType::IDENTIFIER) && peekToken().type == TokenType::ASSIGN) {
            init = parseAssignment();
        }
    }
    consume(TokenType::SEMICOLON, "Expected ';' after for init");
    
    // Condition
    ExprPtr condition = nullptr;
    if (!check(TokenType::SEMICOLON)) {
        condition = parseExpression();
    }
    consume(TokenType::SEMICOLON, "Expected ';' after for condition");
    
    // Increment
    StmtPtr increment = nullptr;
    if (!check(TokenType::RPAREN)) {
        if (check(TokenType::IDENTIFIER) && peekToken().type == TokenType::ASSIGN) {
            increment = parseAssignment();
        }
    }
    consume(TokenType::RPAREN, "Expected ')' after for clauses");
    
    auto body = parseBlock();
    
    return std::make_shared<ForStatement>(init, condition, increment, body);
}

StmtPtr Parser::parseFunctionDef() {
    std::string func_name = consume(TokenType::IDENTIFIER, "Expected function name").value;
    
    consume(TokenType::LPAREN, "Expected '(' after function name");
    auto parameters = parseParameterList();
    consume(TokenType::RPAREN, "Expected ')' after parameters");
    
    auto body = parseBlock();
    
    return std::make_shared<FunctionDef>(func_name, parameters, body);
}

StmtPtr Parser::parseReturnStatement() {
    ExprPtr value = nullptr;
    if (!check(TokenType::NEWLINE) && !isAtEnd()) {
        value = parseExpression();
    }
    return std::make_shared<ReturnStatement>(value);
}

StmtPtr Parser::parsePrintStatement() {
    advance(); // consume 'print'
    consume(TokenType::LPAREN, "Expected '(' after 'print'");
    
    std::vector<ExprPtr> expressions;
    if (!check(TokenType::RPAREN)) {
        do {
            expressions.push_back(parseExpression());
        } while (match(TokenType::COMMA));
    }
    
    consume(TokenType::RPAREN, "Expected ')' after print arguments");
    
    return std::make_shared<PrintStatement>(expressions);
}

StmtPtr Parser::parseExpressionStatement() {
    enterRecursion("parseExpressionStatement");
    logDebug("START", "parseExpressionStatement");
    
    ExprPtr expr = parseExpression();
    
    exitRecursion();
    logDebug("END", "parseExpressionStatement");
    return std::make_shared<ExpressionStmt>(expr);
}

std::vector<StmtPtr> Parser::parseBlock() {
    consume(TokenType::LBRACE, "Expected '{' at start of block");
    
    std::vector<StmtPtr> statements;
    while (!check(TokenType::RBRACE) && !isAtEnd()) {
        statements.push_back(parseStatement());
    }
    
    consume(TokenType::RBRACE, "Expected '}' at end of block");
    
    return statements;
}

// Expression Parsing (Precedence Climbing)

ExprPtr Parser::parseExpression() {
    enterRecursion("parseExpression");
    logDebug("START", "parseExpression");
    
    auto result = parseLogicalOr();
    
    exitRecursion();
    logDebug("END", "parseExpression");
    return result;
}

ExprPtr Parser::parseLogicalOr() {
    ExprPtr left = parseLogicalAnd();
    
    while (match(TokenType::OR)) {
        ExprPtr right = parseLogicalAnd();
        left = std::make_shared<BinaryOp>("or", left, right);
    }
    
    return left;
}

ExprPtr Parser::parseLogicalAnd() {
    ExprPtr left = parseEquality();
    
    while (match(TokenType::AND)) {
        ExprPtr right = parseEquality();
        left = std::make_shared<BinaryOp>("and", left, right);
    }
    
    return left;
}

ExprPtr Parser::parseEquality() {
    ExprPtr left = parseComparison();
    
    while (true) {
        if (match(TokenType::EQ)) {
            ExprPtr right = parseComparison();
            left = std::make_shared<BinaryOp>("==", left, right);
        } else if (match(TokenType::NE)) {
            ExprPtr right = parseComparison();
            left = std::make_shared<BinaryOp>("!=", left, right);
        } else {
            break;
        }
    }
    
    return left;
}

ExprPtr Parser::parseComparison() {
    ExprPtr left = parseBitwiseOr();
    
    while (true) {
        if (match(TokenType::LT)) {
            ExprPtr right = parseBitwiseOr();
            left = std::make_shared<BinaryOp>("<", left, right);
        } else if (match(TokenType::GT)) {
            ExprPtr right = parseBitwiseOr();
            left = std::make_shared<BinaryOp>(">", left, right);
        } else if (match(TokenType::LE)) {
            ExprPtr right = parseBitwiseOr();
            left = std::make_shared<BinaryOp>("<=", left, right);
        } else if (match(TokenType::GE)) {
            ExprPtr right = parseBitwiseOr();
            left = std::make_shared<BinaryOp>(">=", left, right);
        } else {
            break;
        }
    }
    
    return left;
}

ExprPtr Parser::parseBitwiseOr() {
    ExprPtr left = parseBitwiseXor();
    
    while (match(TokenType::BIT_OR)) {
        ExprPtr right = parseBitwiseXor();
        left = std::make_shared<BinaryOp>("|", left, right);
    }
    
    return left;
}

ExprPtr Parser::parseBitwiseXor() {
    ExprPtr left = parseBitwiseAnd();
    
    while (match(TokenType::BIT_XOR)) {
        ExprPtr right = parseBitwiseAnd();
        left = std::make_shared<BinaryOp>("^", left, right);
    }
    
    return left;
}

ExprPtr Parser::parseBitwiseAnd() {
    ExprPtr left = parseShift();
    
    while (match(TokenType::BIT_AND)) {
        ExprPtr right = parseShift();
        left = std::make_shared<BinaryOp>("&", left, right);
    }
    
    return left;
}

ExprPtr Parser::parseShift() {
    ExprPtr left = parseTerm();
    
    while (true) {
        if (match(TokenType::LSHIFT)) {
            ExprPtr right = parseTerm();
            left = std::make_shared<BinaryOp>("<<", left, right);
        } else if (match(TokenType::RSHIFT)) {
            ExprPtr right = parseTerm();
            left = std::make_shared<BinaryOp>(">>", left, right);
        } else {
            break;
        }
    }
    
    return left;
}

ExprPtr Parser::parseTerm() {
    ExprPtr left = parseFactor();
    
    while (true) {
        if (match(TokenType::PLUS)) {
            ExprPtr right = parseFactor();
            left = std::make_shared<BinaryOp>("+", left, right);
        } else if (match(TokenType::MINUS)) {
            ExprPtr right = parseFactor();
            left = std::make_shared<BinaryOp>("-", left, right);
        } else {
            break;
        }
    }
    
    return left;
}

ExprPtr Parser::parseFactor() {
    ExprPtr left = parsePower();
    
    while (true) {
        if (match(TokenType::MULTIPLY)) {
            ExprPtr right = parsePower();
            left = std::make_shared<BinaryOp>("*", left, right);
        } else if (match(TokenType::DIVIDE)) {
            ExprPtr right = parsePower();
            left = std::make_shared<BinaryOp>("/", left, right);
        } else if (match(TokenType::MODULO)) {
            ExprPtr right = parsePower();
            left = std::make_shared<BinaryOp>("%", left, right);
        } else {
            break;
        }
    }
    
    return left;
}

ExprPtr Parser::parsePower() {
    ExprPtr left = parseUnary();
    
    if (match(TokenType::POWER)) {
        ExprPtr right = parsePower(); // Right associative
        left = std::make_shared<BinaryOp>("**", left, right);
    }
    
    return left;
}

ExprPtr Parser::parseUnary() {
    if (match(TokenType::MINUS)) {
        ExprPtr operand = parseUnary();
        return std::make_shared<UnaryOp>("-", operand);
    }
    if (match(TokenType::PLUS)) {
        ExprPtr operand = parseUnary();
        return std::make_shared<UnaryOp>("+", operand);
    }
    if (match(TokenType::BIT_NOT)) {
        ExprPtr operand = parseUnary();
        return std::make_shared<UnaryOp>("~", operand);
    }
    if (match(TokenType::NOT)) {
        ExprPtr operand = parseUnary();
        return std::make_shared<UnaryOp>("not", operand);
    }
    
    return parsePostfix();
}

ExprPtr Parser::parsePostfix() {
    enterRecursion("parsePostfix");
    logDebug("START", "parsePostfix");
    
    ExprPtr expr = parsePrimary();
    
    loop_iterations_ = 0;
    while (true) {
        loop_iterations_++;
        checkLoopLimit("parsePostfix");
        logDebug("LOOP iteration " + std::to_string(loop_iterations_), "parsePostfix");
        if (match(TokenType::LPAREN)) {
            // Check if this is atomicAdd or other atomic operation
            if (auto ident = std::dynamic_pointer_cast<Identifier>(expr)) {
                if (ident->name == "atomicAdd" || ident->name == "atomicSub") {
                    // Parse atomic operation
                    std::string op_name = ident->name;
                    std::string op = op_name.substr(6); // Remove "atomic" prefix, get "Add" or "Sub"
                    // Convert to lowercase
                    for (char& c : op) {
                        c = std::tolower(c);
                    }
                    
                    ExprPtr address = parseExpression();
                    consume(TokenType::COMMA, "Expected ',' after address in atomic operation");
                    ExprPtr value = parseExpression();
                    consume(TokenType::RPAREN, "Expected ')' after atomic operation arguments");
                    
                    auto result = std::make_shared<AtomicOp>(op, address, value);
                    exitRecursion();
                    logDebug("END (atomic)", "parsePostfix");
                    return result;
                }
            }
            expr = parseFunctionCall(expr);
        } else if (match(TokenType::LBRACKET)) {
            expr = parseIndexAccess(expr);
        } else if (match(TokenType::DOT)) {
            expr = parseMemberAccess(expr);
        } else {
            break;
        }
    }
    
    loop_iterations_ = 0; // Reset after loop
    exitRecursion();
    logDebug("END", "parsePostfix");
    return expr;
}

ExprPtr Parser::parsePrimary() {
    enterRecursion("parsePrimary");
    logDebug("START", "parsePrimary");
    
    // Literals
    if (match(TokenType::INTEGER)) {
        int value = std::stoi(tokens_[position_ - 1].value);
        exitRecursion();
        logDebug("END (integer)", "parsePrimary");
        return std::make_shared<IntegerLiteral>(value);
    }
    
    if (match(TokenType::FLOAT)) {
        double value = std::stod(tokens_[position_ - 1].value);
        exitRecursion();
        logDebug("END (float)", "parsePrimary");
        return std::make_shared<FloatLiteral>(value);
    }
    
    if (match(TokenType::STRING)) {
        auto result = std::make_shared<StringLiteral>(tokens_[position_ - 1].value);
        exitRecursion();
        logDebug("END (string)", "parsePrimary");
        return result;
    }
    
    if (match(TokenType::TRUE)) {
        auto result = std::make_shared<BooleanLiteral>(true);
        exitRecursion();
        logDebug("END (true)", "parsePrimary");
        return result;
    }
    
    if (match(TokenType::FALSE)) {
        auto result = std::make_shared<BooleanLiteral>(false);
        exitRecursion();
        logDebug("END (false)", "parsePrimary");
        return result;
    }
    
    if (match(TokenType::NONE)) {
        auto result = std::make_shared<NoneLiteral>();
        exitRecursion();
        logDebug("END (none)", "parsePrimary");
        return result;
    }
    
    // CUDA: device[size] and shared[size]
    if (match(TokenType::DEVICE)) {
        auto result = parseDeviceAlloc();
        exitRecursion();
        logDebug("END (device)", "parsePrimary");
        return result;
    }
    
    if (match(TokenType::SHARED)) {
        auto result = parseSharedAlloc();
        exitRecursion();
        logDebug("END (shared)", "parsePrimary");
        return result;
    }
    
    // Identifier (check for built-in CUDA variables)
    if (match(TokenType::IDENTIFIER)) {
        std::string name = tokens_[position_ - 1].value;
        // Check if it's a CUDA built-in variable
        if (name == "threadIdx_x" || name == "threadIdx_y" || name == "threadIdx_z" ||
            name == "blockIdx_x" || name == "blockIdx_y" || name == "blockIdx_z" ||
            name == "blockDim_x" || name == "blockDim_y" || name == "blockDim_z" ||
            name == "gridDim_x" || name == "gridDim_y" || name == "gridDim_z") {
            auto result = std::make_shared<BuiltInVariable>(name);
            exitRecursion();
            logDebug("END (builtin)", "parsePrimary");
            return result;
        }
        auto result = std::make_shared<Identifier>(name);
        exitRecursion();
        logDebug("END (identifier)", "parsePrimary");
        return result;
    }
    
    // Parenthesized expression
    if (match(TokenType::LPAREN)) {
        logDebug("Found parenthesized expression", "parsePrimary");
        ExprPtr expr = parseExpression();
        consume(TokenType::RPAREN, "Expected ')' after expression");
        exitRecursion();
        logDebug("END (parenthesized)", "parsePrimary");
        return expr;
    }
    
    // List literal
    if (match(TokenType::LBRACKET)) {
        auto result = parseListLiteral();
        exitRecursion();
        logDebug("END (list)", "parsePrimary");
        return result;
    }
    
    // Lambda
    if (match(TokenType::LAMBDA)) {
        auto result = parseLambda();
        exitRecursion();
        logDebug("END (lambda)", "parsePrimary");
        return result;
    }
    
    exitRecursion();
    logDebug("END (error)", "parsePrimary");
    throw std::runtime_error("Unexpected token: " + currentToken().toString());
}

// Helper methods

ExprPtr Parser::parseFunctionCall(ExprPtr function) {
    auto arguments = parseArgumentList();
    consume(TokenType::RPAREN, "Expected ')' after arguments");
    return std::make_shared<FunctionCall>(function, arguments);
}

ExprPtr Parser::parseIndexAccess(ExprPtr array) {
    ExprPtr index = parseExpression();
    consume(TokenType::RBRACKET, "Expected ']' after index");
    return std::make_shared<IndexAccess>(array, index);
}

ExprPtr Parser::parseMemberAccess(ExprPtr object) {
    std::string member = consume(TokenType::IDENTIFIER, "Expected member name").value;
    return std::make_shared<MemberAccess>(object, member);
}

std::vector<ExprPtr> Parser::parseArgumentList() {
    std::vector<ExprPtr> arguments;
    
    if (!check(TokenType::RPAREN)) {
        do {
            arguments.push_back(parseExpression());
        } while (match(TokenType::COMMA));
    }
    
    return arguments;
}

std::vector<std::string> Parser::parseParameterList() {
    std::vector<std::string> parameters;
    
    if (!check(TokenType::RPAREN)) {
        do {
            parameters.push_back(consume(TokenType::IDENTIFIER, "Expected parameter name").value);
        } while (match(TokenType::COMMA));
    }
    
    return parameters;
}

ExprPtr Parser::parseListLiteral() {
    std::vector<ExprPtr> elements;
    
    if (!check(TokenType::RBRACKET)) {
        do {
            elements.push_back(parseExpression());
        } while (match(TokenType::COMMA));
    }
    
    consume(TokenType::RBRACKET, "Expected ']' after list elements");
    return std::make_shared<ListLiteral>(elements);
}

ExprPtr Parser::parseLambda() {
    consume(TokenType::LPAREN, "Expected '(' after 'lambda'");
    auto parameters = parseParameterList();
    consume(TokenType::RPAREN, "Expected ')' after lambda parameters");
    
    ExprPtr body = parseExpression();
    
    return std::make_shared<LambdaExpr>(parameters, body);
}

// CUDA Parsing Methods

StmtPtr Parser::parseCudaKernelDef() {
    std::string name = consume(TokenType::IDENTIFIER, "Expected kernel name").value;
    
    consume(TokenType::LPAREN, "Expected '(' after kernel name");
    auto parameters = parseParameterList();
    consume(TokenType::RPAREN, "Expected ')' after parameters");
    
    // Parse decorators if present (before body)
    std::vector<std::string> decorators;
    bool is_persistent = false;
    
    auto body = parseBlock();
    
    return std::make_shared<CudaKernelDef>(name, parameters, body, is_persistent, decorators);
}

StmtPtr Parser::parseGpuLaunch() {
    // gpu[blocks, threads] kernel(args)
    // or gpu[0][blocks, threads] kernel(args) for multi-GPU
    
    int gpu_id = -1;
    
    // Check for gpu[0], gpu[1], etc (multi-GPU syntax)
    consume(TokenType::LBRACKET, "Expected '[' after 'gpu'");
    if (check(TokenType::INTEGER)) {
        // Multi-GPU: gpu[0][blocks, threads]
        gpu_id = std::stoi(currentToken().value);
        advance();
        consume(TokenType::RBRACKET, "Expected ']' after GPU ID");
        consume(TokenType::LBRACKET, "Expected '[' for launch configuration");
    }
    
    // Parse launch configuration: [blocks, threads]
    ExprPtr blocks = parseExpression();
    consume(TokenType::COMMA, "Expected ',' between blocks and threads");
    ExprPtr threads = parseExpression();
    consume(TokenType::RBRACKET, "Expected ']' after launch configuration");
    
    // Parse kernel call
    ExprPtr kernel = parseExpression();
    if (auto call = std::dynamic_pointer_cast<FunctionCall>(kernel)) {
        return std::make_shared<GpuLaunch>(blocks, threads, kernel, gpu_id);
    }
    throw std::runtime_error("Expected function call after gpu launch");
}

StmtPtr Parser::parseMemoryTransfer() {
    // d_a <- h_a (left arrow: H->D)
    // h_c <- d_c (left arrow: D->H, but we need to infer direction)
    
    // Parse destination (must be identifier or index access)
    ExprPtr destination;
    if (match(TokenType::IDENTIFIER)) {
        destination = std::make_shared<Identifier>(tokens_[position_ - 1].value);
        // Check for index access: d_a[0]
        if (match(TokenType::LBRACKET)) {
            ExprPtr index = parseExpression();
            consume(TokenType::RBRACKET, "Expected ']' after index");
            destination = std::make_shared<IndexAccess>(destination, index);
        }
    } else {
        throw std::runtime_error("Expected identifier for memory transfer destination");
    }
    
    if (!match(TokenType::ARROW)) {
        throw std::runtime_error("Expected '<-' for memory transfer");
    }
    
    // Parse source
    ExprPtr source = parseExpression();
    
    // Infer direction: if destination starts with 'd_', it's H->D
    // Otherwise, assume D->H
    bool is_h2d = true;
    if (auto ident = std::dynamic_pointer_cast<Identifier>(destination)) {
        is_h2d = (ident->name.length() >= 2 && ident->name[0] == 'd' && ident->name[1] == '_');
    } else if (auto idx = std::dynamic_pointer_cast<IndexAccess>(destination)) {
        if (auto ident = std::dynamic_pointer_cast<Identifier>(idx->array)) {
            is_h2d = (ident->name.length() >= 2 && ident->name[0] == 'd' && ident->name[1] == '_');
        }
    }
    
    return std::make_shared<MemoryTransfer>(destination, source, is_h2d);
}

StmtPtr Parser::parseFreeStatement() {
    consume(TokenType::LPAREN, "Expected '(' after 'free'");
    ExprPtr variable = parseExpression();
    consume(TokenType::RPAREN, "Expected ')' after free variable");
    return std::make_shared<FreeStatement>(variable);
}

ExprPtr Parser::parseDeviceAlloc() {
    // device[size]
    consume(TokenType::LBRACKET, "Expected '[' after 'device'");
    ExprPtr size = parseExpression();
    consume(TokenType::RBRACKET, "Expected ']' after device size");
    return std::make_shared<DeviceAlloc>(size);
}

ExprPtr Parser::parseSharedAlloc() {
    // shared[size]
    consume(TokenType::LBRACKET, "Expected '[' after 'shared'");
    ExprPtr size = parseExpression();
    consume(TokenType::RBRACKET, "Expected ']' after shared size");
    return std::make_shared<SharedAlloc>(size);
}

ExprPtr Parser::parseBuiltInVariable() {
    // Built-in variables are handled in parsePrimary
    // This method is kept for consistency but shouldn't be called directly
    if (match(TokenType::IDENTIFIER)) {
        return std::make_shared<BuiltInVariable>(tokens_[position_ - 1].value);
    }
    throw std::runtime_error("Expected built-in variable name");
}

std::vector<std::string> Parser::parseDecorators() {
    // @persistent, @optimize(level), etc
    std::vector<std::string> decorators;
    // Decorators parsing can be added later if needed
    return decorators;
}

// Error handling

void Parser::reportError(const std::string& message) {
    std::cerr << "Parser error: " << message << std::endl;
}

void Parser::synchronize() {
    advance();
    
    while (!isAtEnd()) {
        // Sync at statement boundaries
        if (check(TokenType::DEF) || 
            check(TokenType::IF) ||
            check(TokenType::WHILE) ||
            check(TokenType::FOR) ||
            check(TokenType::RETURN) ||
            check(TokenType::CUDA) ||
            check(TokenType::GPU)) {
            return;
        }
        
        advance();
    }
}

// Debug and safety methods

void Parser::logDebug(const std::string& message, const std::string& function_name) const {
    if (debug_) {
        std::cout << "[DEBUG PARSER] [" << function_name << "] pos=" << position_ 
                  << " depth=" << recursion_depth_ << " " << message;
        try {
            if (position_ < tokens_.size() && !tokens_.empty()) {
                std::cout << " token=" << tokens_[position_].toString();
            } else {
                std::cout << " token=EOF";
            }
        } catch (...) {
            std::cout << " token=<error>";
        }
        std::cout << std::endl;
        std::cout.flush(); // Force flush to ensure output appears before crash
    }
}

void Parser::checkRecursionLimit(const std::string& function_name) {
    if (recursion_depth_ > max_recursion_depth_) {
        std::string error = "Maximum recursion depth (" + 
                           std::to_string(max_recursion_depth_) + 
                           ") exceeded in " + function_name;
        logDebug("RECURSION LIMIT EXCEEDED", function_name);
        throw std::runtime_error(error);
    }
}

void Parser::checkLoopLimit(const std::string& function_name) {
    if (loop_iterations_ > max_loop_iterations_) {
        std::string error = "Maximum loop iterations (" + 
                           std::to_string(max_loop_iterations_) + 
                           ") exceeded in " + function_name;
        logDebug("LOOP LIMIT EXCEEDED", function_name);
        throw std::runtime_error(error);
    }
}

void Parser::enterRecursion(const std::string& function_name) {
    recursion_depth_++;
    checkRecursionLimit(function_name);
    logDebug("ENTER", function_name);
}

void Parser::exitRecursion() {
    recursion_depth_--;
    if (recursion_depth_ < 0) {
        recursion_depth_ = 0; // Safety check
    }
}

} // namespace moonlight







