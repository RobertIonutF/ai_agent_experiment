# AI Agent Project

This project implements an AI agent system capable of executing complex tasks by breaking them down into smaller operations using various modules.

## Project Structure

The project is organized as follows:

- `main.py`: Entry point of the application
- `setup.py`: Configuration for package installation
- `ai_agent/`: Main package directory
  - `__init__.py`: Package initialization
  - `agent.py`: Defines the AIAgent class
  - `commander.py`: Implements the Commander class for processing goals
  - `module.py`: Base class for modules
  - `modules/`: Directory containing various operation modules
    - `__init__.py`: Module initialization
    - `file_operations.py`: File-related operations
    - `web_operations.py`: Web-related operations
    - `google_search_operation.py`: Google search functionality
    - `json_operations.py`: JSON manipulation operations

## Features

- Modular architecture allowing easy addition of new functionalities
- Goal-based task execution
- Error handling and recovery
- Support for file operations, web requests, Google search, and JSON manipulation

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the project directory:
   ```
   cd ai-agent-project
   ```

3. Install the required dependencies:
   ```
   pip install -e .
   ```

## Usage

To use the AI agent, you can modify the `main.py` file or create a new script that utilizes the `AIAgent` and `Commander` classes. Here's a basic example:

```python
from ai_agent import AIAgent, Commander
from ai_agent.modules import all_modules

# Initialize the AI Agent with all available modules
agent = AIAgent()
for module in all_modules:
    agent.add_module(module)

# Initialize the Commander
commander = Commander(agent)

# Process a goal
goal = "Search for the latest news about AI, fetch the content of the top result, save it to a file named 'ai_news.txt' in the workspace, and then read the file content"
result = commander.process_goal(goal)
print("\nFinal Result:")
print(result)
```

## Available Modules

1. File Operations (`file_operations_module`)
   - `read_file(file_path: str) -> str`
   - `write_file(file_path: str, content: str) -> str`

2. Web Operations (`web_operations_module`)
   - `make_get_request(url: str) -> str`
   - `make_post_request(url: str, data: str) -> str`

3. Google Search (`google_search_module`)
   - `google_search(query: str, num_results: int = 5) -> str`

4. JSON Operations (`json_operations_module`)
   - `parse_json(json_string: str) -> str`
   - `get_json_value(json_string: str, key: str) -> str`
   - `create_json(key_value_pairs: str) -> str`
   - `to_json(input_string: str) -> str`

## Extending the Project

To add new functionalities:

1. Create a new module file in the `ai_agent/modules/` directory.
2. Define functions for the new operations.
3. Create a `Module` instance and add the functions to it.
4. Import the new module in `ai_agent/modules/__init__.py` and add it to `all_modules`.

## How to Create Your Own Module

Creating a custom module allows you to extend the AI Agent's capabilities with new functionalities. Here's a step-by-step guide to creating your own module:

1. Create a new Python file in the `ai_agent/modules/` directory. Name it according to its functionality (e.g., `image_processing.py`).

2. Import the necessary dependencies and the `Module` class:

   ```python
   from ..module import Module
   # Import any other required libraries
   ```

3. Define the functions for your module. Each function should take string inputs and return a string output:

   ```python
   def process_image(image_path: str) -> str:
       # Implement your image processing logic here
       return "Image processed successfully"

   def generate_thumbnail(image_path: str, size: str) -> str:
       # Implement thumbnail generation logic here
       return f"Thumbnail generated with size {size}"
   ```

4. Create an instance of the `Module` class and add your functions to it:

   ```python
   image_processing_module = Module("image_processing")
   image_processing_module.add_function("process_image", process_image)
   image_processing_module.add_function("generate_thumbnail", generate_thumbnail)
   ```

5. Open `ai_agent/modules/__init__.py` and import your new module:

   ```python
   from .image_processing import image_processing_module
   ```

6. Add your module to the `all_modules` list in `ai_agent/modules/__init__.py`:

   ```python
   all_modules = [
       file_operations_module,
       web_operations_module,
       json_operations_module,
       image_processing_module,  # Add your new module here
   ]
   ```

7. Your new module is now ready to use! The AI Agent will automatically include it when processing goals.

Remember to handle exceptions in your module functions and return informative error messages as strings when operations fail.

## Environment Variables

Make sure to set the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL` (optional): The OpenAI model to use (default: "gpt-3.5-turbo")

You can use a `.env` file to store these variables.

## License

[Specify the license here]

## Contributing

[Add contribution guidelines if applicable]