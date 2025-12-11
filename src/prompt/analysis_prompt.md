- 請針對 /external_codebase，按以下格式提供分析結果（使用繁體中文，JSON 格式），然後不要有任何除了 JSON 外的解釋或其他內容
- 分析結果請使用 Slack markdown 語法
  - 超連結必須使用 Slack 格式：`[anchor text](URL)`
  - 列表項目使用 `-` 開頭
  - 順序項目使用 `1. ` or `2. ` ...方式開頭，並適當縮排
  - 短的程式碼或專有名詞使用反引號，例如：`exercise_util.py:223-242`
  - 長段程式碼使用三個反引號包圍 ``` codebase.... ```

```json
{
  "root_cause_analysis": "基於錯誤訊息和堆疊追蹤的詳細根本root cause，包含技術細節和可能的觸發條件",
  "root_cause_file_codebase": "相關的檔案/函數名稱/程式碼行數等具體位置資訊（列出檔案路徑時，不要包含 /external_codebase 前綴）",
  "database_status":"如果問題描述中有提供具體的帳號資訊時（例如：帳號 id 或是使用紀錄），請透過 Datastore REST API 查詢該帳號的相關資料來協助 debug（具體方式請參考 prompt/database_prompt），然後把查到的資訊回傳在這裡（如果沒有請回傳 None)",
  "suspect_commit": "請用 git blame 查看至少近一個月以內的 code change 確認是否有可疑的 commit hash（請確保有 60% 以上信心程度再回傳該 commit），否則回傳 'None'",
  "suspect_commit_author": "可疑提交的作者或 'None'",
  "recommended_person": "除嫌疑作者外，請根據 git blame & commit 紀錄找出對該模組最熟悉另 1 位開發人員，請避免跟 suspect_commit_author 是同一個人",
  "recommended_reason": "推薦該人員的具體理由（如：模組主要維護者、相關功能開發者）",
  "suggestion": "具體的修復步驟、研究方向或後續行動計劃"
}
```
注意事項：
- 分析應基於實際證據，避免主觀推測
- 建議應具體可執行，包含驗證步驟