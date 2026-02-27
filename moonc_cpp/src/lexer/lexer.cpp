#include "moonlight/lexer.h"
#include <cctype>
#include <iostream>
#include <sstream>

namespace moonlight {

Lexer::Lexer(const std::string& source)
    : source_(source), position_(0), line_(1), column_(1) {}

std::vector<Token> Lexer::tokenize() {
    std::vector<Token> tokens;
    
    while (!isAtEnd()) {
        Token token = nextToken();
        if (token.type != TokenType::UNKNOWN) {
            tokens.push_back(token);
        }
        if (token.type == TokenType::EOF_TOKEN) {
            break;
        }
    }
    
    return tokens;
}

Token Lexer::nextToken() {
    // Skip whitespace and comments in a loop until we find a token
    while (true) {
        skipWhitespace();
        if (isAtEnd()) {
            return Token(TokenType::EOF_TOKEN, "", line_, column_);
        }
        if (currentChar() == '#') {
            skipComment();
            continue; // Skip to next iteration to check for more whitespace/comments
        }
        break; // Found a non-comment, non-whitespace character
    }
    
    if (isAtEnd()) {
        return Token(TokenType::EOF_TOKEN, "", line_, column_);
    }
    
    char current = currentChar();
    
    // Numbers
    if (isDigit(current)) {
        return parseNumber();
    }
    
    // Strings
    if (current == '"' || current == '\'') {
        return parseString(current);
    }
    
    // Identifiers and keywords
    if (isAlpha(current) || current == '_') {
        return parseIdentifier();
    }
    
    // Operators and delimiters
    return parseOperator();
}

Token Lexer::peekToken() {
    size_t saved_pos = position_;
    size_t saved_line = line_;
    size_t saved_col = column_;
    
    Token token = nextToken();
    
    position_ = saved_pos;
    line_ = saved_line;
    column_ = saved_col;
    
    return token;
}

bool Lexer::isAtEnd() const {
    return position_ >= source_.length();
}

char Lexer::currentChar() const {
    if (isAtEnd()) return '\0';
    return source_[position_];
}

char Lexer::peekChar(int offset) const {
    size_t pos = position_ + offset;
    if (pos >= source_.length()) return '\0';
    return source_[pos];
}

void Lexer::advance() {
    if (!isAtEnd()) {
        if (source_[position_] == '\n') {
            line_++;
            column_ = 1;
        } else {
            column_++;
        }
        position_++;
    }
}

void Lexer::skipWhitespace() {
    while (!isAtEnd() && isWhitespace(currentChar())) {
        advance();
    }
}

void Lexer::skipComment() {
    if (currentChar() == '#') {
        while (!isAtEnd() && currentChar() != '\n') {
            advance();
        }
        if (!isAtEnd()) advance(); // Skip newline
    }
}

Token Lexer::parseNumber() {
    int start_line = line_;
    int start_col = column_;
    std::string num_str;
    bool is_float = false;
    
    while (!isAtEnd() && (isDigit(currentChar()) || currentChar() == '.')) {
        if (currentChar() == '.') {
            if (is_float) break; // Second dot, not part of number
            is_float = true;
        }
        num_str += currentChar();
        advance();
    }
    
    TokenType type = is_float ? TokenType::FLOAT : TokenType::INTEGER;
    return Token(type, num_str, start_line, start_col);
}

Token Lexer::parseString(char quote) {
    int start_line = line_;
    int start_col = column_;
    std::string str;
    
    advance(); // Skip opening quote
    
    while (!isAtEnd() && currentChar() != quote) {
        if (currentChar() == '\\') {
            advance();
            if (!isAtEnd()) {
                // Handle escape sequences
                char escaped = currentChar();
                switch (escaped) {
                    case 'n': str += '\n'; break;
                    case 't': str += '\t'; break;
                    case 'r': str += '\r'; break;
                    case '\\': str += '\\'; break;
                    case '"': str += '"'; break;
                    case '\'': str += '\''; break;
                    default: str += escaped; break;
                }
                advance();
            }
        } else {
            str += currentChar();
            advance();
        }
    }
    
    if (!isAtEnd()) {
        advance(); // Skip closing quote
    }
    
    return Token(TokenType::STRING, str, start_line, start_col);
}

Token Lexer::parseIdentifier() {
    int start_line = line_;
    int start_col = column_;
    std::string identifier;
    
    while (!isAtEnd() && (isAlnum(currentChar()) || currentChar() == '_')) {
        identifier += currentChar();
        advance();
    }
    
    // Check if it's a keyword
    auto it = KEYWORDS.find(identifier);
    if (it != KEYWORDS.end()) {
        return Token(it->second, identifier, start_line, start_col);
    }
    
    return Token(TokenType::IDENTIFIER, identifier, start_line, start_col);
}

Token Lexer::parseOperator() {
    int start_line = line_;
    int start_col = column_;
    char current = currentChar();
    char next = peekChar();
    
    // Two-character operators
    if (current == '=' && next == '=') {
        advance(); advance();
        return Token(TokenType::EQ, "==", start_line, start_col);
    }
    if (current == '!' && next == '=') {
        advance(); advance();
        return Token(TokenType::NE, "!=", start_line, start_col);
    }
    // Check <- before <= and << (order matters!)
    if (current == '<' && next == '-') {
        advance(); advance();
        return Token(TokenType::ARROW, "<-", start_line, start_col);
    }
    if (current == '<' && next == '=') {
        advance(); advance();
        return Token(TokenType::LE, "<=", start_line, start_col);
    }
    if (current == '>' && next == '=') {
        advance(); advance();
        return Token(TokenType::GE, ">=", start_line, start_col);
    }
    if (current == '<' && next == '<') {
        advance(); advance();
        return Token(TokenType::LSHIFT, "<<", start_line, start_col);
    }
    if (current == '>' && next == '>') {
        advance(); advance();
        return Token(TokenType::RSHIFT, ">>", start_line, start_col);
    }
    if (current == '+' && next == '+') {
        advance(); advance();
        return Token(TokenType::INCREMENT, "++", start_line, start_col);
    }
    if (current == '-' && next == '-') {
        advance(); advance();
        return Token(TokenType::DECREMENT, "--", start_line, start_col);
    }
    if (current == '+' && next == '=') {
        advance(); advance();
        return Token(TokenType::PLUS_ASSIGN, "+=", start_line, start_col);
    }
    if (current == '-' && next == '=') {
        advance(); advance();
        return Token(TokenType::MINUS_ASSIGN, "-=", start_line, start_col);
    }
    if (current == '*' && next == '=') {
        advance(); advance();
        return Token(TokenType::MULT_ASSIGN, "*=", start_line, start_col);
    }
    if (current == '*' && next == '*') {
        advance(); advance();
        return Token(TokenType::POWER, "**", start_line, start_col);
    }
    if (current == '-' && next == '>') {
        advance(); advance();
        return Token(TokenType::ARROW, "->", start_line, start_col);
    }
    
    // Single-character operators
    advance();
    switch (current) {
        case '+': return Token(TokenType::PLUS, "+", start_line, start_col);
        case '-': return Token(TokenType::MINUS, "-", start_line, start_col);
        case '*': return Token(TokenType::MULTIPLY, "*", start_line, start_col);
        case '/': return Token(TokenType::DIVIDE, "/", start_line, start_col);
        case '%': return Token(TokenType::MODULO, "%", start_line, start_col);
        case '=': return Token(TokenType::ASSIGN, "=", start_line, start_col);
        case '<': return Token(TokenType::LT, "<", start_line, start_col);
        case '>': return Token(TokenType::GT, ">", start_line, start_col);
        case '&': return Token(TokenType::BIT_AND, "&", start_line, start_col);
        case '|': return Token(TokenType::BIT_OR, "|", start_line, start_col);
        case '^': return Token(TokenType::BIT_XOR, "^", start_line, start_col);
        case '~': return Token(TokenType::BIT_NOT, "~", start_line, start_col);
        case '(': return Token(TokenType::LPAREN, "(", start_line, start_col);
        case ')': return Token(TokenType::RPAREN, ")", start_line, start_col);
        case '[': return Token(TokenType::LBRACKET, "[", start_line, start_col);
        case ']': return Token(TokenType::RBRACKET, "]", start_line, start_col);
        case '{': return Token(TokenType::LBRACE, "{", start_line, start_col);
        case '}': return Token(TokenType::RBRACE, "}", start_line, start_col);
        case ',': return Token(TokenType::COMMA, ",", start_line, start_col);
        case ':': return Token(TokenType::COLON, ":", start_line, start_col);
        case ';': return Token(TokenType::SEMICOLON, ";", start_line, start_col);
        case '.': return Token(TokenType::DOT, ".", start_line, start_col);
        default:
            reportError(std::string("Unknown character: ") + current);
            return Token(TokenType::UNKNOWN, std::string(1, current), start_line, start_col);
    }
}

bool Lexer::isDigit(char c) const {
    return std::isdigit(static_cast<unsigned char>(c));
}

bool Lexer::isAlpha(char c) const {
    return std::isalpha(static_cast<unsigned char>(c));
}

bool Lexer::isAlnum(char c) const {
    return std::isalnum(static_cast<unsigned char>(c));
}

bool Lexer::isWhitespace(char c) const {
    return c == ' ' || c == '\t' || c == '\n' || c == '\r';
}

void Lexer::reportError(const std::string& message) {
    std::cerr << "Lexer error at line " << line_ << ", column " << column_ 
              << ": " << message << std::endl;
}

} // namespace moonlight







