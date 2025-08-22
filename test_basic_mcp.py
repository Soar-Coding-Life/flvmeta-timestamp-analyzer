#!/usr/bin/env python3

import json
import subprocess
import sys

# 测试基本安装的MCP服务器
process = subprocess.Popen(
    ['flv-mcp-server'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# 发送初始化请求
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

try:
    stdout, stderr = process.communicate(
        input=json.dumps(init_request) + '\n',
        timeout=5
    )
    
    print("返回码:", process.returncode)
    print("标准输出:", stdout)
    print("标准错误:", stderr)
    
    if stdout:
        try:
            response = json.loads(stdout.strip())
            print("解析响应:", json.dumps(response, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("无法解析JSON响应")
            
except subprocess.TimeoutExpired:
    print("请求超时")
    process.kill()
except Exception as e:
    print(f"测试失败: {e}")