#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bug Triage Bot - Main Application Entry Point
"""
import sys 
import json
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import Config
from src.api.bug_triage_routes import router as bug_triage_router

# Initialize configuration
config = Config()

# Configure structured logging for GKE
class GKEFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if config.PROJECT == "DEV":
            log_entry = f"{self.formatTime(record)} - {record.getMessage()}"
            return log_entry
        else:
            return json.dumps(log_entry)

# Configure logging for GKE environment
def setup_logging():
    # 清除現有的 handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 設定日誌級別
    root_logger.setLevel(logging.INFO)
    
    # 添加 console handler 並使用 GKE formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(GKEFormatter())
    root_logger.addHandler(console_handler)
    
    # 確保所有子 logger 都使用 root logger 的配置
    logging.getLogger().propagate = True

# 初始化日誌配置
setup_logging()
logger = logging.getLogger(__name__)



# Create FastAPI app
app = FastAPI(
    title="Bug Triage API",
    description="Automated bug analysis and Slack notification system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(bug_triage_router)


@app.get("/")
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "message": "Bug Triage API is running", 
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00.000Z"
    }


if __name__ == "__main__":
    port = config.PORT
    host = config.HOST
    
    logger.info(f"Starting Bug Triage API on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info",
        reload=False
    )
