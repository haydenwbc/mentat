from typing import Dict, Tuple, Any, Optional
from .backend import LLMConfig

class CommandParser:
    """Parses natural language commands into workflow actions."""
    
    def __init__(self, llm_backend: LLMConfig):
        self.llm = llm_backend

    def parse_command(self, command: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Parse a natural language command into workflow components.
        
        Args:
            command: Natural language command from user
            
        Returns:
            Tuple of (workflow_name, command_name, parameters)
            
        Example:
            "Post a tweet saying 'Hello World'" ->
            ("twitter", "post", {"content": "Hello World"})
        """
        command = command.lower().strip()
        
        # Basic command parsing (will be enhanced with LLM later)
        if "tweet" in command or "twitter" in command or "mention" in command:
            workflow = "twitter"
            
            # Handle mentions - adding more variations of the command
            if any(phrase in command for phrase in ["check mention", "recent mention", "show mention", "view mention", "get mention"]):
                return workflow, "mentions", {}
                
            # Handle replies
            if "reply" in command or "respond" in command:
                # Check for specific mention ID
                mention_id = None
                if "to mention" in command and "id" in command:
                    try:
                        mention_id = command.split("id")[-1].strip()
                    except:
                        pass
                return workflow, "reply", {"mention_id": mention_id}
                
            # Handle regular tweets
            if "post" in command or "send" in command or "tweet" in command:
                # Extract content between quotes if present
                content = self._extract_content(command)
                return workflow, "post", {"content": content}
                
        raise ValueError("Command not recognized. Please try again.")
    
    def _extract_content(self, command: str) -> str:
        """Extract content from command string."""
        # Try to find content between quotes
        for quote in ["'", '"']:
            if quote in command:
                parts = command.split(quote)
                if len(parts) >= 3:
                    return parts[1]
        
        # If no quotes, try to extract content after common phrases
        for phrase in ["saying", "tweet", "post", "with content", "with text"]:
            if phrase in command:
                content = command.split(phrase)[1].strip()
                if content:
                    return content
        
        raise ValueError("Could not extract content from command. Please use quotes around your message.")

    def get_command_help(self) -> str:
        """Get help text for command formatting."""
        return """
Available Commands:
------------------
1. Post a Tweet:
   - "Post a tweet saying 'your message here'"
   - "Tweet 'your message here'"
   - "Send tweet 'your message here'"

Tips:
- Use quotes (single or double) around your message
- Be specific about the action you want to take
"""