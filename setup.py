from setuptools import setup, find_packages

setup(
    name="ai_agent",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openai",
        "requests",
        "beautifulsoup4",
        "python-dotenv",
        # Add any other dependencies here
    ],
)