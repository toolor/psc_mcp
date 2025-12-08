# PSC MCP 服务器

基于FastMCP的普通话考试报名查询工具。

## 功能

- 获取省份列表
- 查询开放报名的测试站点
- 查询即将开放报名的测试站点

## 安装

推荐使用uv管理依赖：
```bash
uv sync
```

或者使用pip安装依赖：
```bash
pip install fastmcp requests
```

## 使用方法

启动服务器：
```bash
uv run python src/psc.py
```

或者使用Docker：
```bash
docker build -t psc-mpc .
docker run -p 8000:8000 psc-mpc
```

## 提供的工具

- `get_provinces()`: 获取省份列表
- `get_open_stations(province_id)`: 获取指定省份的开放报名测试站点
- `get_next_stations(province_id)`: 获取指定省份的即将开考测试站点

## 使用示例

1. 获取省份列表：`get_provinces()`
2. 查询宁夏开放报名的测试站点：`get_open_stations("ningxia")`
3. 查询宁夏即将开考的测试站点：`get_next_stations("ningxia")`