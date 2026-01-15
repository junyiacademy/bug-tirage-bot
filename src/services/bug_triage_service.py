"""
Bug Triage Service
Handles bug analysis using Claude Code
"""

import logging
import os
from typing import Optional

from src.core.config import Config
from src.core.models import SlackPayload
from src.core.exceptions import ConfigurationError, GitOperationError, ClaudeAnalysisError, SlackNotificationError
from src.utils.git_utils import GitUtils
from src.utils.claude_utils import ClaudeUtils
from .slack_service import SlackService
from .gcp_error_service import GCPErrorService

logger = logging.getLogger(__name__)


class BugTriageService:
    """Main service for bug triage operations"""
    
    def __init__(self):
        self.config = Config()
        self.git_utils = GitUtils(self.config.CODEBASE_DIR)
        self.claude_utils = ClaudeUtils(self.config.CODEBASE_DIR)
        self.slack_service = SlackService()
        self.gcp_error_service = GCPErrorService()
        self._init_environment()
    
    def _init_environment(self):
        """Initialize environment and validate configuration"""
        try:
            missing_vars = self.config.validate_required_vars()
            if missing_vars:
                raise ConfigurationError(f"Missing required environment variables: {missing_vars}")
            
            logger.info("Environment variables validated successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize environment: {e}")
            raise
    
    def clone_or_update_repository(self) -> bool:
        """Clone or update GitHub repository and checkout to deployed commit"""
        try:
            # Step 1: Clone/update repository
            clone_success = self.git_utils.clone_or_update_repository(
                self.config.GITHUB_TOKEN, 
                self.config.GITHUB_PROJECT
            )
            if not clone_success:
                return False
            
            # Step 2: Checkout to latest deployed commit to exclude undeployed commits
            checkout_success = self.git_utils.checkout_to_deployed_commit()
            if not checkout_success:
                logger.warning("Failed to checkout to deployed commit, proceeding with master HEAD")
            
            return True
        except Exception as e:
            logger.error(f"Repository operation failed: {e}")
            raise GitOperationError(f"Failed to clone/update repository: {e}")
    
    async def analyze_bug(self, error_message: str, analysis_id: str, slack_payload: SlackPayload, custom_prompt: Optional[str] = None) -> str:
        """Analyze bug using Claude Code"""
        try:
            logger.info(f"Starting Claude Code analysis for analysis_id: {analysis_id}")

            result = self.claude_utils.analyze_bug(error_message, slack_payload, custom_prompt)
            if not result:
                raise ClaudeAnalysisError("Claude analysis returned no result")
            
            return result
                
        except Exception as e:
            logger.error(f"Analysis failed for {analysis_id}: {e}")
            raise ClaudeAnalysisError(f"Bug analysis failed: {e}")
    
    async def send_to_slack(self, analysis_id: str, analysis_result: str, slack_payload: SlackPayload):
        """Send analysis result to Slack"""
        try:
            channel_id = slack_payload.channel_id
            if not channel_id:
                raise SlackNotificationError("No Slack channel ID provided")
            
            await self.slack_service.send_analysis_result(
                analysis_id,
                analysis_result, 
                channel_id, 
                slack_payload.thread_id
            )
                
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            raise SlackNotificationError(f"Failed to send to Slack: {e}")
    
    async def process_bug_analysis(
        self, 
        error_message: str, 
        slack_payload: SlackPayload,
        analysis_id: str,
        custom_prompt: Optional[str] = None
    ):
        """Main process for bug analysis workflow"""
        try:
            logger.info(f"Starting bug analysis workflow for analysis_id: {analysis_id}")
            
            # Step 1: Clone or update repository
            if not self.clone_or_update_repository():
                raise GitOperationError("Failed to prepare codebase")
            
            # Step 2: Analyze bug
            analysis_result = await self.analyze_bug(error_message, analysis_id, slack_payload, custom_prompt)
            
            # Step 3: Send to Slack
            if not analysis_result:
                raise ClaudeAnalysisError("Claude analysis returned no result")

            await self.send_to_slack(analysis_id, analysis_result, slack_payload)
            
            logger.info(f"Bug analysis workflow completed for analysis_id: {analysis_id}")
            
        except Exception as e:
            logger.error(f"Bug analysis workflow failed: {e}")
            raise
