# Mentat

Mentat is a workflow automation system designed to help users manage various tasks through natural language commands. The system leverages LLM (Large Language Model) configurations to provide intelligent responses and automate workflows.

## Project Stage

**Current Stage:** Development

The project is currently in the development stage. The core functionalities are being implemented and tested. Contributions and feedback are welcome to improve the system.

## Directory Structure

```
mentat/
├── core/
│   ├── backend.py          # Manages LLM backend configuration and interactions
│   ├── core.py             # Core class managing the Mentat system
│   ├── environment.py      # Manages environment variables for the Core module
│   ├── parser.py           # Parses natural language commands into workflow actions
│   └── workflow.py         # Base class for all workflows and WorkflowManager
├── workflows/
│   ├── twitter/
│   │   ├── twitter.py      # Handles Twitter-related actions
│   │   └── environment.py  # Manages Twitter workflow environment variables
├── .env                    # Environment variables file (ignored by Git)
├── .gitignore              # Git ignore file
├── .venv/                  # Virtual environment directory (ignored by Git)
├── run.py                  # Main entry point for running the application
└── README.md               # Project documentation
```

## Recent Updates

### New Features and Functionalities

1. **Interactive Troubleshooting:**
   - Added an interactive troubleshooting feature that helps users resolve issues with the system.
   - Users can type `troubleshoot` to start a troubleshooting session.

2. **Environment Variable Management:**
   - Improved handling of environment variables using the `.env` file.
   - Added methods to set, unset, and retrieve environment variables.

3. **OAuth Setup and Configuration:**
   - Streamlined the OAuth setup process for Twitter API.
   - Added LLM-assisted configuration for easier setup.

4. **Error Handling:**
   - Centralized error handling for Twitter API operations.
   - Improved feedback for missing credentials and authentication issues.

5. **Command Parsing:**
   - Enhanced command parsing to support more natural language variations.
   - Added examples and help text for better user guidance.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [Poetry](https://python-poetry.org/) for dependency management

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/haydenwbc/mentat.git
   cd mentat
   ```

2. **Set up the environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```sh
   poetry install
   ```

4. **Create and configure the `.env` file:**
   ```sh
   cp .env.example .env
   # Edit the .env file to add your API keys and configuration
   ```

### Running the Application

1. **Bootstrap the system:**
   ```sh
   python run.py
   ```

2. **Run the application:**
   ```sh
   python run.py
   ```

### Usage

- **Help:**
  Type `help` to see available commands and workflows.

- **Troubleshoot:**
  Type `troubleshoot` to start an interactive troubleshooting session.

- **Example Commands:**
  - "Post a tweet saying 'Hello, World!'"
  - "Check my recent mentions"
  - "Reply to latest mention"
  - "Generate response to mention"

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License.