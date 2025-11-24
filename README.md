# Bug Triage Bot

自動化 Bug 分析和 Slack 通知系統

Bug Triage Bot 是一套自動化的錯誤分析服務，能協助開發團隊在遇到軟體 Bug 時，快速收斂問題、解析原因、整理可執行的修復建議，並自動將分析結果即時發佈到指定的 Slack 討論串。

核心特色包括：

- 問題分析：自動下載 GitHub codebase，分析最新程式碼內容，結合錯誤訊息、堆疊追蹤和系統脈絡，協助找出 root cause。
- 脈絡讀取：可利用 Slack MCP 讀取完整的討論串內容，綜合上下文判斷，強化診斷品質。
- Bug triage：整合 git blame、commit 紀錄，找出可疑的 code change，並根據歷史紀錄自動 tag 適當的開發者協助排查，減少人工作業。
- 自動建議：產生具體可執行的修復步驟或行動清單，方便團隊即刻處理。
- 支援自訂 prompt：可依需求餵入自訂問題或進階分析指令。
- 雲端與本地皆可部署，並支援與各種自動化（如 n8n、CI pipeline、Google Error Reporting 等）串接。


```mermaid
flowchart LR
    %% 主流程
    Slack["💬 Slack "] 
        -->|"問題回報，事件觸發"| N8N["🧩 n8n (接收 Slack 事件，轉送至 Cloud Run) "]

    N8N -->|"POST "| CloudRun["☁️ Cloud Run（Bug Triage Bot）"]

    %% 將 Cloud Run 後端技術流程框起來（Slack 不放進去）
    subgraph 流程["本專案範圍（n8n要額外設定）"]
        CloudRun -->|"拉取最新程式碼"| GitHub["📦 GitHub Repo"]
        CloudRun -->|"呼叫 Claude Code "| Claude["🧠 Claude Code(錯誤分析)"]
        
        Claude -->|"回傳問題分析結果 (例如: git blame)"| CloudRun
    end

    %% Slack 與 Cloud Run 的互動放在外面
    Slack -->|" MCP 讀取 slack 討論串脈絡"| CloudRun
    CloudRun -->|"結果回傳至 Slack"| Slack
```

### （使用情境）分析 Slack 問題回報

- 可以設定當問題被回報時，可以 tag bot，並自動讀取 slack 訊息進行分析

<img src="img/demo_report_1.png" alt="demo_1" width="50%">
<img src="img/demo_report_2.png" alt="demo_2" width="50%">

### （使用情境）針對串接到 Slack 的 Error 進行自動分析

可以設定當新的 Slack Error 訊息出現後，進行自動分析

<img src="img/demo_error_report_1.png" alt="demo_1" width="50%">
<img src="img/demo_error_report_2.png" alt="demo_2" width="50%">
<img src="img/demo_error_report_3.png" alt="demo_3" width="50%">


## 📁 專案結構

```
bug-triage/
├── src/                          # 主要原始碼
│   ├── api/                      # API 相關
│   ├── core/                     # 核心功能
│   ├── services/                 # 業務邏輯服務
│   └── utils/                    # 工具函數
├── external_codebase/            # 外部程式碼庫
├── log/                          # 日誌檔案
├── main.py                       # 應用程式入口點
├── requirements.txt              # Python 依賴套件
├── Dockerfile                    # Docker 容器定義
├── docker-compose.yaml           # Docker Compose 配置
├── entrypoint.sh                 # 容器入口腳本
└── .env                          # 環境變數配置
```

# Bug Triage Bot


## Usage: local 開發

### 1.安裝

```bash
git clone git@github.com:junyiacademy/junyi-tools.git
cd junyi-tools/bug-triage
```

### 2. 環境設定
```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，填入實際的 API 金鑰和設定
vim .env
```

#### 設定 `.env`: 如何獲取各項金鑰?

