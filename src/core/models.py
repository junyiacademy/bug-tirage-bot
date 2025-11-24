"""
Data Models for Bug Triage Service
"""

from typing import Optional
from pydantic import BaseModel


class SlackPayload(BaseModel):
    """Slack configuration payload"""
    channel_id: Optional[str] = None
    thread_id: Optional[str] = None
    read_slack_thread_details: Optional[bool] = False


class BugTriageRequest(BaseModel):
    """Bug Triage Analysis Request Model"""
    error_reporting_group_id: Optional[str] = None
    error_message: Optional[str] = None
    slack_channel_id: Optional[str] = None
    slack_thread_id: Optional[str] = None
    use_mcp_for_slack_details: Optional[bool] = False
    dry_run: Optional[bool] = False
    custom_prompt: Optional[str] = None


class BugTriageResponse(BaseModel):
    """Bug Triage Analysis Response Model"""
    status: str
    message: str
    analysis_id: str
    estimated_completion: str
    detail: Optional[str] = None
