#pragma once

#include "moonlight/token.h"
#include <vector>
#include <string>
#include <memory>

namespace moonlight {

class Lexer {
public:
    explicit Lexer(const std::string& source);
    
    // Tokenize the entire source
    std::vector<Token> tokenize();
    
    // Get next token
    Token nextToken();
    
    // Peek at next token without consuming
    Token peekToken();
    
    // Check if we're at end of source
    bool isAtEnd() const;
    
private:
    std::string source_;
    size_t position_;
    size_t line_;
    size_t column_;
    
    // Helper methods
    char currentChar() const;
    char peekChar(int offset = 1) const;
    void advance();
    void skipWhitespace();
    void skipComment();
    
    // Token parsing
    Token parseNumber();
    Token parseString(char quote);
    Token parseIdentifier();
    Token parseOperator();
    
    // Character checks
    bool isDigit(char c) const;
    bool isAlpha(char c) const;
    bool isAlnum(char c) const;
    bool isWhitespace(char c) const;
    
    // Error handling
    void reportError(const std::string& message);
};

} // namespace moonlight







