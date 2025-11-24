"""
Slack Service
"""
import os
import asyncio
import subprocess
import logging
import tempfile
from typing import Optional
from dotenv import load_dotenv

from src.core.config import Config
from src.utils.cmd_utils import run_with_live_output

logger = logging.getLogger(__name__)


class SlackService:
    """Service for handling Slack operations"""
    
    def __init__(self):
        self.config = Config()
        self.check_mcp_server_status()

    
    def check_mcp_server_status(self):
        """Setup Slack MCP server"""
        cmd = [
            'claude', 'mcp', 'get', 'slack'
        ]
        result = run_with_live_output(cmd)
        output = result[0] if isinstance(result, (list, tuple)) and len(result) > 0 else ""
        if "Status: ✓ Connected" in output:
            logger.info("✅ MCP Slack server 已連線")
        else:
            logger.error(f"❌ MCP Slack server 尚未連線，請檢查設定 ${result}")

    
    async def send_analysis_result(self, analysis_id: str, analysis_result: str, slack_channel_id: str, slack_thread_id: Optional[str] = None):
        """Send analysis result to Slack"""
        try:
            slack_channel_id = slack_channel_id
            prompt_file = f"src/prompt/slack_mcp_prompt.md"
            prompt = f"""
            Slack Channel ID: {slack_channel_id}
            Slack Thread ID: {slack_thread_id}
            analysis_result:{analysis_result}
            FEEDBACK_URL: {self.config.FEEDBACK_URL}
            GITHUB_SLACK_USER_MAPPING: {self.config.GITHUB_SLACK_USER_MAPPING}
            github_repo_url: https://github.com/{self.config.GITHUB_PROJECT}
            請閱讀 {prompt_file} 並根據指示執行 prompt
            """

            logger.info(f"======prompt start(Claude Code)=================")
            logger.info(f"{prompt}")
            logger.info(f"======prompt end(Claude Code)==================")
            # Avoid :[Errno 7] Argument list too long: 'claude'
            # os.makedirs("log", exist_ok=True)
            # prompt_file = f"log/slack_prompt_{analysis_id}.txt"
            # with open(prompt_file, 'w', encoding='utf-8') as f:
            #     f.write(prompt)
            # logger.info(f"save prompt to temp file: {prompt_file}")    

            cmd = ['claude', '-p', prompt]
            # Run analysis asynchronously
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            # 儲存 stdout 和 stderr 訊息
            stdout = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""
            logger.info(f"--- STDOUT ---")
            logger.info(f"{stdout}")
            logger.info(f"--- STDERR ---")
            logger.error(f"{stderr}")
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")