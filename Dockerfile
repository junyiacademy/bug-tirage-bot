ARG TARGETPLATFORM=linux/amd64
FROM --platform=$TARGETPLATFORM python:3.10-bookworm
# FROM python:3.10-bookworm

# 用 bash 當預設 shell（nvm 需要）
SHELL ["/bin/bash", "-lc"]

# 移除 build arguments，改用 runtime 環境變數

# 安裝基礎工具與 git
RUN apt-get update && apt-get install -y curl ca-certificates git jq && rm -rf /var/lib/apt/lists/*

# 安裝 nvm 並安裝 Node 20
ENV NVM_DIR=/root/.nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash \
 && source $NVM_DIR/nvm.sh \
 && nvm install 20 \
 && nvm alias default 20 \
 && node -v && npm -v

ENV PATH="/root/.nvm/versions/node/v20.21.1/bin:$PATH"

WORKDIR /app
COPY . /app

# Python install
RUN python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt

# 安裝 Claude Code CLI（SDK 需要）
RUN npm install -g @anthropic-ai/claude-code
# 安裝 MCP server
RUN npm install -g @zencoderai/slack-mcp-server

# 複製並設定 entrypoint 腳本
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set environment variables for Cloud Run
ENV PORT=8080
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

ENV PATH="/root/.nvm/versions/node/v20.19.5/bin:$PATH"

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python3", "main.py"]