```py
PROJECT=DEV # DEV or PRD
# Claude Configuration
ANTHROPIC_API_KEY=sk-ant-YOUR_CLAUDE_API_KEY_HERE

# GitHub Configuration
GITHUB_PROJECT=ORGANIZATION_NAME/REPOSITORY_NAME # eg: junyiacademy/my-project
GITHUB_TOKEN=github_pat_YOUR_GITHUB_TOKEN_HERE

# Github Slack Mapping Configuration
GITHUB_SLACK_USER_MAPPING={"github_username1": "slack_username1","github_username2": "slack_username2" }

# Slack MCP Server Configuration
SLACK_BOT_TOKEN=xoxb-YOUR_SLACK_BOT_TOKEN_HERE
SLACK_TEAM_ID=YOUR_SLACK_TEAM_ID

# GCP Configuration (optional)
GCP_PROJECT_ID=your-gcp-project-id
GCP_SERVICE_ACCOUNT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
GCP_SERVICE_ACCOUNT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT_HERE\n-----END PRIVATE KEY-----\n
```
### GitHub Configuration
**GITHUB_PROJECT**

- 將希望針對分析的 codebase repo，貼到 .env 的 `GITHUB_PROJECT`

```
#example
GITHUB_PROJECT=junyiacademy/my-project 
```
<img src="img/env_github_project.png" alt="env_github_project" width="60%">

