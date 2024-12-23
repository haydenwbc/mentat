from typing import Optional, Dict, Tuple, List, Any
import os
from litellm import completion
import litellm

class LLMConfig:
    """Manages LLM backend configuration and interactions."""
    
    SUPPORTED_PROVIDERS = {
        'openai': ['gpt-4', 'gpt-3.5-turbo'],
        'anthropic': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229']
    }

    # Shorthand names for models
    MODEL_ALIASES = {
        'openai': {
            'gpt4': 'gpt-4',
            'gpt3': 'gpt-3.5-turbo',
            '4': 'gpt-4',
            '3.5': 'gpt-3.5-turbo'
        },
        'anthropic': {
            'opus': 'claude-3-opus-20240229',
            'sonnet': 'claude-3-sonnet-20240229',
            'claude-opus': 'claude-3-opus-20240229',
            'claude-sonnet': 'claude-3-sonnet-20240229'
        }
    }

    def __init__(self):
        self.provider = None
        self.model = None
        self.api_key = None
        litellm.set_verbose = True
        self.conversation_state = {
            'active': False,
            'context': {},
            'history': [],
            'current_task': None
        }

    def get_provider_models(self, provider: str) -> list:
        """Get available models for a provider."""
        return self.SUPPORTED_PROVIDERS.get(provider, [])

    def find_matching_model(self, provider: str, user_input: str) -> List[str]:
        """Find models that match the user input, including aliases."""
        user_input = user_input.lower().strip()
        matches = []
        
        # Check full model names
        full_models = self.SUPPORTED_PROVIDERS.get(provider, [])
        for model in full_models:
            if user_input in model.lower():
                matches.append(model)
        
        # Check aliases
        aliases = self.MODEL_ALIASES.get(provider, {})
        for alias, full_name in aliases.items():
            if user_input in alias.lower():
                matches.append(full_name)
        
        return list(set(matches))  # Remove duplicates

    def setup_interactive(self) -> bool:
        """Interactive setup for LLM configuration."""
        print("\nLLM Backend Configuration")
        print("------------------------")
        print("Available providers:")
        for provider in self.SUPPORTED_PROVIDERS.keys():
            print(f"- {provider}")

        while True:
            provider = input("\nSelect provider (openai/anthropic): ").lower().strip()
            if provider in self.SUPPORTED_PROVIDERS:
                break
            print("Invalid provider. Please try again.")

        print(f"\nAvailable models for {provider}:")
        for model in self.SUPPORTED_PROVIDERS[provider]:
            print(f"- {model}")
        
        # Show aliases
        print("\nYou can also use these shortcuts:")
        for alias, full_name in self.MODEL_ALIASES[provider].items():
            print(f"- {alias} → {full_name}")

        while True:
            model_input = input("\nSelect model (type part of name for suggestions): ").strip()
            matches = self.find_matching_model(provider, model_input)
            
            if not matches:
                print("No matching models found. Try again or type '?' for available options.")
                continue
                
            if len(matches) == 1:
                model = matches[0]
                print(f"Selected model: {model}")
                break
            else:
                print("\nMultiple matches found:")
                for idx, match in enumerate(matches, 1):
                    print(f"{idx}. {match}")
                while True:
                    try:
                        choice = input("Select number (or press Enter to try again): ").strip()
                        if not choice:  # User wants to try again
                            break
                        choice_idx = int(choice) - 1
                        if 0 <= choice_idx < len(matches):
                            model = matches[choice_idx]
                            print(f"Selected model: {model}")
                            break
                        else:
                            print("Invalid selection. Try again.")
                    except ValueError:
                        print("Please enter a number or press Enter to try again.")
                if choice:  # If user made a valid choice
                    break

        while True:
            api_key = input(f"\nEnter your {provider.upper()} API key: ").strip()
            is_valid, message = self.validate_api_key(provider, api_key)
            if not is_valid:
                print(f"Invalid API key: {message}")
                continue
                
            print("\nValidating API key...")
            test_result, error_message = self.test_configuration(provider, model, api_key)
            
            if test_result:
                self.provider = provider
                self.model = model
                self.api_key = api_key
                self._save_config()
                return True
                
            print(f"\nConfiguration test failed: {error_message}")
            retry = input("Would you like to try again? (Y/n): ").lower().strip()
            if retry == 'n':
                return False

    def validate_api_key(self, provider: str, api_key: str) -> Tuple[bool, str]:
        """Validate API key format and basic requirements."""
        if not api_key:
            return False, "API key cannot be empty"
            
        if provider == 'openai' and not api_key.startswith('sk-'):
            return False, "OpenAI API keys should start with 'sk-'"
            
        if provider == 'anthropic' and not api_key.startswith('sk-ant-'):
            return False, "Anthropic API keys should start with 'sk-ant-'"
            
        return True, "API key format is valid"

    def test_configuration(self, provider: str, model: str, api_key: str) -> Tuple[bool, str]:
        """Test LLM configuration with a simple completion."""
        try:
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
            response = completion(
                model=model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True, "Configuration test successful"
            
        except litellm.exceptions.RateLimitError as e:
            if "insufficient_quota" in str(e):
                return False, f"Your {provider} account has insufficient credits. Please check your billing details."
            return False, f"Rate limit exceeded. Please try again later."
            
        except litellm.exceptions.InvalidRequestError as e:
            return False, f"Invalid request: {str(e)}"
            
        except litellm.exceptions.AuthenticationError as e:
            return False, f"Authentication failed. Please check your API key."
            
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def _save_config(self) -> None:
        """Save configuration to environment file."""
        from .environment import Environment
        env = Environment()
        
        # Clear any existing LLM configurations
        for provider in self.SUPPORTED_PROVIDERS:
            env.unset_env_var(f"{provider.upper()}_API_KEY")
        
        # Save new configuration
        env.set_env_var(f"{self.provider.upper()}_API_KEY", self.api_key)
        env.set_env_var("LLM_PROVIDER", self.provider)
        env.set_env_var("LLM_MODEL", self.model)

    def is_configured(self) -> bool:
        """Check if LLM is properly configured."""
        from .environment import Environment
        env = Environment()
        
        provider = env.get_env_var("LLM_PROVIDER")
        model = env.get_env_var("LLM_MODEL")
        
        if not provider or not model:
            return False
            
        api_key = env.get_env_var(f"{provider.upper()}_API_KEY")
        if not api_key:
            return False
            
        is_valid, _ = self.validate_api_key(provider, api_key)
        if not is_valid:
            return False
            
        return True

    def start_conversation(self, task: str, initial_context: Dict[str, Any] = None) -> None:
        """Start a new conversation with the LLM."""
        self.conversation_state = {
            'active': True,
            'context': {
                **(initial_context or {}),
                'system': self._get_system_context(),
                'task': task
            },
            'history': [],
            'current_task': task
        }

    def _get_system_context(self) -> Dict[str, Any]:
        """Get system context information."""
        import platform
        import os
        
        context = {
            'os': platform.system(),
            'terminal': os.environ.get('TERM', 'unknown'),
            'project_root': os.getcwd(),
            'workflows_available': self._get_available_workflows(),
            'assistant_name': 'Thufir',
            'personality': """
            You are Thufir, a thoughtful and knowledgeable assistant who helps users with technical tasks.
            You have a calm, methodical approach and always explain what you're doing.
            You present options clearly and let users make informed choices.
            """
        }
        return context

    def _get_available_workflows(self) -> List[str]:
        """Get list of available workflow directories."""
        workflows_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workflows')
        return [d for d in os.listdir(workflows_dir) 
                if os.path.isdir(os.path.join(workflows_dir, d)) 
                and not d.startswith('__')]

    def pause_conversation(self) -> None:
        """Pause the current conversation to handle terminal interaction."""
        if self.conversation_state['active']:
            self.conversation_state['context']['paused_at'] = len(self.conversation_state['history'])

    def resume_conversation(self) -> Optional[str]:
        """Resume a paused conversation."""
        if not self.conversation_state['active']:
            return None

        context = self.conversation_state['context']
        history = self.conversation_state['history']
        
        resume_prompt = f"""
        Resuming our previous conversation about {self.conversation_state['current_task']}.
        Context: {context}
        Previous interaction: {history[-1] if history else 'Starting fresh'}
        
        Please continue where we left off.
        """
        
        return self.get_completion(resume_prompt)

    def add_to_history(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        if self.conversation_state['active']:
            self.conversation_state['history'].append({
                'role': role,
                'content': content
            })

    def get_completion(self, prompt: str, role: str = "user") -> Optional[str]:
        """Get a completion with enhanced context awareness."""
        if not self.provider or not self.model:
            from .environment import Environment
            env = Environment()
            self.provider = env.get_env_var("LLM_PROVIDER")
            self.model = env.get_env_var("LLM_MODEL")
            
            if not self.provider or not self.model:
                print("LLM not configured. Run setup first.")
                return None
        
        try:
            messages = []
            
            # Add conversation history if in active conversation
            if self.conversation_state['active']:
                messages.extend(self.conversation_state['history'])
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Create focused system prompt based on task
            if self.conversation_state['active']:
                task = self.conversation_state['current_task']
                context = self.conversation_state['context']
                
                if 'twitter_setup' in task:
                    system_prompt = """
                    You are an expert at configuring Twitter API access and OAuth permissions.
                    Focus on helping the user fix OAuth write permissions issues.
                    Current context: {system_context}
                    
                    Guidelines:
                    1. Be specific about Twitter Developer Portal locations
                    2. Mention exact UI elements and settings
                    3. Give one clear step at a time
                    4. Focus on write permissions configuration
                    """
                else:
                    system_prompt = """
                    You are Thufir, a technical assistant helping users with workflow automation.
                    Always introduce yourself when starting a new conversation.
                    Present available workflows and let users choose.
                    Be conversational but concise.
                    Current context: {system_context}
                    """
                
                messages = [
                    {"role": "system", "content": system_prompt.format(
                        system_context=context
                    )}
                ]
                messages.extend(self.conversation_state['history'])
            
            response = completion(
                model=self.model,
                messages=messages
            )
            
            # Store in conversation history if active
            if self.conversation_state['active']:
                self.add_to_history("user", prompt)
                self.add_to_history("assistant", response.choices[0].message.content)
                
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting completion: {e}")
            return None