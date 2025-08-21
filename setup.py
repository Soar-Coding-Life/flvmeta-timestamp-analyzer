from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 直接定义依赖而不是从文件读取
requirements = [
    "pyecharts>=2.0.0",
]

# 可选依赖
extras_require = {
    'fastmcp': ['fastmcp', 'mcp', 'pydantic'],
}

setup(
    name="flvmeta-timestamp-analyzer",
    version="1.0.10",
    author="CoderWGB",
    author_email="864562082@qq.com",
    description="FLV音视频时间戳分析工具，支持MCP协议和FastMCP框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Soar-Coding-Life/flvmeta-timestamp-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux", 
        "Operating System :: MacOS",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "flv-timestamp-analyzer=flvmeta_timestamp_analyzer:cli_main",
            "flv-mcp-server=flvmeta_timestamp_analyzer.mcp_fastmcp:main",
        ],
    },
    package_data={
        "flvmeta_timestamp_analyzer": ["*.json"],
    },
    include_package_data=True,
    license="MIT",
)