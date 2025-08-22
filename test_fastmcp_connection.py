#!/usr/bin/env python3
"""
测试 FastMCP 服务器连接
"""

import subprocess
import json
import sys
import os

def test_fastmcp_server():
    """测试 FastMCP 服务器连接"""
    print("测试 FastMCP 服务器连接...")
    
    # 启动 FastMCP 服务器进程
    env = os.environ.copy()
    env['PATH'] = '/Users/wangguibin/Desktop/flvmeta-timestamp-analyzer/venv/bin:' + env['PATH']
    
    process = subprocess.Popen(
        ['python3', 'mcp_server_fastmcp.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='/Users/wangguibin/Desktop/flvmeta-timestamp-analyzer',
        env=env
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
    
    print(f"发送初始化请求: {json.dumps(init_request)}")
    
    try:
        # 发送请求
        stdout, stderr = process.communicate(
            input=json.dumps(init_request) + '\n',
            timeout=10
        )
        
        print(f"返回码: {process.returncode}")
        print(f"标准输出: {stdout}")
        print(f"标准错误: {stderr}")
        
        if stdout:
            try:
                response = json.loads(stdout.strip())
                print(f"解析响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
                return response
            except json.JSONDecodeError as e:
                print(f"JSON 解析失败: {e}")
        
    except subprocess.TimeoutExpired:
        print("请求超时")
        process.kill()
    except Exception as e:
        print(f"测试失败: {e}")
    
    return None

def test_fastmcp_tools_list():
    """测试 FastMCP 工具列表"""
    print("\n测试 FastMCP 工具列表...")
    
    # 启动 FastMCP 服务器进程  
    env = os.environ.copy()
    env['PATH'] = '/Users/wangguibin/Desktop/flvmeta-timestamp-analyzer/venv/bin:' + env['PATH']
    
    process = subprocess.Popen(
        ['python3', 'mcp_server_fastmcp.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd='/Users/wangguibin/Desktop/flvmeta-timestamp-analyzer',
        env=env
    )
    
    # 发送工具列表请求
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    print(f"发送工具列表请求: {json.dumps(tools_request)}")
    
    try:
        stdout, stderr = process.communicate(
            input=json.dumps(tools_request) + '\n',
            timeout=10
        )
        
        print(f"返回码: {process.returncode}")
        print(f"标准输出: {stdout}")
        print(f"标准错误: {stderr}")
        
        if stdout:
            try:
                response = json.loads(stdout.strip())
                print(f"工具列表响应: {json.dumps(response, indent=2, ensure_ascii=False)}")
                
                # 检查工具列表
                if 'result' in response and 'tools' in response['result']:
                    tools = response['result']['tools']
                    print(f"\n发现 {len(tools)} 个工具:")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")
                
                return response
            except json.JSONDecodeError as e:
                print(f"JSON 解析失败: {e}")
        
    except subprocess.TimeoutExpired:
        print("请求超时")
        process.kill()
    except Exception as e:
        print(f"测试失败: {e}")
    
    return None

if __name__ == '__main__':
    print("=" * 60)
    print("FastMCP FLV 服务器连接测试")
    print("=" * 60)
    
    # 测试初始化
    init_result = test_fastmcp_server()
    
    # 测试工具列表
    tools_result = test_fastmcp_tools_list()
    
    print("\n" + "=" * 60)
    print("FastMCP 测试完成")
    print("=" * 60)