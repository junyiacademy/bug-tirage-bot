"""
Bug Triage API Routes
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.services.bug_triage_service import BugTriageService
from src.services.gcp_error_service import GCPErrorService
from src.core.models import SlackPayload, BugTriageRequest, BugTriageResponse

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/bug-triage", tags=["bug-triage"])

# Initialize services
bug_triage_service = BugTriageService()
gcp_error_service = GCPErrorService()


def run_process_bug_analysis(
    error_message: str,
    slack_payload: SlackPayload,
    analysis_id: str,
    custom_prompt: Optional[str] = None
):
    """Synchronized wrapper function, internally uses asyncio.run to execute async function"""
    asyncio.run(
        bug_triage_service.process_bug_analysis(
            error_message,
            slack_payload,
            analysis_id,
            custom_prompt
        )
    )


@router.post("/analyze", response_model=BugTriageResponse)
async def analyze_bug(
    request: BugTriageRequest,
    background_tasks: BackgroundTasks
):
    """
    input payload:
    - error_reporting_group_id: string (optional)
    - error_message: string (optional)
    - slack_channel_id: string (optional)
    - slack_thread_id: string (optional)
    - use_mcp_for_slack_details: boolean (optional)
    - dry_run: boolean (optional)
    - custom_prompt: string (optional) - 自訂的 prompt，會附加到預設的分析 prompt 中
    """
    try:
        # Generate unique analysis ID
        analysis_id = f"triage-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
        logger.info(f"Received bug analysis request: {analysis_id}")
        logger.info(f"Request payload: {request.dict()}")

        # Determine error message source
        if request.error_reporting_group_id:
            error_message = gcp_error_service.get_gcp_error_events_message(request.error_reporting_group_id)
            if not error_message:
                logger.error(f"無法取得 group_id {request.error_reporting_group_id} 的錯誤訊息")
                raise HTTPException(status_code=400, detail="無法取得指定 group_id 的錯誤訊息")
            detail = f"即將分析 error_reporting_group_id: {request.error_reporting_group_id} (對應的錯誤訊息：{error_message})，並將結果送到 slack channel: {request.slack_channel_id}"
        elif request.error_message:
            error_message = request.error_message
            detail = f"即將分析 error_message: {error_message}，並將結果送到 slack channel: {request.slack_channel_id}"
        else:
            raise HTTPException(status_code=400, detail="請提供 error_reporting_group_id 或 error_message")


        if request.dry_run:
            logger.info(f"Dry run request: {request.dict()}")
            return BugTriageResponse(
                status="accepted",
                message="分析中，結果將自動回覆至 Slack (dry run)",
                detail=detail,
                analysis_id=analysis_id,
                estimated_completion="5-10 minutes"
            )

        # Create Slack payload
        slack_payload = SlackPayload(
            channel_id=request.slack_channel_id,
            thread_id=request.slack_thread_id,
            read_slack_thread_details=request.use_mcp_for_slack_details
        )

        # Add background task
        background_tasks.add_task(
            run_process_bug_analysis,
            error_message,
            slack_payload,
            analysis_id,
            request.custom_prompt
        )

        return BugTriageResponse(
            status="accepted",
            message="分析中，結果將自動回覆至 Slack",
            detail=detail,
            analysis_id=analysis_id,
            estimated_completion="5-10 minutes"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process bug analysis request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
