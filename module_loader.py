"""Sistema de Módulos e Imports do MoonLight"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from parser import parser
from executor_simple import interpretar, variaveis

class Module:
    """Representa um módulo MoonLight"""
    def __init__(self, name: str, path: str, namespace: Dict):
        self.name = name
        self.path = path
        self.namespace = namespace
        self.exports = {}
    
    def get_export(self, name: str):
        """Obtém um export do módulo"""
        return self.namespace.get(name)
    
    def get_all_exports(self):
        """Retorna todos os exports do módulo"""
        return self.namespace.copy()

class ModuleLoader:
    """Carregador de módulos MoonLight"""
    
    def __init__(self):
        self.loaded_modules: Dict[str, Module] = {}
        self.module_paths: List[str] = []
        self.loading_stack: List[str] = []  # Para detectar imports circulares
        
        # Adiciona paths padrão
        self._setup_module_paths()
    
    def _setup_module_paths(self):
        """Configura os caminhos de busca de módulos"""
        # Diretório atual
        self.module_paths.append(os.getcwd())
        
        # Diretório stdlib
        script_dir = os.path.dirname(os.path.abspath(__file__))
        stdlib_path = os.path.join(script_dir, 'stdlib')
        if os.path.exists(stdlib_path):
            self.module_paths.append(stdlib_path)
        
        # Diretório do usuário
        user_modules = os.path.expanduser('~/.moonlight/modules')
        if os.path.exists(user_modules):
            self.module_paths.append(user_modules)
    
    def find_module(self, module_name: str) -> Optional[str]:
        """Encontra o caminho de um módulo"""
        # Converte nome do módulo para path (ex: math -> math.gpu)
        module_file = f"{module_name}.gpu"
        
        for search_path in self.module_paths:
            module_path = os.path.join(search_path, module_file)
            if os.path.exists(module_path):
                return module_path
        
        return None
    
    def load_module(self, module_name: str, current_path: Optional[str] = None) -> Optional[Module]:
        """Carrega um módulo MoonLight"""
        # Se já está carregado, retorna do cache
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
        
        # Detecta imports circulares
        if module_name in self.loading_stack:
            cycle = ' -> '.join(self.loading_stack + [module_name])
            raise ImportError(f"Import circular detectado: {cycle}")
        
        # Encontra o módulo
        module_path = self.find_module(module_name)
        if not module_path:
            raise ImportError(f"Módulo '{module_name}' não encontrado")
        
        # Adiciona à pilha de loading
        self.loading_stack.append(module_name)
        
        try:
            # Lê o arquivo do módulo
            with open(module_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Parse do código
            ast = parser.parse(code)
            if not ast:
                raise SyntaxError(f"Erro ao parsear módulo '{module_name}'")
            
            # Cria namespace isolado para o módulo
            module_vars = {}
            original_vars = variaveis.copy()
            variaveis.clear()
            
            # Executa o módulo
            try:
                interpretar(ast)
                module_vars = variaveis.copy()
            finally:
                # Restaura variáveis originais
                variaveis.clear()
                variaveis.update(original_vars)
            
            # Cria objeto Module
            module = Module(module_name, module_path, module_vars)
            
            # Adiciona ao cache
            self.loaded_modules[module_name] = module
            
            return module
        
        finally:
            # Remove da pilha de loading
            self.loading_stack.remove(module_name)
    
    def import_module(self, module_name: str) -> Dict:
        """Importa um módulo e retorna seu namespace"""
        module = self.load_module(module_name)
        return module.get_all_exports()
    
    def import_from(self, module_name: str, names: List[str]) -> Dict:
        """Importa nomes específicos de um módulo"""
        module = self.load_module(module_name)
        
        if '*' in names:
            # Import all
            return module.get_all_exports()
        
        # Import específicos
        imports = {}
        for name in names:
            value = module.get_export(name)
            if value is None:
                raise ImportError(f"Nome '{name}' não encontrado no módulo '{module_name}'")
            imports[name] = value
        
        return imports
    
    def reload_module(self, module_name: str):
        """Recarrega um módulo (útil para desenvolvimento)"""
        if module_name in self.loaded_modules:
            del self.loaded_modules[module_name]
        return self.load_module(module_name)
    
    def list_loaded_modules(self) -> List[str]:
        """Lista todos os módulos carregados"""
        return list(self.loaded_modules.keys())
    
    def clear_cache(self):
        """Limpa o cache de módulos"""
        self.loaded_modules.clear()

# Instância global
module_loader = ModuleLoader()

def import_module(module_name: str) -> Dict:
    """Função helper para importar módulo"""
    return module_loader.import_module(module_name)

def import_from(module_name: str, names: List[str]) -> Dict:
    """Função helper para import from"""
    return module_loader.import_from(module_name, names)










