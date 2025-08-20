#!/usr/bin/env python3
"""
FLV时间戳分析MCP服务调试客户端
用于调试和测试MCP服务
"""

import subprocess
import json
import sys
import time

def debug_mcp_service(file_path):
    """调试MCP服务"""
    print(f"Debugging MCP service with file: {file_path}")
    
    # 构造请求数据
    request_data = {
        "file_path": file_path
    }
    
    print(f"Request data: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
    
    # 启动MCP服务进程
    print("Starting MCP service process...")
    process = subprocess.Popen(
        [sys.executable, 'mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(f"Process started with PID: {process.pid}")
    
    # 发送请求并获取响应
    print("Sending request to MCP service...")
    start_time = time.time()
    stdout, stderr = process.communicate(input=json.dumps(request_data))
    end_time = time.time()
    
    print(f"Request completed in {end_time - start_time:.2f} seconds")
    
    # 检查是否有错误
    if process.returncode != 0:
        print(f"Process error (exit code {process.returncode}):")
        print(f"stderr: {stderr}")
        return None
        
    # 解析响应
    try:
        response = json.loads(stdout)
        print("Received response:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
        return response
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        print(f"Raw output: {stdout}")
        return None

def interactive_debug():
    """交互式调试模式"""
    print("=== FLV MCP Server Interactive Debugger ===")
    print("Enter 'quit' to exit")
    
    while True:
        file_path = input("\nEnter FLV file path: ").strip()
        
        if file_path.lower() == 'quit':
            break
            
        if not file_path:
            continue
            
        print("\n" + "="*50)
        response = debug_mcp_service(file_path)
        print("="*50)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        # 进入交互式调试模式
        interactive_debug()
    else:
        file_path = sys.argv[1]
        debug_mcp_service(file_path)