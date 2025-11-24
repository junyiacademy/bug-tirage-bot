"""
Git Utilities
"""

import os
import subprocess
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class GitUtils:
    """Utility class for Git operations"""
    
    def __init__(self, codebase_dir: str = None):
        if codebase_dir is None:
            # 從專案根目錄找到 external_codebase
            project_root = Path(__file__).parent.parent.parent
            self.codebase_dir = str(project_root / "external_codebase")
        else:
            self.codebase_dir = codebase_dir
    
    def clone_or_update_repository(self, token: str, github_project: str) -> bool:
        """Clone or update GitHub repository"""
        try:
            repo_url = f"https://oauth2:{token}@github.com/{github_project}"
            
            is_cloned = os.path.isdir(self.codebase_dir)
            
            if not is_cloned:
                # Clone repository
                command = ['git', 'clone', '--single-branch', '--branch', 'master', repo_url, self.codebase_dir]
                logger.info(f"Cloning repository: {github_project}")
                subprocess.run(command, capture_output=True, text=True, check=True)
                logger.info(f"Repository cloned to: {self.codebase_dir}")
            else:
                # Update repository
                logger.info("Updating existing repository")
                subprocess.run(['git', 'pull', 'origin' ,'master'], cwd=self.codebase_dir, check=True)
                logger.info("Repository updated successfully")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Repository operation failed: {e}")
            return False
