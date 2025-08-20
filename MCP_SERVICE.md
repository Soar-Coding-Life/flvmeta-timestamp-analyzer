# FLV Timestamp Analyzer MCP Service

将FLV音视频时间戳分析工具封装为MCP服务，供AI客户端调用。

## 安装依赖

1. 安装Python依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 安装flvmeta工具：
   - macOS: `brew install flvmeta`
   - Linux: `sudo apt-get install flvmeta` 或从源码编译
   - Windows: 下载 https://github.com/noirotm/flvmeta/releases
   - 源码: https://github.com/noirotm/flvmeta

## MCP配置

项目包含MCP配置文件 `mcp.config.json`，定义了模型的元数据和能力：

```json
{
  "models": [
    {
      "name": "flv-timestamp-analyzer",
      "description": "FLV音视频时间戳分析工具",
      "capabilities": {
        "can_stream": false,
        "can_accept_audio_input": false,
        "can_accept_image_input": false,
        "can_accept_text_input": false,
        "can_accept_file_input": true
      },
      "metadata": {
        "author": "Your Name",
        "version": "1.0.0",
        "license": "MIT"
      }
    }
  ]
}
```

## MCP服务配置

项目包含MCP服务配置文件 `mcp_servers.config.json`，用于配置如何启动服务：

```json
{
  "mcpServers": {
    "flv-timestamp-analyzer": {
      "command": "python3",
      "args": ["-u", "/Users/wangguibin/Desktop/flvmeta-timestamp-analyzer/mcp_server.py"],
      "cwd": "/Users/wangguibin/Desktop/flvmeta-timestamp-analyzer"
    }
  }
}
```

配置说明：
- `command`: 启动服务的命令
- `args`: 命令行参数，`-u`参数确保输出不被缓冲
- `cwd`: 服务运行的工作目录

## 使用方法

AI客户端可以通过stdio与服务通信，遵循MCP协议：

1. 客户端发送握手消息
2. 服务端回复握手响应，包含模型信息
3. 客户端发送分析请求
4. 服务端返回分析结果

### 请求格式 (JSON)
```json
{
  "file_path": "/path/to/your/file.flv"
}
```

### 响应格式 (JSON)
成功响应：
```json
{
  "status": "success",
  "data": {
    "filename": "example.flv",
    "metadata": {...},
    "audio": {...},
    "video": {...},
    "total_tags": 1234
  }
}
```

错误响应：
```json
{
  "error": "错误信息",
  "details": "详细错误信息"
}
```

## 调试方法

### 使用调试客户端

项目包含一个调试客户端，可以用于测试和调试MCP服务：

```bash
# 交互式调试模式
python3 debug_client.py

# 单次测试
python3 debug_client.py /path/to/your/file.flv
```

### 日志查看

MCP服务会生成日志文件 `mcp_server.log`，可以通过以下命令查看：

```bash
# 查看实时日志
tail -f mcp_server.log

# 查看错误日志
grep ERROR mcp_server.log

# 查看警告日志
grep WARNING mcp_server.log
```

### 配置文件

服务会读取 `config.json` 配置文件（如果存在）：

```json
{
  "log_level": "debug",
  "max_workers": 4,
  "request_timeout": 30
}
```