"""
Application Configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Development Settings
# DEBUG_MODE can be set via environment variable DEBUG_MODE (true/false)
# Defaults to False if not set
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() in ('true', '1', 'yes')

# When DEBUG_MODE is True, chat responses will be simulated without calling the LLM API
# Set to False for production use with real AI responses
