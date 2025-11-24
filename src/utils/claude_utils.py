"""
Claude Analysis Utilities
"""
import re
import subprocess
import logging
from typing import Optional
from pathlib import Path
from src.core.models import SlackPayload

logger = logging.getLogger(__name__)

jq_filter_for_analysis_result = '''
if .type == "assistant" then
  (.message.content[]? |
    if .type == "text" then
      .text
    elif .type == "tool_use" then
      if .name == "Grep" then
        "Grep(\(.input.pattern) in \(.input.path // .input.file_path))"
      elif .name == "Read" then
        "Read(\(.input.path // .input.file_path))"
      elif .name == "web_search" then
        "Search(\(.input.query))"
      elif .name == "Bash" then
        "Bash(\(.input.command))"
      elif .name == "TodoWrite" then
        "TodoWrite: " + (.input.todos | map(.content) | join(" -> "))
      else
        "\(.name)(\(.input | tojson))"
      end
    else
      empty
    end
  )
elif .type == "result" then
  "result:\(.result)"
else
  empty
end
'''

class ClaudeUtils:
    """Utility class for Claude Code operations"""
    
    def __init__(self, codebase_dir: str = None):
        self.codebase_dir = codebase_dir


    def validate_analysis_output(self, output: str) -> bool:
        """
        驗證 Claude Code 輸出的字串是否包含所有預期的 JSON 欄位
        """
        if not output:
            logger.error("[validate_analysis_output] Output is None or empty")
            return False

        required_fields = [
            "root_cause_analysis",
            "root_cause_file_codebase",
            "suspect_commit",
            "suspect_commit_author",
            "recommended_person",
            "recommended_reason",
            "suggestion"
        ]
        for field in required_fields:
            if field not in output:
                logger.error(f"[validate_analysis_output] Claude 輸出缺少必要欄位: {field}")
                return False
        return True

    def validate_issue_summary_output(self, output: str) -> bool:
        """
        驗證問題摘要輸出的字串是否符合預期的
        """
        # 檢查 output 是否為 None 或空字串
        if not output or len(output) < 20:
            logger.error("[validate_issue_summary_output] Output is None or empty")
            return False
            
        keywords = [
            "issue_summary",
            "problem_description",
            "technical_observations",
            "問題摘要",
        ]
        for keyword in keywords:
            if keyword in output:
                logger.info(f"[validate_issue_summary_output] 找到必要關鍵字: {keyword}")
                return True
        return False

    def generate_issue_summary(self, error_message: str, slack_payload: SlackPayload) -> str:
        """Generate issue summary with retry logic"""
        issue_summary_generator_prompt_file = f"src/prompt/issue_summary_generator_prompt.md"
        prompt = (
            f"對於 channel id: '{slack_payload.channel_id}' 和 thread id: '{slack_payload.thread_id}' 的 {error_message}' 這個錯誤訊息/問題回報 "
            f"根據 {issue_summary_generator_prompt_file} 的指示生成問題摘要"
        )

        
        max_retries = 2
        attempt = 0
        
        while attempt <= max_retries:
            try:
                logger.info(f"[generate_issue_summary] 嘗試第 {attempt + 1} 次生成問題摘要")
                logger.info(f"[generate_issue_summary - prompt]: {prompt}")
                cmd = ['claude', '-p', prompt]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )
                # 儲存 stdout 和 stderr 訊息
                stdout = result.stdout if result.stdout else ""
                stderr = result.stderr if result.stderr else ""
                logger.info(f"--- STDOUT: generate_issue_summary ---")
                logger.info(f"{stdout}")
                logger.info(f"--- STDERR: generate_issue_summary ---")
                logger.info(f"{stderr}")
            
                # 驗證輸出格式
                if self.validate_issue_summary_output(stdout):
                    logger.info(f"[generate_issue_summary] 第 {attempt + 1} 次嘗試成功")
                    return stdout
                else:
                    logger.warning(f"[generate_issue_summary] 第 {attempt + 1} 次嘗試驗證失敗")
                    if attempt < max_retries:
                        logger.info(f"[generate_issue_summary] 準備重試第 {attempt + 2} 次...")
                    
            except Exception as e:
                logger.error(f"[generate_issue_summary] 第 {attempt + 1} 次嘗試失敗: {e}")
                if attempt < max_retries:
                    logger.info(f"[generate_issue_summary] 準備重試第 {attempt + 2} 次...")
            
            attempt += 1
        
        logger.error(f"[generate_issue_summary] 所有 {max_retries + 1} 次嘗試都失敗")
        return None
            
    def analyze_error(self, error_detail: str, custom_prompt: Optional[str] = None) -> str:
        """Analyze error with smart retry logic"""
        prompt_file = f"src/prompt/analysis_prompt.md"
        
        base_prompt = (
            f"對於『{error_detail}』這個錯誤訊息／問題回報，"
            f"請根據 {prompt_file} 的指示分析，"
            f"並嚴格確保輸出結果符合指定的 JSON 格式。"
        )
        
        # 如果有自訂 prompt，附加到基礎 prompt 後面
        if custom_prompt:
            prompt = f"{base_prompt}\n\n此外，請特別注意以下自訂指示：\n{custom_prompt}"
        else:
            prompt = base_prompt

        max_retries = 3
        attempt = 1

        while attempt <= max_retries:
            try:
                logger.info(f"[analyze_error] 嘗試第 {attempt} 次進行問題分析")
                logger.info(f"[analyze_error] prompt: {prompt}")
                
                cmd = f"claude --add-dir {self.codebase_dir} -p --verbose --output-format stream-json '{prompt}' | jq -r '{jq_filter_for_analysis_result}'"
                logger.info(f"[analyze_error] 開始執行 Claude 命令...")
                logger.info(f"[analyze_error] Claude 正在分析，根據問題複雜度可能需要幾十秒~幾分鐘...")

                proc = subprocess.Popen(
                    cmd,
                    shell=True,
                    executable="/bin/bash",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # 合併輸出，避免雙管道阻塞
                    text=True,
                    bufsize=1,                 # 行緩衝
                )

                lines = []
                for line in proc.stdout:
                    line = line.rstrip("\n")
                    logger.info(line)          # 即時顯示
                    lines.append(line)         # 同步累積

                rc = proc.wait()
                full_stdout = "\n".join(lines)
                # 解析 full_stdout 當中的 "result:" 後之內容
                match = re.search(r"result:(.*)", full_stdout, re.DOTALL)
                stdout = match.group(1).strip() if match else ""

                logger.info(f"--- STDOUT: analyze_error ---")
                logger.info(f"{stdout}")
                if stdout and self.validate_analysis_output(stdout):
                    return stdout
                
                # 檢查是否為連接錯誤
                if self.is_connection_error(stdout):
                    logger.warning(f"[analyze_error] 第 {attempt} 次嘗試遇到連接錯誤，需要重試")
                    if attempt < max_retries:
                        logger.info(f"[analyze_error] 準備重試第 {attempt + 1} 次...")
                        attempt += 1
                        continue
                    else:
                        logger.error(f"[analyze_error] 連接錯誤，所有重試都失敗")
                        return None

                # 檢查是否有內容但格式不正確
                # case1: 有內容，但沒格式化
                if len(stdout) > 30:
                    logger.warning(f"[analyze_error] 第 {attempt} 次嘗試有內容但格式不正確，嘗試格式化修正")
                    formatted_result = self.format_analysis_result(stdout)
                    if formatted_result and self.validate_analysis_output(formatted_result):
                        logger.info(f"[analyze_error] 格式化修正成功")
                        return formatted_result
                else:
                    logger.warning(f"[analyze_error] 第 {attempt} 次嘗試沒內容，需要重試")
                    if attempt < max_retries:
                        logger.info(f"[analyze_error] 準備重試第 {attempt + 1} 次...")
                        attempt += 1
                        continue
                    else:
                        logger.error(f"[analyze_error] 沒內容，所有重試都失敗")
                        return None
   
            except Exception as e:
                logger.error(f"[analyze_error] 第 {attempt} 次嘗試失敗: {e}")
                if attempt < max_retries:
                    logger.info(f"[analyze_error] 準備重試第 {attempt + 1} 次...")
                    attempt += 1
        
        logger.error(f"[analyze_error] 所有 {max_retries} 次嘗試都失敗")
        return None

    def is_connection_error(self, output: str) -> bool:
        """檢查是否為連接錯誤"""
        if not output:
            return True
        
        connection_error_keywords = [
            "Connection error",
            "Connection timeout", 
            "Network error",
            "Failed to connect",
            "Connection refused",
            "API Error"
        ]
        
        for keyword in connection_error_keywords:
            if keyword in output:
                return True
        
        return False

    def format_analysis_result(self, result: str) -> str:
        """Format analysis result (single attempt)"""
        prompt_file = f"src/prompt/analysis_prompt.md"
        prompt = f"針對`{result}` 請確保分析結果符合 {prompt_file} 的格式，並輸出符合要求的 JSON 格式"
        
        
        try:
            cmd = ['claude', '-p', prompt]
            logger.info(f"[format_analysis_result] prompt: {prompt}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            # 儲存 stdout 和 stderr 訊息
            stdout = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""
            logger.info(f"--- STDOUT: analyze_error ---")
            logger.info(f"{stdout}")
            logger.info(f"--- STDERR: analyze_error ---")
            logger.info(f"{stderr}")

            return stdout
            
        except Exception as e:
            logger.error(f"[format_analysis_result] format analysis result failed: {e}")
            return None

    def analyze_bug(self, error_message: str, slack_payload: SlackPayload, custom_prompt: Optional[str] = None) -> Optional[str]:
        """Analyze bug using Claude Code with individual method retry logic"""
        try:
            logger.info(f"[analyze_bug] Start to analyze bug")
            
            # 階段 1: 問題摘要（如果需要）
            if slack_payload.read_slack_thread_details and slack_payload.channel_id and slack_payload.thread_id:                
                issue_summary = self.generate_issue_summary(error_message, slack_payload)
                if not issue_summary:
                    logger.error(f"[analyze_bug] generate_issue_summary 生成失敗")
                    return None
                error_message = issue_summary

            # 階段 2: 問題分析
            analysis_result = self.analyze_error(error_message, custom_prompt)
            if not analysis_result:
                logger.error(f"[analyze_bug] analyze_error 失敗")
                return None
            logger.info(f"[analyze_bug] 問題分析完成")
            logger.info(f"[analyze_bug] analysis_result: {analysis_result}")
            return analysis_result
                
        except Exception as e:
            logger.error(f"[analyze_bug] Claude analysis failed: {e}")
            return None