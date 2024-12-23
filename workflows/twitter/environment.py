import os
import tweepy
from typing import Dict, List, Tuple, Optional, Any
from core.environment import Environment
from core.backend import LLMConfig

class TwitterEnvironment:
    """Manages Twitter workflow environment variables."""
    
    REQUIRED_VARS = {
        'TWITTER_API_KEY': 'Twitter API Key (Consumer Key)',
        'TWITTER_API_SECRET': 'Twitter API Secret (Consumer Secret)',
        'TWITTER_ACCESS_TOKEN': 'Twitter Access Token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'Twitter Access Token Secret'
    }
    
    OAUTH_SETUP_STEPS = [
        {
            "title": "Access Developer Portal",
            "instructions": "1. Go to https://developer.twitter.com/portal/projects",
            "verification": "Are you on the developer portal? (Y/n): "
        },
        {
            "title": "Configure OAuth Settings",
            "instructions": """1. Select your app
2. Go to 'Settings' > 'User authentication settings'
3. Enable 'OAuth 1.0a'
4. Set App permissions to 'Read and Write'
5. Save changes""",
            "verification": "Have you updated the OAuth settings? (Y/n): "
        },
        {
            "title": "Generate Tokens",
            "instructions": """1. Go to 'Keys and tokens' tab
2. Generate new access tokens if needed
3. Copy your tokens""",
            "verification": "Do you have your tokens ready? (Y/n): "
        }
    ]
    
    def __init__(self):
        self.env = Environment()
        self.llm = LLMConfig()
    
    def _create_client(self, credentials: Dict[str, str]) -> Optional[tweepy.Client]:
        """Create and verify a Twitter client with given credentials."""
        try:
            client = tweepy.Client(**credentials)
            # Test basic authentication
            client.get_me()
            return client
        except Exception:
            return None

    def _handle_credentials(self, var_name: str, description: str) -> bool:
        """Handle credential input and validation."""
        current = self.env.get_env_var(var_name)
        updated = False
        
        while True:
            prompt = f"\n{description}"
            if current:
                prompt += f" [current: {current[:4]}...]"
            prompt += ": "
            
            value = input(prompt).strip()
            
            if value:
                self.env.set_env_var(var_name, value)
                updated = True
                break
            elif current:
                break
            else:
                print(f"{description} cannot be empty. Please try again.")
        
        return updated

    def _verify_permissions(self, client: tweepy.Client, test_write: bool = True) -> bool:
        """Verify API permissions with optional write test."""
        try:
            me = client.get_me()
            if not me.data:
                return False
                
            if not test_write:
                return True
                
            test_tweet = client.create_tweet(text="Testing write permissions...")
            if test_tweet.data:
                client.delete_tweet(test_tweet.data['id'])
                return True
                
        except Exception:
            return False
        
        return False

    def configure(self) -> bool:
        """Configure Twitter credentials with LLM assistance if available."""
        if self.llm.is_configured():
            return self._configure_with_llm()
        return self._configure_standard()

    def _configure_with_llm(self) -> bool:
        """LLM-assisted configuration process."""
        self.llm.start_conversation("twitter_setup", {
            'status': self._get_credential_status(),
            'oauth_steps': self.OAUTH_SETUP_STEPS
        })
        
        updated = False
        for var_name, description in self.REQUIRED_VARS.items():
            help_text = self.llm.get_completion(f"Guide user for {description}")
            if help_text:
                print(f"\n{help_text}")
            if self._handle_credentials(var_name, description):
                updated = True
        
        return updated and self.verify_credentials()

    def _configure_standard(self) -> bool:
        """Standard configuration process without LLM."""
        print("\nConfiguring Twitter credentials:")
        for step in self.OAUTH_SETUP_STEPS:
            print(f"\n{step['title']}")
            print(step['instructions'])
            if input(step['verification']).lower().strip() != 'y':
                return False
        
        updated = False
        for var_name, description in self.REQUIRED_VARS.items():
            if self._handle_credentials(var_name, description):
                updated = True
        
        return updated and self.verify_credentials()

    def verify_credentials(self) -> bool:
        """Verify Twitter API credentials and permissions."""
        credentials = self.get_credentials()
        client = self._create_client(credentials)
        
        if not client:
            print("\nFailed to authenticate with Twitter.")
            return False
        
        print("✓ Basic authentication successful")
        
        if self._verify_permissions(client):
            print("✓ Write permissions verified")
            return True
            
        print("\nWrite permissions test failed.")
        print("Would you like to fix OAuth settings? (Y/n)")
        if input().lower().strip() != 'n':
            return self._fix_write_permissions()
            
        return False

    # Keep essential methods
    def get_credentials(self) -> Dict[str, Optional[str]]:
        """Get Twitter API credentials with status logging."""
        credentials = {
            'api_key': self.env.get_env_var('TWITTER_API_KEY'),
            'api_secret': self.env.get_env_var('TWITTER_API_SECRET'),
            'access_token': self.env.get_env_var('TWITTER_ACCESS_TOKEN'),
            'access_secret': self.env.get_env_var('TWITTER_ACCESS_TOKEN_SECRET')
        }
        
        print("\nCredential status:")
        for key, value in credentials.items():
            print(f"- {key}: {'✓ Present' if value else '✗ Missing'}")
            
        return credentials

    def get_credential_status(self) -> Dict[str, Any]:
        """Get current status of credential configuration."""
        status = {
            'complete': True,
            'missing': [],
            'configured': []
        }
        
        for var in self.REQUIRED_VARS:
            value = self.env.get_env_var(var)
            if not value:
                status['missing'].append(var)
                status['complete'] = False
            else:
                status['configured'].append(var)
                
        return status

    def check_configuration_exists(self) -> bool:
        """Quick check if configuration exists."""
        return all(bool(self.env.get_env_var(var)) for var in self.REQUIRED_VARS)

    def fix_configuration(self) -> bool:
        """Fix configuration issues."""
        credentials = self.get_credentials()
        client = self._create_client(credentials)
        
        if not client:
            print("\nCredentials are invalid. Let's reconfigure.")
            return self.configure()
            
        if not self._verify_permissions(client):
            print("\nWrite permissions need to be configured.")
            return self._fix_write_permissions()
            
        return True

    def _fix_write_permissions(self) -> bool:
        """Guide through fixing write permissions."""
        oauth_step = next(step for step in self.OAUTH_SETUP_STEPS 
                         if step["title"] == "Configure OAuth Settings")
        print(f"\n{oauth_step['instructions']}")
        
        if input("Would you like to generate new access tokens? (y/N): ").lower().strip() == 'y':
            return self._configure_standard()
            
        return self.verify_credentials()