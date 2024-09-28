from typing import Callable

class Module:
    def __init__(self, name):
        self.name = name
        self.functions = {}

    def add_function(self, name, function):
        self.functions[name] = function

    def execute(self, function_name, *args):
        if function_name in self.functions:
            return self.functions[function_name](*args)
        else:
            raise ValueError(f"Function '{function_name}' not found in module '{self.name}'")

    def list_functions(self):
        return list(self.functions.keys())