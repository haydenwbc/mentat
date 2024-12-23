from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class Workflow(ABC):
    """Base class for all workflows."""
    
    def __init__(self):
        self.name = self.__class__.__name__.lower().replace('workflow', '')
        self.description = "Base workflow class"
        self.commands = {}
        self.register_commands()

    @abstractmethod
    def register_commands(self) -> None:
        """Register the commands this workflow supports."""
        pass

    @abstractmethod
    def validate_environment(self) -> bool:
        """Validate that all required environment variables are set."""
        pass
        
    def get_commands(self) -> Dict[str, str]:
        """Get the list of supported commands and their descriptions."""
        return self.commands

    def get_name(self) -> str:
        """Get the workflow name."""
        return self.name

    def get_description(self) -> str:
        """Get the workflow description."""
        return self.description
    
    @abstractmethod
    def get_example_commands(self) -> List[str]:
        """Get list of example commands for this workflow."""
        pass

    @abstractmethod
    def execute_command(self, command: str, **kwargs) -> Any:
        """Execute a workflow command."""
        pass


class WorkflowManager:
    """Manages workflow registration and execution."""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}

    def register_workflow(self, workflow: Workflow) -> None:
        """Register a new workflow."""
        name = workflow.get_name()
        if name in self.workflows:
            raise ValueError(f"Workflow '{name}' is already registered")
        self.workflows[name] = workflow

    def get_workflow(self, name: str) -> Optional[Workflow]:
        """Get a workflow by name."""
        return self.workflows.get(name)

    def get_available_workflows(self) -> List[Dict[str, str]]:
        """Get list of available workflows and their descriptions."""
        return [
            {"name": w.get_name(), "description": w.get_description()}
            for w in self.workflows.values()
        ]

    def execute_workflow_command(self, workflow_name: str, command: str, **kwargs) -> Any:
        """Execute a command on a specific workflow."""
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        if not workflow.validate_environment():
            raise EnvironmentError(f"Environment not properly configured for workflow '{workflow_name}'")
            
        return workflow.execute_command(command, **kwargs)