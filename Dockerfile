# 使用官方Python运行时作为基础镜像
FROM python:3.14-slim

# 安装uv
RUN pip install uv

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN uv sync

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uv", "run", "python", "src/psc.py"]