**GitHub Token (GITHUB_TOKEN)**
- 前往 GitHub : Setting > Developer Settings > Personal access tokens > Fine > [grained personal access token](https://github.com/settings/personal-access-tokens)
- 點擊 "Generate new token"
- Token 名稱: `Bug Triage Bot`，設定適當有效期限
- 勾選權限 Add permission：
  - `Contents` (Access: `Read-only`)
- 點擊 "Generate token" 並複製 token (以 `github_pat_` 開頭)，貼到 .env 的 `GITHUB_TOKEN`

<img src="img/env_github_token.png" alt="env_github_token" width="60%">

### Claude Configuration
**Claude API Key (ANTHROPIC_API_KEY)**
- 前往 [Anthropic Console](https://console.anthropic.com/settings/keys)
- 點擊 API keys >  Create Key 建立新的 API 金鑰
- 複製 API 金鑰 (以 `sk-ant-` 開頭)，並貼到 .env 的 `ANTHROPIC_API_KEY`
 
 <img src="img/env_claude_api_key.png" alt="env_claude_api_key" width="60%">


### Slack MCP Server Configuration

**Slack 配置 (SLACK_BOT_TOKEN, SLACK_TEAM_ID)**

1. 前往 [Slack API Apps](https://api.slack.com/apps)
2. 建立新的 Slack App：
<img src="img/env_slack_1_create_app.png" alt="demo_1" width="60%">
3. 設定 Bot Token Scopes:
<img src="img/env_slack_2_oauth_permission_setting.png" alt="demo_2" width="60%">
<img src="img/env_slack_3_oauth_permission_scope.png" alt="demo_3" width="60%">
  請加入以下權限
  - `app_mentions:read` - 檢視在應用程式所在對話中直接提及 @Bot
  - `channels:history` - 檢視 @Bot 已加入的公開頻道中的訊息與內容
  - `channels:read` - 檢視工作區內公開頻道的基本資訊
  - `channels:history` - 檢視 Bug analyst 已加入的公開頻道中的訊息與內容
  - `channels:read` - 檢視工作區內公開頻道的基本資訊
  - `chat:write` - 以 @Bug analyst 身份發送訊息
  - `groups:history` - 檢視 Bug analyst 已加入的私人頻道中的訊息與內容
  - `groups:read` - 檢視 Bug analyst 已加入的私人頻道基本資訊
  - `reactions:write` - 新增與編輯表情符號反應
4. 安裝 App 到 Slack workspace 工作區
<img src="img/env_slack_4_install_app.png" alt="demo_4" width="60%">
5. 複製 "Bot User OAuth Token" (以 `xoxb-` 開頭)，貼到 .env 的 `SLACK_BOT_TOKEN`
<img src="img/env_slack_5_copy_token.png" alt="demo_5" width="60%">
6. 到 Slack Web 版，從 URL 中獲取 slack team id，貼到 .env 的 `SLACK_TEAM_ID`
<img src="img/env_slack_6_team_id.png" alt="demo_5" width="60%">

**GITHUB_SLACK_USER_MAPPING 介紹**

GITHUB_SLACK_USER_MAPPING 在本專案中作為 .env 參數設定，格式如下：

```env
GITHUB_SLACK_USER_MAPPING = {"github_username1":"slack.username1","github_username2":"slack.username2"}
```

- key 為 GitHub 帳號；value 為 Slack 使用者名稱
- 當系統偵測到可疑的 GitHub commit 的 author 時，會根據這份設定將 commit author 對應到 Slack 使用者名稱，方便在通知或標註時自動找到對應的人員。



(Optional)**GCP Error Reporting 配置**

- 如果分析過程要讓系統從 Google Cloud Error Reporting 搜索錯誤紀錄，或查詢 GCP datastore，才需要填。
- 不使用 GCP Error Reporting 的話可以全部留空

**GCP 設定**

- **建立服務帳戶**:
  1. 前往 [Google Cloud Console IAM](https://console.cloud.google.com/iam-admin/serviceaccounts) -  選擇待分析專案
  2. 點擊 "建立服務帳戶"

  <img src="img/env_gcp_1_create_account.png" alt="demo_1" width="60%">

  3. 設定角色權限: 
  設定
  - `Error Reporting Viewer` 
  - `Datastore Viewer`

  <img src="img/env_gcp_2_set_account_permission.png" alt="demo_2" width="60%">

- **創建 GCP service account Key**
  1. 在服務帳戶頁面點擊帳戶名稱
  2. "金鑰" 分頁 → "新增金鑰" → "建立新的金鑰"
    <img src="img/env_gcp_4_GCP_key.png" alt="demo_1" width="60%">

  3. 選擇 JSON 格式下載
    <img src="img/env_gcp_5_GCP_key_json.png" alt="demo_1" width="60%">

  4. 從 JSON 檔案中複製 project_id & client_email & private_key
    <img src="img/env_gcp_6_GCP_copy_key.png" alt="demo_1" width="60%">


  - 複製`project_id` 欄位的值到 .env `GCP_PROJECT_ID`
  - 複製 `client_email` 欄位的值到 .env `GCP_SERVICE_ACCOUNT_EMAIL`
    - 格式: `bug-triage-bot@junyiacademy.iam.gserviceaccount.com`
  - 複製`private_key` 欄位的值到 .env `GCP_SERVICE_ACCOUNT_PRIVATE_KEY`
    - **注意**: 需要包含完整的 `-----BEGIN PRIVATE KEY-----` 和 `-----END PRIVATE KEY-----`
    - 換行符號用 `\n` 表示

```py
GCP_PROJECT_ID=your-gcp-project-id
GCP_SERVICE_ACCOUNT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
GCP_SERVICE_ACCOUNT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT_HERE\n-----END PRIVATE KEY-----\n
```

### 3. 啟動服務

```bash
# 使用 Docker Compose 啟動
docker-compose up --build  
```
or 如果已經有 claude pro 帳號（不想額外花 api key 費用）
```bash
docker-compose build
docker-compose up -d
docker-compose exec bug-triage bash
claude # 登入 claude pro 帳號  ->  登入成功 ->  Ctrl-C 退出
python3 main.py
```


### 4. API 測試

4-1 **健康檢查**
```bash
curl http://localhost:8080/health
```

- APP 已經正確啟動
<img src="img/demo_app_health_check.png" alt="demo_1" width="60%">

4-2 **分析測試**

**Request**
- 第一次測試可以先簡化：利用 `custom_prompt` 輸入「這只是測試分析 ，先不要花太多時間分析，回傳 1+1 結果即可」加快分析速度

```bash

#直接帶入 error_message
curl -X POST http://localhost:8080/bug-triage/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "error_message": "首頁點選登入畫面沒有反應，console 出現 TypeError: Cannot read properties of undefined (reading 'foo')",
    "custom_prompt: "這只是測試分析 ，先不要花太多時間分析，回傳 1+1 結果即可"
    "slack_channel_id": "<slack_channel_id>", 
    "slack_thread_id": "<slack_thread_id>",
  }'
```


**Response**


1. 開始分析（根據問題複雜度，claude 會花上幾十秒~幾分鐘）

<img src="img/demo_app.png" alt="demo_app" width="60%">
<img src="img/demo_terminal.png" alt="demo_terminal" width="60%">

2. Bot 透過 Slack MCP 將結果回傳結果到 Slack thread

<img src="img/demo_response_demo.png" alt="demo_response_demo" width="60%">


### 5. 查看日誌
```bash
# Docker 容器日誌
docker-compose logs -f

# 本地執行日誌 (儲存在 log/ 目錄)
tail -f log/app.log
```


## API 參數說明

| 參數名稱                   | 型態      | 說明                                                                                             | 範例                      |
|------------------------|---------|------------------------------------------------------------------------------------------------|-------------------------|
| `error_message`             | 字串      | 使用者實際遇到的錯誤情境和錯誤訊息，例如：<br>•  | `e.g: 首頁點選登入畫面沒有反應，console 出現 TypeError: Cannot read properties of undefined (reading 'foo')"`
| `custom_prompt`             | 字串(可不填)      | （進階）客製化的分析指令，可要求AI 進行更特定化分析和回應      | `e.g: 分析時，請特別針對 login.js 進行分析，並且檢查最近一週的 git commit `    |
| `slack_channel_id`          | 字串      | Slack 頻道的 ID：分析結果將發送到該 channel。                                                    | `"C04KTHK3A67"`         |
| `slack_thread_id`           | 字串      | Slack 討論串 ID：分析結果將發送到該 thread。                                                     | `"1686629980.428519"`   |



## 選填（optional)

| 參數名稱                   | 型態      | 說明                                                                                             | 範例                      |
|------------------------|---------|------------------------------------------------------------------------------------------------|-------------------------|
| `error_reporting_group_id`  | 字串      | 來自 Google Cloud Error Reporting 的錯誤群組 ID，用於指定要分析的特定錯誤群組。                 | `"CPnh0d3mkNjLCw"`      |
| `dry_run`                   | 布林值    | 是否進行模擬運行。設為 `true` 時，僅模擬分析過程，不會實際執行。                                | `false` / `true`        |
| `read_slack_thread_details` | 布林值    | 是否需要讀取 Slack 討論串詳細內容。若為 `true`，系統將透過 MCP 工具獲取討論串上下文。           | `true`    


## Deployment




### 部署到 Cloud Run
1. 先 Fork 這個 repo 到你自己的 GitHub 帳號
2. 打開 Google Cloud Console，找到 Cloud Run 服務
3. 建立新服務時，選擇「連接儲存庫」（Connect repo），選擇剛剛 fork 的 GitHub repo
4. 按照導引設定自動部署，Cloud Run 會自動從你的 repo build 並部署服務

<img src="img/deploy_cloud_run.png" alt="deploy_cloud_run" width="60%">

或是也可以選擇部署到其他雲端平台，例如：AWS、Azure、Heroku

## 自動化串接（推薦n8n)

部署完後，即可透過任何自動化工具，讀取 slack 訊息並觸發 endpoint 

1. 建立 n8n Webhook Workflow
2. 讀取 slack 訊息並且將相關參數送至服務

<img src="img/demo_n8n.png" alt="demo_n8n" width="60%">

## Q&A

#### Q: 如何取得 Error Reporting Group ID?

1. **前往 Google Cloud Console**
   - 登入 [Google Cloud Console](https://console.cloud.google.com/)
   - 選擇專案: `junyiacademy`

2. **進入 Error Reporting**
   - 在左側選單中搜尋 "Error Reporting" 或前往 [Error Reporting](https://console.cloud.google.com/errors)
   - 會看到錯誤群組列表

3. **找到 Group ID**
   - 點擊任一錯誤群組
   - 在 URL 中可以找到 Group ID，格式如：
     ```
     https://console.cloud.google.com/errors/detail/[GROUP_ID]
     ```
   - 或在錯誤詳細頁面的 "Error group" 欄位中找到

4. **Group ID 範例**
   ```
   CPnh0d3mkNjLCw  # 實際的 Group ID 格式
   ```


### License  

[MIT License](http://opensource.org/licenses/MIT)

