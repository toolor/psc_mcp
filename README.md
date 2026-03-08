# PSC MCP 服务器

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![PyPI](https://img.shields.io/pypi/v/psc_mcp)

基于 FastMCP 框架开发的普通话水平测试（PSC）考试报名查询系统，提供全国各省份测试站点的报名信息查询服务。

## 目录

- [功能特性](#功能特性)
- [安装](#安装)
- [作为包使用](#作为包使用)
- [作为Web服务运行](#作为web服务运行)
  - [本地运行](#本地运行)
  - [Docker 部署](#docker-部署)
- [API 接口](#api-接口)
- [项目结构](#项目结构)
- [许可证](#许可证)

## 功能特性

- 🌍 **省份列表获取** - 获取支持的所有省份列表
- 📅 **报名信息查询** - 实时查询各省份开放报名的测试站点
- ⏱️ **即将开考查询** - 查看即将举行考试的测试站点信息
- 🚀 **高性能架构** - 基于 FastMCP 框架，提供高效的 API 服务
- 🐳 **容器化部署** - 支持 Docker 快速部署

## 安装

### 作为包安装

```bash
pip install psc_mcp
```

### 开发环境安装

推荐使用 uv 管理依赖：

```bash
uv sync
```

或者使用 pip 安装依赖：

```bash
pip install -r requirements.txt
```

## 作为包使用

安装后，您可以直接在 Python 代码中使用该包：

```python
from psc_mcp import get_provinces, get_open_stations, get_next_stations

# 获取省份列表
provinces = get_provinces()
print(provinces)

# 获取宁夏开放报名的测试站点
ningxia_stations = get_open_stations("ningxia")
print(ningxia_stations)

# 获取宁夏即将开考的测试站点
next_stations = get_next_stations("ningxia")
print(next_stations)
```

## 作为MCP服务运行

### 默认方式（stdio）

默认情况下，服务以 stdio 方式运行，适合与支持 MCP 协议的客户端集成：

```bash
psc_mcp
```

### HTTP 服务模式

支持多种 HTTP 传输方式：

**标准 HTTP 模式**：
```bash
psc_mcp --transport http --host 127.0.0.1 --port 8000 --path /mcp
```

**SSE 模式**（Server-Sent Events）：
```bash
psc_mcp --transport sse --host 127.0.0.1 --port 8000 --path /mcp
```

**Streamable HTTP 模式**：
```bash
psc_mcp --transport streamable-http --port 8000
```

服务器将在 `http://localhost:8000/mcp` 启动。

### 开发环境安装

推荐使用 uv 管理依赖：

```bash
uv sync
```

或者使用 pip 安装依赖：

```bash
pip install -r requirements.txt
```

### Docker 部署

构建 Docker 镜像：

```bash
docker build -t psc_mcp .
```

运行容器：

```bash
docker run -p 8000:8000 psc_mcp
```

## API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/provinces` | 获取省份列表 |
| GET | `/open-stations/{province_id}` | 获取指定省份开放报名的测试站点 |
| GET | `/next-stations/{province_id}` | 获取指定省份即将开考的测试站点 |

### 示例请求

1. 获取省份列表：
   ```bash
   curl http://localhost:8000/provinces
   ```

2. 查询宁夏开放报名的测试站点：
   ```bash
   curl http://localhost:8000/open-stations/ningxia
   ```

3. 查询宁夏即将开考的测试站点：
   ```bash
   curl http://localhost:8000/next-stations/ningxia
   ```

## 项目结构

```
psc_mcp/
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   └── psc.py              # 主应用文件
├── Dockerfile              # Docker 配置文件
├── pyproject.toml          # 项目配置和依赖声明
├── README.md               # 项目说明文档
└── LICENSE                 # 许可证文件
```

## 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。