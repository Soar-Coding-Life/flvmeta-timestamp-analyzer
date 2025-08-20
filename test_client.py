#!/usr/bin/env python3
"""
FLV时间戳分析MCP服务测试客户端
"""

import subprocess
import json
import sys

def test_mcp_service(file_path):
    """测试MCP服务"""
    # 构造初始化请求
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize", 
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    # 构造工具调用请求
    tool_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "analyze_flv",
            "arguments": {
                "file_path": file_path
            }
        }
    }
    
    # 启动MCP服务进程
    process = subprocess.Popen(
        [sys.executable, 'mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # 发送请求
    input_data = json.dumps(init_request) + '\n' + json.dumps(tool_request) + '\n'
    stdout, stderr = process.communicate(input=input_data)
    
    # 检查是否有错误
    if process.returncode != 0:
        print(f"Process error (exit code {process.returncode}):")
        print(f"stderr: {stderr}")
        return None
        
    # 解析响应
    try:
        # 按行分割输出
        lines = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
        
        # 找到工具调用的响应（通常是第二个响应）
        for line in lines:
            try:
                response = json.loads(line)
                if response.get("id") == 2:  # 工具调用请求的ID
                    return response
            except json.JSONDecodeError:
                continue
                
        # 如果没有找到ID为2的响应，返回最后一个有效的JSON
        if lines:
            return json.loads(lines[-1])
        
        return None
    except Exception as e:
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