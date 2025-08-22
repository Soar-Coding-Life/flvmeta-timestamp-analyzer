#!/usr/bin/env python3

import json
import subprocess
import sys

# 测试完整版本的MCP服务器
process = subprocess.Popen(
    ['./final_test_env/bin/flv-mcp-server'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

requests = [
    # 初始化
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    },
    # 初始化完成通知
    {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    },
    # 工具列表
    {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
]

try:
    input_data = '\n'.join(json.dumps(req) for req in requests) + '\n'
    stdout, stderr = process.communicate(input=input_data, timeout=10)
    
    print("=== 完整版本测试结果 ===")
    print(f"返回码: {process.returncode}")
    print(f"标准输出: {stdout}")
    print(f"标准错误: {stderr}")
    
    if stdout:
        lines = stdout.strip().split('\n')
        for i, line in enumerate(lines):
            if line and line.startswith('{'):
                try:
                    response = json.loads(line)
                    print(f"响应 {i+1}: {json.dumps(response, indent=2, ensure_ascii=False)}")
                    
                    # 检查工具列表
                    if 'result' in response and 'tools' in response['result']:
                        tools = response['result']['tools']
                        print(f"发现 {len(tools)} 个工具:")
                        for tool in tools:
                            print(f"  - {tool['name']}: {tool['description']}")
                except json.JSONDecodeError:
                    print(f"无法解析响应: {line}")
                    
except subprocess.TimeoutExpired:
    print("请求超时")
    process.kill()
except Exception as e:
    print(f"测试失败: {e}")