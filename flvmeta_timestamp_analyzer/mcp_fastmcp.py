#!/usr/bin/env python3
"""
独立的 FastMCP 服务器，包含在包内
"""

import os
import json
from typing import Optional

try:
    from fastmcp import FastMCP
    from pydantic import BaseModel, Field
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False

def create_fastmcp_server():
    """创建 FastMCP 服务器"""
    if not FASTMCP_AVAILABLE:
        raise ImportError("FastMCP 不可用，请安装: pip install fastmcp")
    
    # 导入分析器功能
    from .analyzer import parse_flv_with_flvmeta, analyze_timestamps, create_charts

    class AnalyzeFlvInput(BaseModel):
        """FLV 分析输入参数"""
        file_path: str = Field(description="FLV文件路径")

    class AnalyzeFlvJsonInput(BaseModel):
        """FLV JSON 分析输入参数"""
        file_path: str = Field(description="FLV文件路径")

    class GenerateFlvReportInput(BaseModel):
        """生成 FLV 报告输入参数"""
        file_path: str = Field(description="FLV文件路径")
        output_path: Optional[str] = Field(default=None, description="HTML输出文件路径（可选）")

    # 创建 FastMCP 实例
    mcp = FastMCP("FLV Timestamp Analyzer")

    @mcp.tool()
    def analyze_flv(inputs: AnalyzeFlvInput) -> str:
        """分析FLV文件的时间戳信息，提供详细报告和异常检测"""
        try:
            file_path = inputs.file_path
            
            # 验证文件存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
                
            # 解析FLV文件
            json_data = parse_flv_with_flvmeta(file_path)
            analysis_data = analyze_timestamps(json_data, file_path)
            
            # 生成详细的分析报告
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append(f"FLV音视频时间戳分析报告: {analysis_data['filename']}")
            report_lines.append("=" * 60)
            
            # 基本统计
            report_lines.append(f"\n📊 **基本统计**:")
            report_lines.append(f"  - 总标签数: {analysis_data['total_tags']}")
            
            return "\n".join(report_lines)
            
        except Exception as e:
            return f"❌ **FLV分析失败**: {str(e)}"

    @mcp.tool()
    def analyze_flv_json(inputs: AnalyzeFlvJsonInput) -> str:
        """分析FLV文件并返回完整的JSON数据结构，包含所有时间戳信息"""
        try:
            file_path = inputs.file_path
            
            # 验证文件存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
                
            # 解析FLV文件
            json_data = parse_flv_with_flvmeta(file_path)
            analysis_data = analyze_timestamps(json_data, file_path)
            
            # 返回格式化的JSON数据
            return f"**完整FLV分析数据 - {analysis_data['filename']}**\n\n```json\n{json.dumps(analysis_data, indent=2, ensure_ascii=False)}\n```"
            
        except Exception as e:
            return f"❌ **JSON分析失败**: {str(e)}"

    @mcp.tool()
    def generate_flv_report(inputs: GenerateFlvReportInput) -> str:
        """分析FLV文件并生成HTML可视化报告"""
        try:
            file_path = inputs.file_path
            output_path = inputs.output_path
            
            # 验证文件存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
                
            # 解析FLV文件
            json_data = parse_flv_with_flvmeta(file_path)
            analysis_data = analyze_timestamps(json_data, file_path)
            
            # 确定输出路径
            if not output_path:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = f"{base_name}_timestamp_analysis.html"
            
            # 生成HTML报告
            create_charts(analysis_data, output_path)
            abs_path = os.path.abspath(output_path)
            file_size = os.path.getsize(abs_path) / 1024
            
            return f"""📈 **HTML可视化报告已生成**

**文件位置**: {abs_path}
**文件大小**: {file_size:.1f} KB

报告包含:
- 音视频时间戳增量变化曲线
- 异常点标记和分析
- 交互式图表（支持缩放和拖拽）
- 详细统计信息

可以在浏览器中打开查看完整的可视化分析结果。"""
            
        except Exception as e:
            return f"❌ **HTML报告生成失败**: {str(e)}"

    return mcp

def main():
    """MCP 服务器主入口"""
    try:
        if FASTMCP_AVAILABLE:
            # 使用 FastMCP
            mcp = create_fastmcp_server()
            mcp.run(transport="stdio")
        else:
            # 回退到基本版本
            import sys
            
            def handle_request(request):
                method = request.get("method")
                request_id = request.get("id")
                
                if method == "initialize":
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {"listChanged": False}},
                            "serverInfo": {"name": "flv-timestamp-analyzer", "version": "1.0.9"}
                        }
                    }
                elif method == "tools/list":
                    return {
                        "jsonrpc": "2.0", 
                        "id": request_id,
                        "result": {
                            "tools": [
                                {
                                    "name": "analyze_flv_basic",
                                    "description": "基础FLV分析（需要安装 fastmcp 以获得完整功能）",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "file_path": {"type": "string", "description": "FLV文件路径"}
                                        },
                                        "required": ["file_path"]
                                    }
                                }
                            ]
                        }
                    }
                elif method == "tools/call":
                    tool_name = request.get("params", {}).get("name")
                    if tool_name == "analyze_flv_basic":
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [{"type": "text", "text": "⚠️ 基础模式：请安装完整版本 `pip install flvmeta-timestamp-analyzer[fastmcp]` 以获得完整的FLV分析功能"}],
                                "isError": False
                            }
                        }
                    else:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                        }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Method not found: {method}"}
                    }
            
            # 基本 MCP 服务器循环
            for line in sys.stdin:
                if line.strip():
                    try:
                        request = json.loads(line.strip())
                        response = handle_request(request)
                        print(json.dumps(response), flush=True)
                    except:
                        pass
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import sys
        print(f"MCP 服务器错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()