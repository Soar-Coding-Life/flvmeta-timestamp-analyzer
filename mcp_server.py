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
                        "version": "1.0.6"
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
                        },
                        {
                            "name": "analyze_flv_json",
                            "description": "分析FLV文件并返回完整的JSON数据结构，包含所有时间戳信息",
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
                        },
                        {
                            "name": "generate_flv_report",
                            "description": "分析FLV文件并生成HTML可视化报告",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "file_path": {
                                        "type": "string", 
                                        "description": "FLV文件路径"
                                    },
                                    "output_path": {
                                        "type": "string",
                                        "description": "HTML输出文件路径（可选）"
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
            
            if tool_name in ["analyze_flv", "analyze_flv_json", "generate_flv_report"]:
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
                        from flvmeta_timestamp_analyzer.analyzer import parse_flv_with_flvmeta, analyze_timestamps, create_charts
                        import os
                        import json as json_lib
                        
                        if not os.path.exists(file_path):
                            raise FileNotFoundError(f"文件不存在: {file_path}")
                            
                        # 解析FLV文件
                        json_data = parse_flv_with_flvmeta(file_path)
                        analysis_data = analyze_timestamps(json_data, file_path)
                        
                        if tool_name == "analyze_flv_json":
                            # 返回完整的JSON数据
                            response = {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "result": {
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": f"**完整FLV分析数据 - {analysis_data['filename']}**\n\n```json\n{json_lib.dumps(analysis_data, indent=2, ensure_ascii=False)}\n```"
                                        }
                                    ],
                                    "isError": False
                                }
                            }
                        elif tool_name == "generate_flv_report":
                            # 生成HTML报告
                            output_path = arguments.get("output_path") 
                            if not output_path:
                                base_name = os.path.splitext(os.path.basename(file_path))[0]
                                output_path = f"{base_name}_timestamp_analysis.html"
                            
                            try:
                                create_charts(analysis_data, output_path)
                                abs_path = os.path.abspath(output_path)
                                
                                response = {
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "result": {
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": f"📈 **HTML可视化报告已生成**\n\n**文件位置**: {abs_path}\n**文件大小**: {os.path.getsize(abs_path) / 1024:.1f} KB\n\n报告包含:\n- 音视频时间戳增量变化曲线\n- 异常点标记和分析\n- 交互式图表（支持缩放和拖拽）\n- 详细统计信息\n\n可以在浏览器中打开查看完整的可视化分析结果。"
                                            }
                                        ],
                                        "isError": False
                                    }
                                }
                            except Exception as chart_error:
                                response = {
                                    "jsonrpc": "2.0",
                                    "id": request_id,
                                    "result": {
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": f"❌ **HTML报告生成失败**: {str(chart_error)}"
                                            }
                                        ],
                                        "isError": True
                                    }
                                }
                        else:  # analyze_flv
                            # 生成详细的分析报告
                            report_lines = []
                            report_lines.append("=" * 60)
                            report_lines.append(f"FLV音视频时间戳分析报告: {analysis_data['filename']}")
                            report_lines.append("=" * 60)
                            
                            # 元数据信息
                            if analysis_data['metadata']:
                                report_lines.append("\n📋 **元数据信息**:")
                                for key, value in analysis_data['metadata'].items():
                                    report_lines.append(f"  - {key}: {value}")
                            
                            report_lines.append(f"\n📊 **基本统计**:")
                            report_lines.append(f"  - 总标签数: {analysis_data['total_tags']}")
                            
                            # 音频分析结果
                            if analysis_data['audio']['timestamps']:
                                audio_stats = analysis_data['audio']['stats']
                                audio_duration = max(t['timestamp'] for t in analysis_data['audio']['timestamps']) - min(t['timestamp'] for t in analysis_data['audio']['timestamps'])
                                report_lines.append(f"\n🔊 **音频分析**:")
                                report_lines.append(f"  - 音频帧数: {len(analysis_data['audio']['timestamps'])}")
                                report_lines.append(f"  - 音频时长: {audio_duration}ms")
                                if audio_stats:
                                    report_lines.append(f"  - 平均间隔: {audio_stats['avg']:.2f}ms")
                                    report_lines.append(f"  - 最大间隔: {audio_stats['max']}ms")  
                                    report_lines.append(f"  - 最小间隔: {audio_stats['min']}ms")
                                    
                                    # 音频异常检测
                                    if audio_stats.get('anomalies'):
                                        report_lines.append(f"  - ⚠️ 检测到 {len(audio_stats['anomalies'])} 个音频异常:")
                                        for anom in audio_stats['anomalies'][:5]:  # 只显示前5个
                                            report_lines.append(f"    * {anom['type']} at {anom['position']}ms (值: {anom['value']}ms)")
                                        if len(audio_stats['anomalies']) > 5:
                                            report_lines.append(f"    * ... 还有 {len(audio_stats['anomalies']) - 5} 个异常")
                                    else:
                                        report_lines.append("  - ✅ 未检测到音频异常")
                            else:
                                report_lines.append(f"\n🔊 **音频分析**: 无音频数据")
                                
                            # 视频分析结果
                            if analysis_data['video']['timestamps']:
                                video_stats = analysis_data['video']['stats']
                                video_duration = max(t['timestamp'] for t in analysis_data['video']['timestamps']) - min(t['timestamp'] for t in analysis_data['video']['timestamps'])
                                report_lines.append(f"\n🎥 **视频分析**:")
                                report_lines.append(f"  - 视频帧数: {len(analysis_data['video']['timestamps'])}")
                                report_lines.append(f"  - 视频时长: {video_duration}ms")
                                if video_stats:
                                    report_lines.append(f"  - 平均间隔: {video_stats['avg']:.2f}ms")
                                    report_lines.append(f"  - 最大间隔: {video_stats['max']}ms")
                                    report_lines.append(f"  - 最小间隔: {video_stats['min']}ms")
                                    
                                    # 视频异常检测
                                    if video_stats.get('anomalies'):
                                        report_lines.append(f"  - ⚠️ 检测到 {len(video_stats['anomalies'])} 个视频异常:")
                                        for anom in video_stats['anomalies'][:5]:  # 只显示前5个
                                            report_lines.append(f"    * {anom['type']} at {anom['position']}ms (值: {anom['value']}ms)")
                                        if len(video_stats['anomalies']) > 5:
                                            report_lines.append(f"    * ... 还有 {len(video_stats['anomalies']) - 5} 个异常")
                                    else:
                                        report_lines.append("  - ✅ 未检测到视频异常")
                            else:
                                report_lines.append(f"\n🎥 **视频分析**: 无视频数据")
                                
                            # 生成HTML可视化报告
                            try:
                                base_name = os.path.splitext(os.path.basename(file_path))[0]
                                html_output = f"{base_name}_timestamp_analysis.html"
                                create_charts(analysis_data, html_output)
                                report_lines.append(f"\n📈 **可视化报告**: {os.path.abspath(html_output)}")
                            except Exception as chart_error:
                                report_lines.append(f"\n📈 **可视化报告**: 生成失败 - {str(chart_error)}")
                            
                            report_lines.append("=" * 60)
                            
                            # 构造响应内容
                            content_items = [
                                {
                                    "type": "text",
                                    "text": "\n".join(report_lines)
                                }
                            ]
                            
                            # 添加JSON数据作为额外内容
                            json_summary = {
                                "filename": analysis_data['filename'],
                                "total_tags": analysis_data['total_tags'],
                                "metadata": analysis_data['metadata'],
                                "audio": {
                                    "frame_count": len(analysis_data['audio']['timestamps']),
                                    "duration_ms": max(t['timestamp'] for t in analysis_data['audio']['timestamps']) - min(t['timestamp'] for t in analysis_data['audio']['timestamps']) if analysis_data['audio']['timestamps'] else 0,
                                    "stats": analysis_data['audio']['stats']
                                },
                                "video": {
                                    "frame_count": len(analysis_data['video']['timestamps']),
                                    "duration_ms": max(t['timestamp'] for t in analysis_data['video']['timestamps']) - min(t['timestamp'] for t in analysis_data['video']['timestamps']) if analysis_data['video']['timestamps'] else 0,
                                    "stats": analysis_data['video']['stats']
                                }
                            }
                            
                            content_items.append({
                                "type": "text",
                                "text": f"\n**JSON数据摘要**:\n```json\n{json_lib.dumps(json_summary, indent=2, ensure_ascii=False)}\n```"
                            })
                            
                            response = {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "result": {
                                    "content": content_items,
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