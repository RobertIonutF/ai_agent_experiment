from ai_agent.agent import AIAgent
from ai_agent.commander import Commander
from ai_agent.modules.file_operations import file_operations_module
from ai_agent.modules.web_operations import web_operations_module
from ai_agent.modules.google_search_operation import google_search_module
from ai_agent.modules.json_operations import json_operations_module

# Initialize the AI Agent with all available modules
agent = AIAgent()
agent.add_module(file_operations_module)
agent.add_module(web_operations_module)
agent.add_module(google_search_module)
agent.add_module(json_operations_module)

# Initialize the Commander
commander = Commander(agent)

# Process a goal
goal = "Search for the latest news about AI, fetch the content of the top result, save it to a file named 'ai_news.txt' in the workspace, and then read the file content"
result = commander.process_goal(goal)
print("\nFinal Result:")
print(result)