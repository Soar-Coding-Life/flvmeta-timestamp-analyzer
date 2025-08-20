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

def send_response(response):
    """发送响应到标准输出"""
    logger.debug(f"Sending response: {response}")
    print(json.dumps(response), flush=True)

def send_error(message, details=None):
    """发送错误响应"""
    logger.error(f"Error: {message}, Details: {details}")
    error_response = {
        "error": message,
        "details": details or ""
    }
    send_response(error_response)

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

def analyze_flv_via_mcp(request_data):
    """通过MCP协议分析FLV文件"""
    logger.info("Starting FLV analysis")
    try:
        # 验证输入
        if 'file_path' not in request_data:
            send_error("Missing 'file_path' in request")
            return
            
        file_path = request_data['file_path']
        logger.debug(f"Analyzing file: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            send_error(f"File not found: {file_path}")
            return
            
        # 使用flvmeta解析FLV文件
        logger.debug("Calling flvmeta to parse FLV file")
        json_data = parse_flv_with_flvmeta(file_path)
        logger.debug(f"flvmeta parsing completed, got {len(json_data.get('tags', []))} tags")
        
        # 分析时间戳变化
        logger.debug("Analyzing timestamps")
        analysis_data = analyze_timestamps(json_data, file_path)
        logger.debug("Timestamp analysis completed")
        
        # 构造响应
        response = {
            "status": "success",
            "data": analysis_data
        }
        
        logger.info("Analysis completed successfully")
        send_response(response)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        send_error(f"Analysis failed: {str(e)}", traceback.format_exc())

def handle_mcp_protocol():
    """处理MCP协议握手和消息"""
    # 读取MCP协议握手消息
    input_line = sys.stdin.readline()
    if not input_line:
        return False
        
    try:
        # 解析握手消息
        handshake = json.loads(input_line.strip())
        if handshake.get("protocol_version") != "mcp-0.1":
            send_error("Unsupported protocol version")
            return False
            
        # 发送握手响应
        response = {
            "protocol_version": "mcp-0.1",
            "models": [
                {
                    "name": "flv-timestamp-analyzer",
                    "description": "FLV音视频时间戳分析工具",
                    "capabilities": {
                        "can_stream": False,
                        "can_accept_audio_input": False,
                        "can_accept_image_input": False,
                        "can_accept_text_input": False,
                        "can_accept_file_input": True
                    }
                }
            ]
        }
        print(json.dumps(response), flush=True)
        return True
    except Exception as e:
        logger.error(f"Handshake failed: {str(e)}")
        send_error(f"Handshake failed: {str(e)}")
        return False

def main():
    """主函数 - 通过stdio提供MCP服务"""
    # 检查是否是直接运行脚本而不是作为MCP服务
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        # 显示帮助信息
        print("FLV时间戳分析MCP服务")
        print("用法:")
        print("  直接运行: python3 mcp_server.py <input.flv> [output.html]")
        print("  作为MCP服务: python3 mcp_server.py")
        print("  安装后: flv-timestamp-analyzer <input.flv> [output.html]")
        return
    
    # 如果有命令行参数且不是MCP握手参数，则作为命令行工具运行
    if len(sys.argv) > 1 and not sys.stdin.isatty():
        # 作为MCP服务运行
        logger.info("FLV MCP Server started")
        
        # 加载配置
        config = load_config()
        logger.info(f"Loaded config: {config}")
        
        # 处理MCP协议握手
        if not handle_mcp_protocol():
            logger.error("MCP protocol handshake failed")
            return
        
        try:
            logger.debug("Waiting for input from stdin")
            # 读取标准输入的JSON请求
            input_data = sys.stdin.read()
            logger.debug(f"Received input: {input_data}")
            
            if not input_data:
                send_error("No input received")
                return
                
            # 解析JSON请求
            try:
                request_data = json.loads(input_data)
                logger.debug(f"Parsed request data: {request_data}")
            except json.JSONDecodeError as e:
                send_error("Invalid JSON in request", str(e))
                return
                
            # 处理请求
            analyze_flv_via_mcp(request_data)
            
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            send_error(f"Server error: {str(e)}", traceback.format_exc())
        finally:
            logger.info("FLV MCP Server shutting down")
    elif len(sys.argv) > 1:
        # 作为命令行工具运行，调用原始分析工具
        from flv_timestamp_analyzer import main as analyzer_main
        analyzer_main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        # 作为MCP服务运行
        logger.info("FLV MCP Server started")
        
        # 加载配置
        config = load_config()
        logger.info(f"Loaded config: {config}")
        
        # 处理MCP协议握手
        if not handle_mcp_protocol():
            logger.error("MCP protocol handshake failed")
            return
        
        try:
            logger.debug("Waiting for input from stdin")
            # 读取标准输入的JSON请求
            input_data = sys.stdin.read()
            logger.debug(f"Received input: {input_data}")
            
            if not input_data:
                send_error("No input received")
                return
                
            # 解析JSON请求
            try:
                request_data = json.loads(input_data)
                logger.debug(f"Parsed request data: {request_data}")
            except json.JSONDecodeError as e:
                send_error("Invalid JSON in request", str(e))
                return
                
            # 处理请求
            analyze_flv_via_mcp(request_data)
            
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            send_error(f"Server error: {str(e)}", traceback.format_exc())
        finally:
            logger.info("FLV MCP Server shutting down")

if __name__ == '__main__':
    main()