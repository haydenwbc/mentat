from typing import Optional, List, Dict
import os
import importlib
import inspect
from core.backend import LLMConfig
from core.workflow import WorkflowManager, Workflow
from core.parser import CommandParser

class Core:
    """Core class managing the Mentat system."""
    
    def __init__(self):
        self.llm = LLMConfig()
        self.workflow_manager = WorkflowManager()
        self.command_parser = CommandParser(self.llm)
        self.workflows_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'workflows')

    def discover_workflows(self) -> List[Dict[str, str]]:
        """
        Load and configure all available workflows.
        
        Returns:
            List[Dict[str, str]]: List of properly configured and validated workflows
            
        Note:
            Only returns workflows that are properly configured and validated.
            Workflows with missing or invalid credentials are logged but not returned.
        """
        available = []
        
        if not os.path.exists(self.workflows_dir):
            print("\nThufir: I couldn't find any workflows to work with. Let me help you set those up.")
            return available

        print("\nThufir: I'm checking which workflows are available...")
        
        for item in os.listdir(self.workflows_dir):
            workflow_dir = os.path.join(self.workflows_dir, item)
            if os.path.isdir(workflow_dir) and not item.startswith('__'):
                print(f"\nChecking workflow: {item}")
                try:
                    module = importlib.import_module(f'workflows.{item}.{item}')
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, Workflow) and 
                            obj != Workflow):
                            # Initialize the workflow
                            workflow = obj()
                            
                            # Validate workflow
                            print(f"Validating {item} workflow configuration...")
                            if workflow.validate_environment():
                                print(f"✓ {item} workflow validated successfully")
                                self.workflow_manager.register_workflow(workflow)
                                available.append({
                                    "name": workflow.get_name(),
                                    "description": workflow.get_description()
                                })
                            else:
                                print(f"✗ {item} workflow is not properly configured")
                            break
                            
                except Exception as e:
                    print(f"Error loading workflow {item}: {str(e)}")
                    import traceback
                    print(f"Stack trace:\n{traceback.format_exc()}")
                    
        return available

    def get_available_workflows(self) -> List[Dict[str, str]]:
        """Get list of available workflows."""
        return self.workflow_manager.get_available_workflows()
        
    def execute_command(self, command: str) -> Optional[str]:
        """Execute a natural language command."""
        try:
            if command.lower() == "help":
                return self._show_help()
            
            if command.lower() == "troubleshoot":
                return self._start_troubleshooting()
                
            if not self.workflow_manager.get_available_workflows():
                print("\nThufir: I don't see any configured workflows. Would you like me to help you set one up?")
                return None
                
            if command.lower() == "help":
                workflows = self.workflow_manager.get_available_workflows()
                print("\nThufir: Here are the workflows I can help you with:")
                for w in workflows:
                    print(f"- {w['name']}: {w['description']}")
                return None
                
            # Parse the command
            workflow_name, command_name, params = self.command_parser.parse_command(command)
            
            # Get the workflow
            workflow = self.workflow_manager.get_workflow(workflow_name)
            if not workflow:
                raise ValueError(f"Workflow '{workflow_name}' not found or not properly configured")
            
            # Execute the command
            return self.workflow_manager.execute_workflow_command(
                workflow_name, command_name, **params
            )
            
        except ValueError as e:
            print(f"Error: {e}")
            print("\nHint:", self.command_parser.get_command_help())
        except EnvironmentError as e:
            print(f"Configuration Error: {e}")
            print("Please ensure all required environment variables are set.")
        except Exception as e:
            print(f"\nThufir: I encountered an issue: {e}")
            print("Would you like help troubleshooting? (y/N)")
            if input().lower().strip() == 'y':
                return self._start_troubleshooting(str(e))
            else:
                print("Let me know if you need help later - just type 'troubleshoot'")
        return None

    def _start_troubleshooting(self, error_context: str = None) -> str:
        """Start an interactive troubleshooting session."""
        if not self.llm.is_configured():
            return "Sorry, I need LLM configuration to help with troubleshooting."
            
        context = {
            'workflows': self.workflow_manager.get_available_workflows(),
            'error': error_context,
            'system_status': {
                'llm_configured': self.llm.is_configured(),
                'workflows_loaded': bool(self.workflow_manager.workflows)
            }
        }
        
        self.llm.start_conversation("troubleshooting", context)
        
        print("\nThufir: I'll help you troubleshoot. What seems to be the problem?")
        while True:
            user_input = input("> ").strip().lower()
            
            if user_input in ['exit', 'quit', 'done']:
                print("Thufir: Alright, let me know if you need anything else!")
                break
                
            response = self.llm.get_completion(user_input)
            if response:
                print(f"\nThufir: {response}")
                
                # Check if the issue is resolved
                print("\nDid that solve your issue? (y/N/exit)")
                if input().lower().strip() == 'y':
                    return "Glad I could help! Let me know if you need anything else."
            else:
                print("I'm having trouble generating a response. Please try rephrasing or type 'exit' to quit.")
                
        return None

    def _show_help(self) -> str:
        """Show available commands and workflows."""
        help_text = "\nAvailable Commands:\n"
        help_text += "- help: Show this help message\n"
        help_text += "- troubleshoot: Start interactive troubleshooting\n"
        help_text += "- exit: Exit the application\n\n"
        
        workflows = self.workflow_manager.get_available_workflows()
        if workflows:
            help_text += "Available Workflows:\n"
            for w in workflows:
                help_text += f"- {w['name']}: {w['description']}\n"
                
            # Show example commands
            help_text += "\nExample Commands:\n"
            for workflow in self.workflow_manager.workflows.values():
                for example in workflow.get_example_commands():
                    help_text += f"- {example}\n"
                    
        return help_text