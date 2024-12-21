import os
import subprocess
import sys
from dotenv import load_dotenv

# Constants
ENV_FILE = ".env"
POETRY_CMD = "poetry"
VENV_PYTHON = ".venv/bin/python" if os.name != "nt" else ".venv\\Scripts\\python"

def check_python_version():
    """Ensure Python 3.x is installed."""
    if sys.version_info.major < 3:
        print("Python 3.x is required. Please install Python 3 and try again.")
        sys.exit(1)

def is_poetry_installed():
    """Check if Poetry is installed."""
    try:
        subprocess.run([POETRY_CMD, "--version"], check=True, stdout=subprocess.PIPE)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def install_poetry():
    """Install Poetry."""
    print("Installing Poetry...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "poetry"], check=True)
    print("Poetry installed successfully.")

def create_env_file():
    """Create a .env file with placeholders if it doesn't exist."""
    if not os.path.exists(ENV_FILE):
        print("Setting up environment variables...")
        with open(ENV_FILE, "w") as env_file:
            env_file.write("""# Core LLM Backend Configuration
OPENAI_API_KEY=
# Placeholder for Git/GitHub Integration
GIT_USERNAME=
GIT_TOKEN=
BOOTSTRAP_COMPLETE=false
""")
        print(".env file created with placeholders.")
    else:
        print(".env file already exists.")

def update_env(key, value):
    """Update or add a key-value pair in the .env file."""
    if not os.path.exists(ENV_FILE):
        create_env_file()

    with open(ENV_FILE, "r") as env_file:
        lines = env_file.readlines()

    updated = False
    with open(ENV_FILE, "w") as env_file:
        for line in lines:
            if line.startswith(f"{key}="):
                env_file.write(f"{key}={value}\n")
                updated = True
            else:
                env_file.write(line)
        if not updated:
            env_file.write(f"{key}={value}\n")

def is_bootstrap_complete():
    """Check if the bootstrap process is complete by reading the .env file."""
    load_dotenv(ENV_FILE)
    return os.getenv("BOOTSTRAP_COMPLETE", "false").lower() == "true"

def is_inside_virtual_env():
    """Check if the script is running inside the virtual environment."""
    # Check if the virtual environment variable is set
    if os.getenv("VIRTUAL_ENV"):
        return True
    # Check if sys.prefix differs from sys.base_prefix
    if hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix:
        return True
    # Check if the virtual environment folder exists
    if os.path.exists(".venv"):
        return sys.executable.startswith(os.path.abspath(".venv"))
    return False

def install_dependencies():
    """Install project dependencies using Poetry."""
    print("Installing dependencies with Poetry...")
    subprocess.run([POETRY_CMD, "install"], check=True)
    print("Dependencies installed successfully.")

def bootstrap():
    """Run the bootstrap process."""
    check_python_version()
    if not is_poetry_installed():
        install_poetry()
    create_env_file()
    install_dependencies()
    update_env("BOOTSTRAP_COMPLETE", "true")
    print("Bootstrap process complete!")

def run_application():
    """Start the application."""
    print("Starting Mentat...")
    print("Welcome to Mentat. Please choose a workflow.")
    # Placeholder functionality
    print("Functionality not implemented yet.")

def main():
    if not is_bootstrap_complete():
        print("System not set up. Running bootstrap process...")
        bootstrap()
        # Relaunch the script inside the virtual environment
        print("Relaunching the script inside the virtual environment...")
        subprocess.run([VENV_PYTHON, *sys.argv])
        sys.exit(0)
    elif not is_inside_virtual_env():
        # Relaunch if not already inside the virtual environment
        print("Not running inside the virtual environment. Relaunching...")
        subprocess.run([VENV_PYTHON, *sys.argv])
        sys.exit(0)
    else:
        print("System is already set up and running inside the virtual environment.")
        print(f"Current environment: {os.getenv('VIRTUAL_ENV') or 'Not in a virtual environment'}")
        run_application()

if __name__ == "__main__":
    main()
