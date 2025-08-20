# FLV时间戳分析工具发布和使用详细教程

## 发布准备

### 1. 注册账户

#### PyPI账户
1. 访问 https://pypi.org/ 并注册一个账户
2. 访问 https://test.pypi.org/ 并注册一个测试账户（用于测试发布）

#### npm账户
1. 访问 https://www.npmjs.com/ 并注册一个账户

### 2. 安装发布工具

```bash
# 安装Python打包工具
pip install setuptools wheel twine

# 确保已安装Node.js和npm（用于npm发布）
# 从 https://nodejs.org/ 下载并安装Node.js
```

### 3. 配置认证信息

#### PyPI认证
创建或编辑 `~/.pypirc` 文件:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = YOUR_PYPI_API_TOKEN

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = YOUR_TEST_PYPI_API_TOKEN
```

#### npm认证
```bash
npm login
# 输入你的npm用户名、密码和邮箱
```

## 发布步骤

### 1. 更新版本号

在发布之前，需要更新以下文件中的版本号:
1. `setup.py` 中的 `version` 字段
2. `package.json` 中的 `version` 字段
3. `mcp.config.json` 中的版本号（如果需要）

### 2. 构建和发布到PyPI

```bash
# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建Python包
python setup.py sdist bdist_wheel

# 首先发布到测试PyPI进行验证
twine upload --repository testpypi dist/*

# 如果测试成功，发布到正式PyPI
twine upload dist/*
```

### 3. 发布到npm

```bash
# 确保package.json中的版本号正确
# 然后发布
npm publish
```

## 安装和使用

### 方法一：通过pip安装（推荐）

#### 1. 安装
```bash
# 安装工具
pip install flvmeta-timestamp-analyzer
```

#### 2. 使用
```bash
# 命令行使用
flv-timestamp-analyzer input.flv output.html

# 作为MCP服务使用（需要支持MCP的AI客户端）
# 在AI客户端中配置MCP服务，服务名称为 "flv-timestamp-analyzer"
```

### 方法二：通过npx安装（无需预先安装）

#### 1. 使用
```bash
# 直接运行（会自动下载并执行）
npx flvmeta-timestamp-analyzer input.flv output.html

# 作为MCP服务使用
# 在AI客户端中配置MCP服务，服务名称为 "flv-timestamp-analyzer"
```

### 方法三：从源码安装

#### 1. 克隆或下载源码
```bash
git clone https://github.com/yourusername/flvmeta-timestamp-analyzer.git
cd flvmeta-timestamp-analyzer
```

#### 2. 安装依赖
```bash
# 安装Python依赖
pip install -r requirements.txt

# 如果需要使用npm命令
npm install
```

#### 3. 安装工具
```bash
# 本地安装Python包
pip install -e .

# 或者使用npm安装
npm install -g .
```

#### 4. 使用
```bash
# 命令行使用
flv-timestamp-analyzer input.flv output.html

# 直接运行Python脚本
python mcp_server.py input.flv output.html
```

## 在AI客户端中使用MCP服务

### 1. 配置MCP服务

大多数支持MCP的AI客户端会自动发现已安装的MCP服务。如果需要手动配置，请按照以下步骤操作：

1. 打开AI客户端的设置或配置页面
2. 找到MCP服务或插件配置部分
3. 添加一个新的MCP服务，使用以下配置：
   - 服务名称: `flv-timestamp-analyzer`
   - 命令: `python3`
   - 参数: `-u mcp_server.py`
   - 工作目录: 工具安装目录

### 2. 使用MCP服务

在AI客户端中，你可以通过以下方式使用该工具：
1. 上传一个FLV文件到AI客户端
2. 选择使用`flv-timestamp-analyzer`工具进行分析
3. 等待分析完成，查看结果

## 故障排除

### 1. 安装问题

如果遇到安装问题，请尝试以下解决方法：

```bash
# 升级pip
pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装
pip uninstall flvmeta-timestamp-analyzer
pip install flvmeta-timestamp-analyzer
```

### 2. 运行问题

如果工具无法运行，请检查以下几点：
1. 确保已安装所有依赖（特别是flvmeta）
2. 检查是否有权限问题
3. 查看日志文件（通常在当前目录下的`mcp_server.log`）

### 3. MCP服务问题

如果MCP服务无法启动，请检查：
1. 确保Python环境正确配置
2. 检查`.mcp.servers.json`配置文件是否正确
3. 查看AI客户端的日志信息

## 开发者说明

### 项目结构
```
flvmeta-timestamp-analyzer/
├── flv_timestamp_analyzer.py  # 核心分析功能
├── mcp_server.py             # MCP服务实现
├── setup.py                  # Python包配置
├── package.json              # npm包配置
├── mcp.config.json           # MCP模型配置
├── .mcp.servers.json         # MCP服务配置
├── requirements.txt          # Python依赖
└── README.md                 # 使用说明
```

### 自定义配置

你可以在`config.json`中自定义工具的行为：
```json
{
  "log_level": "info",
  "max_workers": 4,
  "request_timeout": 30
}
```

### 构建和测试

在发布之前，建议进行充分的测试：

```bash
# 运行单元测试（如果有的话）
python -m pytest

# 测试命令行功能
python mcp_server.py test.flv

# 测试MCP服务功能
python test_client.py
```

通过遵循这个详细的教程，即使是初学者也能成功发布和使用这个FLV时间戳分析工具。