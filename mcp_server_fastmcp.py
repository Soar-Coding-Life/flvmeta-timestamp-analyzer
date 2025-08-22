#!/usr/bin/env python3
"""
使用 FastMCP 重构的 FLV 时间戳分析服务器
更简洁的代码结构和更好的类型支持
"""

import os
import json
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 导入原有的分析器功能
from flvmeta_timestamp_analyzer.analyzer import parse_flv_with_flvmeta, analyze_timestamps, create_charts


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
    """
    分析FLV文件的时间戳信息，提供详细报告和异常检测
    
    Args:
        inputs: 包含file_path的输入参数
        
    Returns:
        详细的分析报告文本
    """
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
            
        # 尝试生成HTML可视化报告
        try:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            html_output = f"{base_name}_timestamp_analysis.html"
            create_charts(analysis_data, html_output)
            report_lines.append(f"\n📈 **可视化报告**: {os.path.abspath(html_output)}")
        except Exception as chart_error:
            report_lines.append(f"\n📈 **可视化报告**: 生成失败 - {str(chart_error)}")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
        
    except Exception as e:
        return f"❌ **FLV分析失败**: {str(e)}"


@mcp.tool()
def analyze_flv_json(inputs: AnalyzeFlvJsonInput) -> str:
    """
    分析FLV文件并返回完整的JSON数据结构，包含所有时间戳信息
    
    Args:
        inputs: 包含file_path的输入参数
        
    Returns:
        完整的JSON数据结构
    """
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
    """
    分析FLV文件并生成HTML可视化报告
    
    Args:
        inputs: 包含file_path和可选output_path的输入参数
        
    Returns:
        HTML报告生成结果
    """
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


if __name__ == "__main__":
    # 运行服务器
    mcp.run(transport="stdio")