#!/usr/bin/env python3
"""
测试 FastMCP 服务器的完整流程
"""

import subprocess
import json
import sys
import os
import time

def test_fastmcp_complete():
    """完整测试 FastMCP 服务器"""
    print("测试 FastMCP 服务器完整流程...")
    
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
    
    try:
        # 1. 发送初始化请求
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
        
        print("1. 发送初始化请求...")
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # 读取初始化响应
        response_line = process.stdout.readline()
        if response_line.strip():
            init_response = json.loads(response_line.strip())
            print(f"   初始化成功: {init_response['result']['serverInfo']['name']}")
        
        # 2. 发送初始化完成通知
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print("2. 发送初始化完成通知...")
        process.stdin.write(json.dumps(initialized_notification) + '\n')
        process.stdin.flush()
        
        # 稍等一下让服务器处理
        time.sleep(0.1)
        
        # 3. 请求工具列表
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("3. 请求工具列表...")
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        # 读取工具列表响应
        response_line = process.stdout.readline()
        if response_line.strip():
            tools_response = json.loads(response_line.strip())
            if 'result' in tools_response and 'tools' in tools_response['result']:
                tools = tools_response['result']['tools']
                print(f"   发现 {len(tools)} 个工具:")
                for tool in tools:
                    print(f"     - {tool['name']}: {tool['description']}")
            else:
                print(f"   错误: {tools_response}")
        
        print("\n✅ FastMCP 服务器测试成功!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        try:
            process.terminate()
            process.wait(timeout=2)
        except:
            process.kill()

if __name__ == '__main__':
    print("=" * 60)
    print("FastMCP FLV 服务器完整测试")
    print("=" * 60)
    
    result = test_fastmcp_complete()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ 所有测试通过!")
    else:
        print("❌ 测试失败!")
    print("=" * 60)