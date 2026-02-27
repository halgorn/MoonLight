#include "moonlight/token.h"

namespace moonlight {

const std::map<std::string, TokenType> KEYWORDS = {
    // Control flow
    {"if", TokenType::IF},
    {"else", TokenType::ELSE},
    {"elif", TokenType::ELIF},
    {"while", TokenType::WHILE},
    {"for", TokenType::FOR},
    {"break", TokenType::BREAK},
    {"continue", TokenType::CONTINUE},
    
    // Functions and classes
    {"def", TokenType::DEF},
    {"return", TokenType::RETURN},
    {"yield", TokenType::YIELD},
    {"class", TokenType::CLASS},
    {"self", TokenType::SELF},
    {"lambda", TokenType::LAMBDA},
    
    // Modules
    {"import", TokenType::IMPORT},
    {"from", TokenType::FROM},
    {"as", TokenType::AS},
    
    // Context managers
    {"with", TokenType::WITH},
    
    // Exceptions
    {"try", TokenType::TRY},
    {"except", TokenType::EXCEPT},
    {"finally", TokenType::FINALLY},
    {"raise", TokenType::RAISE},
    
    // Async
    {"async", TokenType::ASYNC},
    {"await", TokenType::AWAIT},
    
    // CUDA
    {"cuda", TokenType::CUDA},
    {"kernel", TokenType::KERNEL},
    {"device", TokenType::DEVICE},
    {"gpu", TokenType::GPU},
    {"host", TokenType::HOST},
    {"shared", TokenType::SHARED},
    {"global", TokenType::GLOBAL},
    {"free", TokenType::FREE},
    
    // Logical
    {"and", TokenType::AND},
    {"or", TokenType::OR},
    {"not", TokenType::NOT},
    
    // Literals
    {"True", TokenType::TRUE},
    {"False", TokenType::FALSE},
    {"None", TokenType::NONE},
};

std::string tokenTypeToString(TokenType type) {
    switch(type) {
        case TokenType::INTEGER: return "INTEGER";
        case TokenType::FLOAT: return "FLOAT";
        case TokenType::STRING: return "STRING";
        case TokenType::TRUE: return "TRUE";
        case TokenType::FALSE: return "FALSE";
        case TokenType::NONE: return "NONE";
        case TokenType::IDENTIFIER: return "IDENTIFIER";
        case TokenType::IF: return "IF";
        case TokenType::ELSE: return "ELSE";
        case TokenType::WHILE: return "WHILE";
        case TokenType::FOR: return "FOR";
        case TokenType::DEF: return "DEF";
        case TokenType::RETURN: return "RETURN";
        case TokenType::PLUS: return "PLUS";
        case TokenType::MINUS: return "MINUS";
        case TokenType::MULTIPLY: return "MULTIPLY";
        case TokenType::DIVIDE: return "DIVIDE";
        case TokenType::ASSIGN: return "ASSIGN";
        case TokenType::LPAREN: return "LPAREN";
        case TokenType::RPAREN: return "RPAREN";
        case TokenType::LBRACE: return "LBRACE";
        case TokenType::RBRACE: return "RBRACE";
        case TokenType::EOF_TOKEN: return "EOF";
        default: return "UNKNOWN";
    }
}

std::string Token::toString() const {
    return tokenTypeToString(type) + "(" + value + ") at " + 
           std::to_string(line) + ":" + std::to_string(column);
}

} // namespace moonlight







