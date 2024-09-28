import os
import openai
import json
from dotenv import load_dotenv
from .agent import AIAgent
import re
from .modules.json_operations import json_operations_module

WORKSPACE_DIR = "workspace"

class Commander:
    def __init__(self, agent: AIAgent):
        self.agent = agent
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        if not openai.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.conversation_history = []
        self.agent.add_module(json_operations_module)

    def process_goal(self, goal: str) -> str:
        self.goal = goal
        self.conversation_history.append(("user", goal))
        iteration = 1
        while True:
            try:
                print(f"\n--- Iteration {iteration} ---")
                plan = self._create_plan()
                print("Plan:")
                print(plan)
                self.conversation_history.append(("assistant", plan))
                result = self._execute_plan(plan)
                print("\nExecution Result:")
                print(result)
                evaluation = self._evaluate_result(result)
                print("\nEvaluation:")
                print(evaluation)
                if self._is_goal_achieved(evaluation):
                    return "Goal achieved successfully."
                iteration += 1
            except Exception as e:
                error_msg = f"Error in iteration {iteration}: {str(e)}"
                print(f"\nError occurred: {error_msg}")
                solution = self._get_error_solution(error_msg, "process_goal", "iteration", [str(iteration)])
                print("Proposed solution:")
                print(solution)
                self.conversation_history.append(("error", error_msg))
                self.conversation_history.append(("solution", solution))
                continue_execution = input("Do you want to continue execution? (yes/no): ")
                if continue_execution.lower() != 'yes':
                    return "Execution stopped due to error."

    def _execute_plan(self, plan: str) -> str:
        lines = plan.strip().split('\n')
        result = []
        executing_plan = False
        step_results = {}
        plan_steps = []

        for line in lines:
            if line.lower().startswith("plan:"):
                executing_plan = True
                continue
            if executing_plan and line.strip():
                plan_steps.append(line.strip())

        for i, step in enumerate(plan_steps):
            try:
                # Remove the step number if present
                step = re.sub(r'^\d+\.\s*', '', step)
                
                parts = step.split(',', 1)
                if len(parts) < 1:
                    raise ValueError(f"Invalid step format: {step}")
                
                module_func = parts[0].strip()
                args = parts[1].strip() if len(parts) > 1 else ""
                
                module_parts = module_func.split('.')
                if len(module_parts) != 2:
                    raise ValueError(f"Invalid module.function format: {module_func}")
                
                module_name, function_name = module_parts
                args = [self._process_arg(arg.strip(), step_results) for arg in args.split(',') if arg.strip()]

                # Ask for permission before executing each step
                permission = input(f"Do you want to execute: {module_name}.{function_name}{tuple(args)}? (yes/no): ")
                if permission.lower() != 'yes':
                    result.append(f"Skipped: {module_name}.{function_name}{tuple(args)}")
                    continue

                if function_name == 'make_get_request' and args:
                    url = args[0]
                    if not self._is_valid_url(url):
                        raise ValueError(f"Invalid URL: {url}")

                module_result = self.agent.execute_module(module_name, function_name, *args)
                
                # Try to convert the result to JSON if it's not already
                if module_name != 'json_operations' and isinstance(module_result, str):
                    try:
                        json_result = self.agent.execute_module("json_operations", "to_json", module_result)
                        if not json_result.startswith("Error"):
                            module_result = json_result
                    except:
                        pass  # If conversion fails, keep the original result

                result.append(f"{module_name}.{function_name} result: {module_result}")
                step_results[f"result from step {len(result)}"] = module_result

                # Evaluate the result and potentially modify the plan
                plan_modification = self._evaluate_step_result(module_result, i, plan_steps)
                if plan_modification and not plan_modification.startswith("No modification needed"):
                    print("\nPlan modification suggested:")
                    print(plan_modification)
                    apply_modification = input("Do you want to apply this modification? (yes/no): ")
                    if apply_modification.lower() == 'yes':
                        plan_steps = self._modify_plan(plan_steps, i, plan_modification)
                        print("\nUpdated plan:")
                        for j, updated_step in enumerate(plan_steps[i+1:], start=i+1):
                            print(f"{j}. {updated_step}")

                if "Error" in module_result:
                    solution = self._get_error_solution(module_result, module_name, function_name, args)
                    result.append(f"Error solution: {solution}")
            except Exception as e:
                error_msg = f"Error executing step: {step}. Error: {str(e)}"
                result.append(error_msg)
                print(f"\nError occurred: {error_msg}")
                solution = self._get_error_solution(error_msg, "unknown", "unknown", [])
                print("Proposed solution:")
                print(solution)
                result.append(f"Error solution: {solution}")
                continue_execution = input("Do you want to continue execution? (yes/no): ")
                if continue_execution.lower() != 'yes':
                    result.append("Execution stopped due to error.")
                    break

        return "\n".join(result)

    def _evaluate_result(self, result: str) -> str:
        prompt = f"""
        Goal: {self.goal}
        Execution result:
        {result}

        Has the goal been achieved? If not, what steps should be taken next?
        Consider the following:
        1. Are the results in JSON format? If not, suggest converting them to JSON.
        2. Is the data structured properly for easy manipulation and storage?
        3. Are there any remaining tasks that need to be completed to fully achieve the goal?

        Provide your analysis and next steps in the following format:

        Analysis:
        1. [Point 1]
        2. [Point 2]
        ...

        Next steps:
        1. [Step 1]
        2. [Step 2]
        ...

        Goal achieved: [Yes/No]

        Response:
        """

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an AI assistant that evaluates the results of executed plans and determines if the goal has been achieved. If not, you provide guidance on what steps to take next. Prefer working with JSON data whenever possible."},
                {"role": "user", "content": prompt}
            ]
        )

        evaluation = response.choices[0].message.content
        self.conversation_history.append(("assistant", evaluation))
        return evaluation

    def _is_goal_achieved(self, evaluation: str) -> bool:
        return "Goal achieved: Yes" in evaluation

    def _format_available_modules(self):
        formatted_modules = []
        for module_name, module in self.agent.modules.items():
            functions = module.list_functions()
            formatted_modules.append(f"{module_name}: {', '.join(functions)}")
        return "\n".join(formatted_modules)

    def _format_conversation_history(self):
        if not self.conversation_history:
            return "No previous conversation."
        return "\n".join([f"{role.capitalize()}: {content}" for role, content in self.conversation_history[-5:]])

    def _process_arg(self, arg, step_results):
        if arg.startswith('[') and arg.endswith(']'):
            step_ref = arg.strip('[]')
            if step_ref.startswith('result from step'):
                step_num = int(step_ref.split()[-1])
                if f"result from step {step_num}" in step_results:
                    result = step_results[f"result from step {step_num}"]
                    if isinstance(result, str):
                        # Try to parse the result as JSON
                        try:
                            json.loads(result)
                            return result  # Return the JSON string if it's valid
                        except json.JSONDecodeError:
                            # If it's not valid JSON, proceed with the existing logic
                            if "google_search.google_search result:" in result:
                                lines = result.split('\n')
                                for line in lines:
                                    if 'http' in line or 'https' in line:
                                        url = line.split()[-1].strip()
                                        if url.startswith('http') or url.startswith('https'):
                                            return url
                            elif result.startswith('http'):
                                return result.split('\n')[0].strip()
                    return result
        return arg.strip('"')  # Remove quotes from arguments

    def _is_valid_url(self, url):
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url is not None and url_pattern.match(url)

    def _get_error_solution(self, error_message, module_name, function_name, args):
        prompt = f"""
        An error occurred while executing a step in the plan:
        Module: {module_name}
        Function: {function_name}
        Arguments: {args}
        Error message: {error_message}

        Previous conversation and reasoning:
        {self._format_conversation_history()}

        Please provide a solution to this error. Consider the following:
        1. Is there an issue with the arguments passed to the function?
        2. Is there a problem with the function itself?
        3. Is there an alternative approach using other available modules and functions?
        4. How can we modify the plan to overcome this error and continue towards the goal?

        Provide a step-by-step solution to resolve this error and continue with the plan.

        Solution:
        """

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an AI assistant that helps solve errors in execution plans and suggests modifications to achieve the goal."},
                {"role": "user", "content": prompt}
            ]
        )

        solution = response.choices[0].message.content
        self.conversation_history.append(("user", f"Error: {error_message}"))
        self.conversation_history.append(("assistant", f"Solution: {solution}"))
        return solution

    def _evaluate_step_result(self, result: str, step_index: int, remaining_steps: list) -> str:
        prompt = f"""
        Goal: {self.goal}
        Step result: {result}
        Current step index: {step_index}
        Remaining steps in the plan:
        {self._format_remaining_steps(remaining_steps[step_index+1:])}

        Previous conversation and reasoning:
        {self._format_conversation_history()}

        Evaluate if this result compromises the initial plan or if the plan needs to be adapted.
        If a modification is needed, provide a detailed explanation and the modified steps.
        If no modification is needed, respond with "No modification needed."

        Response format:
        Explanation: [Your explanation here]
        Modified steps:
        1. [Modified step 1]
        2. [Modified step 2]
        ...

        Response:
        """

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an AI assistant that evaluates execution results and suggests plan modifications if necessary to achieve the goal."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    def _modify_plan(self, plan_steps: list, current_step: int, modification: str) -> list:
        modified_steps = []
        for line in modification.split('\n'):
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                modified_steps.append(line.split('.', 1)[1].strip())
        
        return plan_steps[:current_step+1] + modified_steps

    def _format_remaining_steps(self, steps: list) -> str:
        return "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))

    def _create_plan(self) -> str:
        available_modules = self.agent.list_modules()
        prompt = f"""
        Goal: {self.goal}
        Available modules and their functions:
        {self._format_available_modules()}

        Workspace information:
        - All files should be created or accessed in the '{WORKSPACE_DIR}' folder.
        - When using file operations, provide only the filename, not the full path.

        Guidelines for creating the plan:
        1. Analyze the available modules and their functions to determine the best approach for achieving the goal.
        2. Break down complex tasks into smaller, manageable steps.
        3. Use the results from previous steps in subsequent steps when necessary.
        4. Ensure that each step in the plan uses the correct module and function for the task at hand.
        5. If a previous attempt failed, consider alternative approaches.
        6. Whenever possible, use JSON for data storage and manipulation. Use the json_operations module to work with JSON data.
        7. When fetching data from web sources, try to convert the results to JSON format using json_operations.to_json.
        8. When writing data to files, prefer JSON format for structured data.

        Previous conversation and reasoning:
        {self._format_conversation_history()}

        Reason step-by-step about how to achieve the goal using the available modules and functions. 
        Then, provide a detailed plan of action using the following format:

        Reasoning:
        1. [Step 1 of reasoning]
        2. [Step 2 of reasoning]
        ...

        Plan:
        1. [Module name].[Function name], [Argument 1], [Argument 2], ...
        2. [Module name].[Function name], [Argument 1], [Argument 2], ...
        ...

        Response:
        """

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an AI assistant that creates detailed, step-by-step plans to achieve goals using available modules and functions. Analyze the modules and their functions carefully to determine the best approach. Learn from previous interactions and errors to improve your plans. Prefer working with JSON data whenever possible."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content