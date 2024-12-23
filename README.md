# Mentat

Mentat is an AI-powered command-line assistant for automating social media management and other workflows through natural language commands.

## Features

- Natural language command processing
- Modular workflow system
- Multiple LLM backend support (OpenAI GPT-4, Anthropic Claude)
- Twitter integration with full API v2 support
- Interactive configuration and setup

## Supported Workflows

### Twitter
- Post tweets using natural language commands
- OAuth 1.0a authentication with read/write permissions
- Automatic credential validation and testing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mentat
```

2. Run the bootstrap script:
```bash
python run.py
```

The bootstrap process will:
- Install Poetry if not present
- Create necessary environment files
- Set up a virtual environment
- Install required dependencies

## Configuration

Create a `.env` file in the project root (automatically created during bootstrap) with:

```properties
OPENAI_API_KEY=your_api_key_here
GIT_USERNAME=your_github_username
GIT_TOKEN=your_github_token
```

## Project Structure

- `run.py`: Main entry point and bootstrap script
- `pyproject.toml`: Project dependencies and metadata
- `.env`: Environment configuration

## Development Status

This project is currently in early development. Core functionality is being implemented.
