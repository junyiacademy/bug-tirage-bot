import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

def run_with_live_output(cmd):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # 行緩衝
        universal_newlines=True
    )
    
    stdout_lines = []
    stderr_lines = []
    
    # 實時讀取 stdout
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            logger.info(f"Command output: {output.strip()}")  # 使用 logger 替代 print
            stdout_lines.append(output)  # 同時記錄
    
    # 獲取任何剩餘的 stderr
    stderr = process.stderr.read()
    if stderr:
        stderr_lines.append(stderr)
    
    return ''.join(stdout_lines), ''.join(stderr_lines)