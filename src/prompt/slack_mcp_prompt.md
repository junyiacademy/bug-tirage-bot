## 步驟 1:定義 slack thread id 和 channel id
Slack Channel ID: {slack_channel_id}
Slack Thread ID: {slack_thread_id}

## 步驟 2: 解析訊息並傳送
把 analysis_result:{analysis_result} 解析如下訊息，並且使用 mcp__slack__slack_reply_to_thread 將產出的訊息reply 到的 thread id 當中（如果沒有 Slack Thread ID 可以直接發到 Slack Channel

========================

[目前實驗中，僅供參考]
（以下是來自 Claude Code 的 bug 分析和 Triage 參考建議）

▌問題分析
<analysis_result.root_cause_analysis>

▌codebase
<analysis_result.root_cause_file_codebase>

▌database
<analysis_result.database_status>

▌處理建議
<analysis_result.suggestion>

▌建議排查順序
順位1. tag analysis_result.suspect_commit_author （if 如果有 analysis_result.suspect_commit_author，沒有則直接下個順位）

（建議原因：系統判斷可能為 suspect commit <github_repo_url>/commit/<analysis_result.suspect_commit> 的作者 ） 

順位2. tag analysis_result.recommended_person
（建議原因：系統判斷對該 module 熟悉的人，<analysis_result.recommended_reason>）



========================

- 如果有 suspect_commit_author 或 recommended_person 且<GITHUB_SLACK_USER_MAPPING> 不會空 ，可以根據 <GITHUB_SLACK_USER_MAPPING> 內容去找到 slack_username 來去 tag（但如果找不到，表示該員已經離職，不要 tag 也不要顯示）
- 如果 <FEEDBACK_URL> 不是空的請在最後一段加上 「=> 歡迎填寫<FEEDBACK_URL> 回饋此次 AI 分析結果」
- 如何產生 {slack_link}
  - Slack 連結格式如下：https://junyiacademy.slack.com/archives/{slack_channel_id}/p{ts_no_dot}?thread_ts={slack_thread_id}
  - 其中：ts_no_dot = 將 slack_thread_id 的小數點移除(例如：1763059193.030299 → 1763059193030299)