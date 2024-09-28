from typing import List, Dict
from .module import Module

class AIAgent:
    def __init__(self):
        self.modules = {}

    def add_module(self, module):
        self.modules[module.name] = module

    def list_modules(self):
        return list(self.modules.keys())

    def execute_module(self, module_name, function_name, *args):
        if module_name in self.modules:
            return self.modules[module_name].execute(function_name, *args)
        else:
            raise ValueError(f"Module '{module_name}' not found")