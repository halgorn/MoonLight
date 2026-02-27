"""Sistema de tratamento de erros do MoonLight"""

class MoonLightError(Exception):
    """Classe base para erros do MoonLight"""
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(self.format_message())
    
    def format_message(self):
        """Formata a mensagem de erro"""
        if self.line:
            return f"Linha {self.line}: {self.message}"
        return self.message

class LexicalError(MoonLightError):
    """Erro léxico"""
    pass

class SyntaxError(MoonLightError):
    """Erro sintático"""
    pass

class RuntimeError(MoonLightError):
    """Erro de execução"""
    pass

class TypeError(MoonLightError):
    """Erro de tipo"""
    pass

class NameError(MoonLightError):
    """Erro de nome não definido"""
    pass

class IndexError(MoonLightError):
    """Erro de índice fora dos limites"""
    pass

class ZeroDivisionError(MoonLightError):
    """Erro de divisão por zero"""
    pass

class ErrorHandler:
    """Gerenciador de erros"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, error):
        """Adiciona um erro"""
        self.errors.append(error)
    
    def add_warning(self, message, line=None):
        """Adiciona um warning"""
        warning = f"Warning (linha {line}): {message}" if line else f"Warning: {message}"
        self.warnings.append(warning)
    
    def has_errors(self):
        """Verifica se há erros"""
        return len(self.errors) > 0
    
    def get_errors(self):
        """Retorna lista de erros"""
        return self.errors
    
    def get_warnings(self):
        """Retorna lista de warnings"""
        return self.warnings
    
    def print_errors(self):
        """Imprime todos os erros"""
        if self.errors:
            print("\n=== ERROS ===")
            for error in self.errors:
                print(f"❌ {error}")
        
        if self.warnings:
            print("\n=== WARNINGS ===")
            for warning in self.warnings:
                print(f"⚠️  {warning}")
    
    def clear(self):
        """Limpa erros e warnings"""
        self.errors.clear()
        self.warnings.clear()

# Instância global
error_handler = ErrorHandler()










