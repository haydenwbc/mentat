import os
import subprocess
import sys
from dotenv import load_dotenv
from core.environment import Environment
from core.backend import LLMConfig
from core.core import Core

# Constants
ENV_FILE = ".env"
POETRY_CMD = "poetry"
VENV_PYTHON = ".venv/bin/python" if os.name != "nt" else ".venv\\Scripts\\python"

def check_python_version():
    """Ensure Python 3.12 or higher is installed."""
    if sys.version_info < (3, 12):
        print("Python 3.12 or higher is required. Please upgrade Python and try again.")
        sys.exit(1)

def is_poetry_installed():
    """Check if Poetry is installed."""
    try:
        subprocess.run([POETRY_CMD, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def install_poetry():
    """Install Poetry."""
    print("Installing Poetry...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "poetry"], check=True)
    print("Poetry installed successfully.")

def install_dependencies():
    """Install project dependencies using Poetry."""
    print("Installing dependencies with Poetry...")
    try:
        subprocess.run([POETRY_CMD, "install"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def setup_llm() -> bool:
    """Set up LLM configuration."""
    llm_backend = LLMConfig()
    
    if llm_backend.is_configured():
        print("\nLLM is already configured.")
        reconfigure = input("Would you like to reconfigure? (y/N): ").lower().strip()
        if reconfigure != 'y':
            return True
    
    return llm_backend.setup_interactive()

def bootstrap():
    """Run the bootstrap process."""
    print("Starting bootstrap process...")
    check_python_version()
    
    if not is_poetry_installed():
        install_poetry()
    
    env = Environment()
    env.create_default_env()
    install_dependencies()
    
    if not setup_llm():
        print("LLM configuration failed. Please try again.")
        sys.exit(1)
    
    env.set_env_var("BOOTSTRAP_COMPLETE", "true")
    print("Bootstrap process complete!")

def is_bootstrap_complete():
    """Check if the bootstrap process is complete."""
    if os.path.exists(ENV_FILE):
        load_dotenv(ENV_FILE)
        return os.getenv("BOOTSTRAP_COMPLETE", "false").lower() == "true"
    return False

def is_inside_virtual_env():
    """Check if the script is running inside the virtual environment."""
    venv_path = os.path.abspath(".venv")
    current_python = os.path.abspath(sys.executable)
    return os.path.exists(venv_path) and current_python.startswith(venv_path)

def run_application():
    """Start the application."""
    try:
        print("\nWelcome to Mentat!")
        
        # Initialize core
        core = Core()
        
        # Load and configure all workflows first
        print("\nChecking workflow configurations...")
        workflows = core.discover_workflows()
        
        if not workflows:
            print("No workflows available. Please check the workflows directory.")
            return
            
        # Display available workflows
        print("\nAvailable workflows:")
        for workflow in workflows:
            print(f"- {workflow['name']}: {workflow['description']}")
        
        # Get example commands from all configured workflows
        all_examples = []
        for workflow in core.workflow_manager.workflows.values():
            all_examples.extend(workflow.get_example_commands())
        
        if all_examples:
            print("\nExample commands:")
            for example in all_examples:
                print(f'- "{example}"')
        
        while True:
            try:
                command = input("\nEnter command (or 'exit' to quit, 'help' for examples): ").strip()
                
                if command.lower() == 'exit':
                    break
                    
                if command.lower() == 'help':
                    print("\nExample commands:")
                    for example in all_examples:
                        print(f'- "{example}"')
                    continue
                
                result = core.execute_command(command)
                if result:
                    print(result)
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
                
    except Exception as e:
        print(f"Error running application: {e}")

def main():
    if not is_bootstrap_complete():
        print("System not set up. Running bootstrap process...")
        bootstrap()
    
    if not is_inside_virtual_env():
        if os.path.exists(VENV_PYTHON):
            print("Relaunching inside virtual environment...")
            try:
                subprocess.run([VENV_PYTHON, *sys.argv], check=True)
                sys.exit(0)
            except subprocess.CalledProcessError as e:
                print(f"Error relaunching in virtual environment: {e}")
                sys.exit(1)
        else:
            print("Virtual environment Python interpreter not found. Running bootstrap again...")
            bootstrap()
            if os.path.exists(VENV_PYTHON):
                subprocess.run([VENV_PYTHON, *sys.argv], check=True)
            else:
                print("Failed to create virtual environment.")
            sys.exit(1)
    else:
        print("Running inside virtual environment")
        run_application()

if __name__ == "__main__":
    main()