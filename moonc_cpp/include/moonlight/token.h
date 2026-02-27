#pragma once

#include <string>
#include <map>

namespace moonlight {

enum class TokenType {
    // Literals
    INTEGER,
    FLOAT,
    STRING,
    TRUE,
    FALSE,
    NONE,
    
    // Identifiers
    IDENTIFIER,
    
    // Keywords
    IF, ELSE, ELIF,
    WHILE, FOR,
    BREAK, CONTINUE,
    DEF, RETURN, YIELD,
    CLASS, SELF,
    IMPORT, FROM, AS,
    LAMBDA,
    WITH,
    TRY, EXCEPT, FINALLY, RAISE,
    ASYNC, AWAIT,
    
    // CUDA Keywords
    CUDA, KERNEL, DEVICE, GPU, HOST,
    SHARED, GLOBAL, FREE,
    
    // Operators
    PLUS, MINUS, MULTIPLY, DIVIDE, MODULO, POWER,
    ASSIGN, PLUS_ASSIGN, MINUS_ASSIGN, MULT_ASSIGN,
    INCREMENT, DECREMENT,
    
    // Comparison
    EQ, NE, LT, GT, LE, GE,
    
    // Logical
    AND, OR, NOT,
    
    // Bitwise
    BIT_AND, BIT_OR, BIT_XOR, BIT_NOT,
    LSHIFT, RSHIFT,
    
    // Delimiters
    LPAREN, RPAREN,
    LBRACKET, RBRACKET,
    LBRACE, RBRACE,
    COMMA, COLON, SEMICOLON, DOT,
    ARROW,
    
    // Special
    NEWLINE,
    INDENT, DEDENT,
    EOF_TOKEN,
    
    // Unknown
    UNKNOWN
};

struct Token {
    TokenType type;
    std::string value;
    int line;
    int column;
    
    Token(TokenType t = TokenType::UNKNOWN, const std::string& v = "", int l = 0, int c = 0)
        : type(t), value(v), line(l), column(c) {}
    
    std::string toString() const;
};

// Keywords map
extern const std::map<std::string, TokenType> KEYWORDS;

// Token type to string
std::string tokenTypeToString(TokenType type);

} // namespace moonlight







