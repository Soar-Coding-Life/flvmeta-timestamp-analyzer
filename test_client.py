#!/usr/bin/env python3
"""
FLV时间戳分析MCP服务测试客户端
"""

import subprocess
import json
import sys

def test_mcp_service(file_path):
    """测试MCP服务"""
    # 构造请求数据
    request_data = {
        "file_path": file_path
    }
    
    # 启动MCP服务进程
    process = subprocess.Popen(
        [sys.executable, 'mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 发送请求并获取响应
    stdout, stderr = process.communicate(input=json.dumps(request_data))
    
    # 检查是否有错误
    if process.returncode != 0:
        print(f"Process error (exit code {process.returncode}):")
        print(f"stderr: {stderr}")
        return None
        
    # 解析响应
    try:
        response = json.loads(stdout)
        return response
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print(f"Raw output: {stdout}")
        return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_client.py <flv_file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    print(f"Testing MCP service with file: {file_path}")
    
    response = test_mcp_service(file_path)
    
    if response:
        print("Received response:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
        print("Failed to get response from MCP service")
        sys.exit(1)