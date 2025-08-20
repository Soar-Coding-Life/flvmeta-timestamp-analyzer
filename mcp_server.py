#!/usr/bin/env python3
"""
FLV时间戳分析MCP服务
通过stdio与AI客户端通信，接收JSON请求并返回分析结果
"""

import sys
import json
import os
import subprocess
import traceback
import logging
import logging.handlers

# 配置日志
def setup_logging():
    # 创建日志记录器
    logger = logging.getLogger('flv_mcp')
    logger.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 添加文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        'mcp_server.log', maxBytes=1024*1024, backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# 全局日志记录器
logger = setup_logging()

def load_config():
    """加载配置文件"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load config.json, using defaults: {e}")
        return {
            "log_level": "info",
            "max_workers": 4,
            "request_timeout": 30
        }

def handle_mcp_request(request):
    """处理MCP请求"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.debug(f"处理方法: {method}")
        
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
                        "version": "1.0.5"
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
                            "description": "分析FLV文件的时间戳信息",
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
        elif method == "tools/call":
            # 执行工具调用
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "analyze_flv":
                file_path = arguments.get("file_path")
                if not file_path:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: file_path is required"
                        }
                    }
                else:
                    # 执行FLV分析
                    try:
                        from flvmeta_timestamp_analyzer.analyzer import parse_flv_with_flvmeta, analyze_timestamps
                        
                        if not os.path.exists(file_path):
                            raise FileNotFoundError(f"文件不存在: {file_path}")
                            
                        # 解析FLV文件
                        json_data = parse_flv_with_flvmeta(file_path)
                        analysis_data = analyze_timestamps(json_data, file_path)
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"FLV文件分析完成！\n文件名: {analysis_data['filename']}\n总标签数: {analysis_data['total_tags']}\n音频帧数: {len(analysis_data['audio']['timestamps'])}\n视频帧数: {len(analysis_data['video']['timestamps'])}"
                                    }
                                ],
                                "isError": False
                            }
                        }
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text", 
                                        "text": f"分析失败: {str(e)}"
                                    }
                                ],
                                "isError": True
                            }
                        }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
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
        logger.error(f"处理请求时出错: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

def main():
    """主函数 - MCP服务器"""
    # 检查帮助参数
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("FLV时间戳分析MCP服务")
        print("用法:")
        print("  作为MCP服务: python3 mcp_server.py")
        print("  命令行工具: flv-timestamp-analyzer <input.flv> [output.html]")
        return
        
    # 检查是否作为命令行工具运行
    if len(sys.argv) > 1:
        from flvmeta_timestamp_analyzer.analyzer import main as analyzer_main
        analyzer_main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
        return
    
    # 作为MCP服务运行
    logger.info("启动FLV MCP服务器")
    
    try:
        # MCP服务器主循环
        for line in sys.stdin:
            if not line.strip():
                continue
                
            try:
                request = json.loads(line.strip())
                logger.debug(f"收到请求: {request}")
                
                response = handle_mcp_request(request)
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.error(f"处理请求时出错: {str(e)}")
                error_response = {
                    "jsonrpc": "2.0", 
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        logger.info("收到中断信号，关闭服务器")
    except Exception as e:
        logger.error(f"服务器错误: {str(e)}")
    finally:
        logger.info("FLV MCP服务器已关闭")

if __name__ == '__main__':
    main()