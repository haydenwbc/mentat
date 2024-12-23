import tweepy
from typing import List, Dict
from core.workflow import Workflow
from core.backend import LLMConfig
from .environment import TwitterEnvironment

class TwitterWorkflow(Workflow):
    """Handles Twitter-related actions."""
    
    def __init__(self):
        super().__init__()
        self.env = TwitterEnvironment()
        self.description = "Post and manage tweets"
        self.client = None
        # Don't initialize client in __init__, wait until needed
        
    def register_commands(self) -> None:
        """Register supported commands."""
        self.commands = {
            "post": "Post a new tweet",
            "mentions": "View recent mentions of your account",
            "reply": "Generate and post an AI response to a mention",
        }
    
    def get_example_commands(self) -> List[str]:
        """Get example commands for the Twitter workflow."""
        return [
            "Post a tweet saying 'Hello, World!'",
            "Check my recent mentions",
            "Reply to latest mention",
            "Generate response to mention"
        ]

    def validate_environment(self) -> bool:
        """Check if environment is valid without full validation."""
        return self.env.check_configuration_exists()

    def _initialize_client(self) -> bool:
        """
        Initialize Twitter API v2 client with OAuth 1.0a.
        
        Returns:
            bool: True if client initialization is successful
            
        Note:
            Handles various authentication errors and prints detailed debug info.
        """
        try:
            print("\nInitializing Twitter client...")
            credentials = self.env.get_credentials()
            
            # Check for missing credentials
            status = self.env.get_credential_status()
            if not status['complete']:
                print(f"Missing credentials: {', '.join(status['missing'])}")
                return False
                
            # Map credentials to tweepy client parameters
            self.client = tweepy.Client(
                consumer_key=credentials['api_key'],
                consumer_secret=credentials['api_secret'],
                access_token=credentials['access_token'],
                access_token_secret=credentials['access_secret']
            )
            
            # Verify client by making a test API call
            print("Testing API connection...")
            me = self.client.get_me()
            print(f"✓ Successfully authenticated as @{me.data.username}")
            return True
            
        except tweepy.errors.Unauthorized as e:
            print(f"\nAuthentication failed: {str(e)}")
            print("This usually means your API keys or tokens are invalid.")
            return False
        except Exception as e:
            print(f"\nFailed to initialize Twitter client: {str(e)}")
            import traceback
            print(f"Stack trace:\n{traceback.format_exc()}")
            return False

    def execute_command(self, command: str, **kwargs) -> str:
        """Execute a Twitter workflow command."""
        if not self.client:
            if not self._initialize_client():
                if not self.env.fix_configuration():
                    raise RuntimeError("Failed to configure Twitter access. Please try again later.")
                if not self._initialize_client():
                    raise RuntimeError("Still unable to initialize Twitter client after reconfiguration.")
                    
        if command == "post":
            return self._post_tweet(**kwargs)
        elif command == "mentions":
            return self._get_mentions()
        elif command == "reply":
            return self._handle_reply(**kwargs)
            
        raise ValueError(f"Unknown command: {command}")

    def _handle_twitter_error(self, error: Exception, context: str) -> None:
        """Centralized error handling for Twitter API operations."""
        error_msg = str(error)
        print(f"\nError during {context}: {error_msg}")
        
        if isinstance(error, tweepy.errors.Unauthorized):
            print("\nTwitter authentication failed. Let's reconfigure your credentials.")
            if self.env.configure():
                self._initialize_client()
                return True
                
        elif isinstance(error, tweepy.errors.Forbidden):
            print("\nThe app doesn't have sufficient permissions.")
            if self.env.reconfigure_oauth():
                return self._initialize_client()
                
        elif "oauth" in error_msg.lower() or "unauthorized" in error_msg.lower():
            print("\nAuthentication issue detected. Let's reconfigure Twitter.")
            if self.env.configure() and self._initialize_client():
                return True
                
        return False

    def _post_tweet(self, content: str) -> str:
        """Post a tweet with the given content using API v2."""
        try:
            response = self.client.create_tweet(text=content)
            if response.data:
                return f"Successfully posted tweet: '{content}'"
            raise RuntimeError("No response data received from Twitter")
        except Exception as e:
            if self._handle_twitter_error(e, "posting tweet"):
                return self._post_tweet(content)
            raise RuntimeError(f"Failed to post tweet: {str(e)}")

    def _get_mentions(self) -> str:
        """Fetch recent mentions of the user's account."""
        try:
            me = self.client.get_me()
            mentions = self.client.get_users_mentions(
                me.data.id,
                max_results=10,
                tweet_fields=['created_at', 'author_id', 'text']
            )
            
            if not mentions.data:
                return "No recent mentions found."
                
            result = "\nRecent mentions:\n"
            for tweet in mentions.data:
                result += f"\nID: {tweet.id}\n"
                result += f"Text: {tweet.text}\n"
                result += f"Time: {tweet.created_at}\n"
                result += "-" * 40
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch mentions: {str(e)}")

    def _handle_reply(self, mention_id: str = None) -> str:
        """Generate and post an AI response to a mention."""
        try:
            # If no mention_id provided, get the latest mention
            if not mention_id:
                me = self.client.get_me()
                mentions = self.client.get_users_mentions(
                    me.data.id,
                    max_results=1,
                    tweet_fields=['text']
                )
                if not mentions.data:
                    return "No mentions found to reply to."
                mention_id = mentions.data[0].id
                mention_text = mentions.data[0].text
            else:
                tweet = self.client.get_tweet(mention_id)
                if not tweet.data:
                    return f"Could not find tweet with ID: {mention_id}"
                mention_text = tweet.data.text

            # Generate AI response
            response = self._generate_response(mention_text)
            
            # Post the reply
            self.client.create_tweet(
                text=response,
                in_reply_to_tweet_id=mention_id
            )
            
            return f"Posted reply: '{response}'"
            
        except Exception as e:
            raise RuntimeError(f"Failed to handle reply: {str(e)}")

    def _generate_response(self, mention_text: str) -> str:
        """Generate an AI response to a mention."""
        llm = LLMConfig()
        if not llm.is_configured():
            raise RuntimeError("LLM not configured. Cannot generate response.")
            
        prompt = f"""
        Generate a friendly and professional response to this tweet:
        Tweet: {mention_text}
        
        Requirements:
        - Keep it under 280 characters
        - Be helpful and positive
        - Maintain professional tone
        - Include relevant emojis if appropriate
        - Don't include quotes in the response
        """
        
        response = llm.get_completion(prompt)
        if not response:
            raise RuntimeError("Failed to generate response")
            
        # Ensure response fits Twitter's length limit
        if len(response) > 280:
            response = response[:277] + "..."
            
        return response