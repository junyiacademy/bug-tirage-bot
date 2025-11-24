"""
Configuration Management
"""

import os
from typing import Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application Configuration"""
    
    # API Configuration
    PORT: int = int(os.getenv("PORT", 8080))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    # Logging Configuration
    PROJECT: str = os.getenv("PROJECT", "DEV")
    CODEBASE_DIR: str = str(Path(__file__).parent.parent.parent / "external_codebase")

    # GitHub Configuration
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_PROJECT: str = os.getenv("GITHUB_PROJECT", "")
    # GitHub <-> Slack User Name Mapping Configuration
    GITHUB_SLACK_USER_MAPPING: str = os.getenv("GITHUB_SLACK_USER_MAPPING", "")
    # Slack Configuration
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_TEAM_ID: str = os.getenv("SLACK_TEAM_ID", "")

    # GCP Configuration
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    GCP_SERVICE_ACCOUNT_EMAIL: str = os.getenv("GCP_SERVICE_ACCOUNT_EMAIL", "")
    GCP_SERVICE_ACCOUNT_PRIVATE_KEY: str = os.getenv("GCP_SERVICE_ACCOUNT_PRIVATE_KEY", "")
    
    # Claude Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    @classmethod
    def validate_required_vars(cls) -> List[str]:
        """Validate required environment variables"""
        required_vars = [
            'GITHUB_TOKEN', 'GITHUB_PROJECT', 
            'SLACK_BOT_TOKEN', 'SLACK_TEAM_ID'
        ]
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        return missing_vars
