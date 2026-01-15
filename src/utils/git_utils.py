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

    def get_latest_deployed_commit(self) -> Optional[str]:
        """Get the latest deployed commit hash using prod- tags"""
        try:
            # 查找最新的 prod- 開頭的 tag
            result = subprocess.run(
                ['git', 'tag', '--sort=-creatordate', '--list', 'prod-*'],
                cwd=self.codebase_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            tags = result.stdout.strip().split('\n') if result.stdout.strip() else []
            if not tags or not tags[0]:
                logger.warning("No prod- tags found, will analyze all commits")
                return None
            
            latest_prod_tag = tags[0]
            logger.info(f"Found latest production tag: {latest_prod_tag}")
            
            # 取得該 tag 對應的 commit hash
            tag_result = subprocess.run(
                ['git', 'rev-list', '-n', '1', latest_prod_tag],
                cwd=self.codebase_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_hash = tag_result.stdout.strip()
            logger.info(f"Latest deployed commit: {commit_hash}")
            return commit_hash
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get latest deployed commit: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get latest deployed commit: {e}")
            return None

    def checkout_to_deployed_commit(self, commit_hash: Optional[str] = None) -> bool:
        """Checkout to the latest deployed commit to exclude undeployed commits from analysis"""
        try:
            if not commit_hash:
                commit_hash = self.get_latest_deployed_commit()
                
            if not commit_hash:
                logger.warning("No deployed commit found, staying on master HEAD (may include undeployed commits)")
                return True
            
            # 先確保在正確的分支
            subprocess.run(
                ['git', 'checkout', 'master'],
                cwd=self.codebase_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            # 切換到特定的 deployed commit
            subprocess.run(
                ['git', 'checkout', commit_hash],
                cwd=self.codebase_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Checked out to deployed commit: {commit_hash} (excluding undeployed commits from analysis)")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to checkout to deployed commit: {e}")
            return False
        except Exception as e:
            logger.error(f"Checkout operation failed: {e}")
            return False
