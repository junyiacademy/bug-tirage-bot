## 步驟 1:定義 slack thread id 和 channel id
Slack Channel ID: {slack_channel_id}
Slack Thread ID: {slack_thread_id}

## 步驟 2: 輸出問題摘要
- 請先使用 MCP mcp__slack__slack_get_thread_replies 工具讀取 channel_id 和 thread_id 完整對話內容，獲取上下文、圖片
- 如果有遇到 github 連結，請使用 mcp__github__search_issues 或 mcp__github__get_issue 獲取 github issue 細節

最後請產出以下 JSON 格式摘要，不要有任何除了 JSON 外的解釋或其他內容

```json
{
  "issue_summary": {
    "title": "問題簡短標題",
    "severity": "Critical/High/Medium/Low",
    "reported_date": "YYYY-MM-DD",
    "reporter": "回報者名稱/角色",
  },
  
  "problem_description": {
    "user_impact": "使用者遇到的具體問題（使用者視角）",
    "affected_users": ["受影響的帳號/範圍"],
    "affected_features": ["受影響的功能模組"],
    "reproduction_status": "Yes/No/Partial - 說明"
  },
  
  "technical_observations": {
    "error_messages": ["錯誤訊息1", "錯誤訊息2"],
    "missing_data": ["缺失的資料記錄"],
    "abnormal_behaviors": ["異常行為描述"],
    "screenshots_summary": [
      {
        "image_name": "IMG_4171",
        "content_type": "UI截圖/Console錯誤/後台查詢/Network請求",
        "key_findings": ["截圖中的關鍵資訊"]
      }
    ]
  },
  
  "investigation_findings": {
    "tested_by": "測試人員",
    "test_results": "測試結果摘要",
    "reproducible_conditions": "可重現的條件",
    "non_reproducible_conditions": "無法重現的條件",
    "suspected_factors": ["懷疑的影響因素"]
  },
  
  "discussion_highlights": [
    {
      "author": "發言者",
      "timestamp": "時間",
      "key_point": "關鍵發現或建議"
    }
  ],
  
  "pending_information": [
    "待確認的資訊1：為何需要",
    "待確認的資訊2：為何需要"
  ],
  
  "related_links": {
    "github_issue": "Issue URL",
    "slack_thread": "Slack 連結",
    "customer_ticket": "客服單連結"
  }
}
```