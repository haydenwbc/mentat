import os
from typing import Optional
from dotenv import load_dotenv, set_key, unset_key

class Environment:
    """Manages environment variables for the Core module."""
    
    def __init__(self):
        self.env_file = ".env"
        load_dotenv(self.env_file)

    def get_env_var(self, var_name: str) -> Optional[str]:
        """Safely retrieve an environment variable."""
        return os.getenv(var_name)

    def set_env_var(self, var_name: str, value: str) -> None:
        """Set an environment variable and save to .env file."""
        # Update the environment
        os.environ[var_name] = value
        # Update the .env file
        set_key(self.env_file, var_name, value)

    def unset_env_var(self, var_name: str) -> None:
        """Remove an environment variable."""
        if var_name in os.environ:
            del os.environ[var_name]
        unset_key(self.env_file, var_name)

    def create_default_env(self) -> None:
        """Create a default .env file if it doesn't exist."""
        if not os.path.exists(self.env_file):
            print("Creating default .env file...")
            with open(self.env_file, "w") as f:
                f.write("""# LLM Configuration
LLM_PROVIDER=
LLM_MODEL=

# Provider API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# System Configuration
BOOTSTRAP_COMPLETE=false
""")