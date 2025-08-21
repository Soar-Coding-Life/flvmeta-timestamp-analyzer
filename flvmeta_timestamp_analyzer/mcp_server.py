#!/usr/bin/env python3
"""
MCP 服务器入口点
支持 FastMCP 和原始版本的自动选择
"""

import sys
import os

def main():
    """MCP 服务器主入口"""
    try:
        # 尝试使用 FastMCP 版本
        try:
            # 导入 FastMCP 版本的服务器
            from fastmcp import FastMCP
            from pydantic import BaseModel, Field
            import json
            from pathlib import Path
            from typing import Optional
            
            # 导入分析器功能
            from .analyzer import parse_flv_with_flvmeta, analyze_timestamps, create_charts
            
            # 使用 FastMCP 运行服务器
            exec(open(os.path.join(os.path.dirname(__file__), '..', 'mcp_server_fastmcp.py')).read())
            
        except ImportError:
            print("FastMCP 不可用，使用原始 MCP 服务器...", file=sys.stderr)
            
            # 回退到原始版本
            import json
            
            def handle_mcp_request(request):
                """处理MCP请求"""
                try:
                    method = request.get("method")
                    params = request.get("params", {})
                    request_id = request.get("id")
                    
                    if method == "initialize":
                        # 初始化响应
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {
                                    "tools": {
                                        "listChanged": False
                                    }
                                },
                                "serverInfo": {
                                    "name": "flv-timestamp-analyzer",
                                    "version": "1.0.7"
                                }
                            }
                        }
                    elif method == "tools/list":
                        # 返回可用工具列表
                        response = {
                            "jsonrpc": "2.0", 
                            "id": request_id,
                            "result": {
                                "tools": [
                                    {
                                        "name": "analyze_flv",
                                        "description": "分析FLV文件的时间戳信息，提供详细报告和异常检测",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "file_path": {
                                                    "type": "string",
                                                    "description": "FLV文件路径"
                                                }
                                            },
                                            "required": ["file_path"]
                                        }
                                    }
                                ]
                            }
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        }
                        
                    return response
                    
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
            
            # MCP 服务器主循环
            try:
                for line in sys.stdin:
                    if not line.strip():
                        continue
                        
                    try:
                        request = json.loads(line.strip())
                        response = handle_mcp_request(request)
                        print(json.dumps(response), flush=True)
                        
                    except json.JSONDecodeError:
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32700,
                                "message": "Parse error"
                            }
                        }
                        print(json.dumps(error_response), flush=True)
                        
            except KeyboardInterrupt:
                pass
            
    except KeyboardInterrupt:
        print("\nMCP 服务器已停止", file=sys.stderr)
    except Exception as e:
        print(f"MCP 服务器错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()