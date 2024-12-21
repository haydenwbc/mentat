# Mentat

Mentat is an open-source, fully extensible interface for configuration and deployment of agentic workflows. It provides a streamlined way to set up and manage AI-powered automation tasks.

## Features

- Automated environment setup and dependency management
- Integration with OpenAI's API
- Git/GitHub integration capabilities
- Environment variable management
- Virtual environment handling

## Prerequisites

- Python 3.12 or higher
- Poetry (package manager) - auto-installed if missing

## Quick Start

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
