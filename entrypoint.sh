#!/bin/bash
set -e

echo "Starting Bug Triage Bot..."

# 如果有 .env 檔案就載入（local 開發）
if [ -f /app/.env ]; then
    set -a  # automatically export all variables
    # 使用 while read 逐行處理，避免 shell 解析空格問題
    while IFS= read -r line || [ -n "$line" ]; do
        # 跳過註解和空行
        [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
        # 導出環境變數
        export "$line"
    done < /app/.env
    set +a  # turn off automatic export
    echo "Loaded environment variables from .env file"
fi

# 設定 Claude MCP Slack 連線
if [ -n "$SLACK_BOT_TOKEN" ] && [ -n "$SLACK_TEAM_ID" ] ; then
    echo "Setting up Claude MCP Slack..."
    claude mcp add slack \
        --env SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN" \
        --env SLACK_TEAM_ID="$SLACK_TEAM_ID" \
        -- npx -y @zencoderai/slack-mcp-server 
    echo "Claude MCP Slack setup completed"
else
    echo "SLACK_BOT_TOKEN or SLACK_TEAM_ID is not found, skipping MCP setup"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "ANTHROPIC_API_KEY is set"
else
    echo "ANTHROPIC_API_KEY not found: Please set ANTHROPIC_API_KEY or login claude pro account"
fi

# 設定 Claude Github MCP 連線
if [ -n "$GITHUB_TOKEN" ]; then
    echo "Setting up Github MCP ..."
    claude mcp add --transport http github https://api.githubcopilot.com/mcp -H "Authorization: Bearer $GITHUB_TOKEN"
    echo "Claude MCP Github setup completed"
else
    echo "SLACK_BOT_TOKEN not found, skipping MCP setup"
fi

echo "Starting Python application..."

# 執行原本的命令
if [ "$PROJECT" = "DEV" ]; then
    echo "PROJECT=DEV，跳過自動啟動，保持容器存活"
    exec tail -f /dev/null
fi
exec "$@"
