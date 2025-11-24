"""
GCP Error Reporting Service
"""

import json
import requests
import os
from src.core.config import Config

from google.oauth2 import service_account
from google.auth.transport.requests import Request



class GCPErrorService:
    """Service for handling GCP Error Reporting operations"""
    
    def __init__(self):
        self.config = Config()
        self.project_id = self.config.GCP_PROJECT_ID
        self.client_email = self.config.GCP_SERVICE_ACCOUNT_EMAIL
        self.private_key = self.config.GCP_SERVICE_ACCOUNT_PRIVATE_KEY
        self.base_url = "https://clouderrorreporting.googleapis.com/v1beta1"
        # 啟動時自動產生帶 token 的 database_prompt runtime 檔
        try:
            token = self.get_access_token()
            self._generate_database_prompt_runtime(token)
        except Exception as _:
            # 避免初始化失敗影響主要功能，忽略錯誤（可視需要加上 logging）
            pass

    def _generate_database_prompt_runtime(self, token: str):
        """Generate database prompt runtime file"""
        prompt_file = f"src/prompt/database_prompt.md"
        with open(prompt_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        replaced_content = original_content.replace("$(gcp access token)", token)
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(replaced_content)
            
    def get_access_token(self) -> str:
        """Get access token for GCP API"""
        scopes = ['https://www.googleapis.com/auth/cloud-platform']
        
        if self.private_key and self.client_email:
            credentials_info = {
                "type": "service_account",
                "project_id": self.project_id,
                "private_key": self.private_key.replace('\\n', '\n'),
                "client_email": self.client_email,
                "token_uri": "https://oauth2.googleapis.com/token"
            }
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info, scopes=scopes)
        
        credentials.refresh(Request())
        return credentials.token

    def get_first_error_message(self, data: dict) -> str:
        """Extract first error message from error events data"""
        error_events = data.get('errorEvents', [])
        if not error_events:
            return None
        return error_events[0].get('message', '')

    def get_gcp_error_events_message(self, group_id: str) -> str:
        """Get error message from GCP Error Reporting for given group ID"""
        try:
            access_token = self.get_access_token()
            url = f"{self.base_url}/projects/{self.project_id}/events?groupId={group_id}"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return self.get_first_error_message(data)
            
        except Exception as e:
            print(f"Error fetching GCP error events: {e}")
            return None
