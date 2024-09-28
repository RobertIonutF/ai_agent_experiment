import os
from ..module import Module

WORKSPACE_DIR = "workspace"

def ensure_workspace_exists():
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)

def sanitize_filename(filename):
    return os.path.normpath(filename).lstrip(os.sep)

def read_file(file_path: str) -> str:
    ensure_workspace_exists()
    safe_path = sanitize_filename(file_path)
    full_path = os.path.join(WORKSPACE_DIR, safe_path)
    try:
        if not os.path.exists(full_path):
            return f"Error: File '{full_path}' does not exist."
        with open(full_path, 'r') as file:
            content = file.read()
        return f"Content of '{full_path}':\n{content}"
    except Exception as e:
        return f"Error reading file '{full_path}': {str(e)}"

def write_file(file_path: str, content: str) -> str:
    ensure_workspace_exists()
    safe_path = sanitize_filename(file_path)
    full_path = os.path.join(WORKSPACE_DIR, safe_path)
    try:
        with open(full_path, 'w') as file:
            file.write(content)
        return f"Successfully wrote content to '{full_path}'"
    except Exception as e:
        return f"Error writing to file '{full_path}': {str(e)}"

file_operations_module = Module("file_operations")
file_operations_module.add_function("read_file", read_file)
file_operations_module.add_function("write_file", write_file)